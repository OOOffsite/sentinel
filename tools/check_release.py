"""Check local release artifacts without installation, network access, or publishing."""
from __future__ import annotations

import argparse
import base64
import configparser
import csv
from email.parser import BytesParser
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "atlas_sentinel"
COMMANDS = {
    "sentinel-openrig": "atlas_sentinel.tools.sentinel:main",
    "sentinel-project": "atlas_sentinel.tools.bootstrap:main",
}
PRIVATE_PARTS = {"AGENTS.md", "CLAUDE.md", "validation.txt", ".env", ".git", ".agents", ".uharness", ".claude-flow", ".venv", "runtime", "__pycache__", "checkpoint.json"}
PRIVATE_CONTENT = re.compile(
    rb"(?:/(?:Users|Volumes)/[^/\s]+/|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    rb"pypi-" + rb"AgEIcHlwaS5vcmc)"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def safe_name(name: str) -> None:
    path = PurePosixPath(name)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in name,
            f"Unsafe archive member: {name}")
    require(not PRIVATE_PARTS.intersection(path.parts), f"Private/local file included: {name}")
    require(not re.search(r"\.(?:sqlite(?:3)?(?:-wal|-shm)?|db|pyc|pyo)$", name),
            f"Runtime/generated file included: {name}")


def inspect_files(files: dict[str, bytes], label: str) -> None:
    for name, content in files.items():
        safe_name(name)
        require(not PRIVATE_CONTENT.search(content), f"Local path or credential marker in {label}: {name}")


def inspect_metadata(data: bytes, project: dict, label: str) -> None:
    metadata = BytesParser().parsebytes(data)
    require(metadata["Name"] == project["name"], f"{label}: package name mismatch")
    require(metadata["Version"] == project["version"], f"{label}: version mismatch")
    require(metadata["Requires-Python"] == project["requires-python"], f"{label}: Python requirement mismatch")
    require(not metadata.get_all("Requires-Dist"), f"{label}: unexpected runtime dependencies")
    require(metadata["Description-Content-Type"] == "text/markdown", f"{label}: Markdown content type missing")
    require(metadata["License-Expression"] == project.get("license"), f"{label}: license expression mismatch")
    require("LICENSE" in metadata.get_all("License-File", []), f"{label}: license file metadata missing")
    urls = dict(value.split(", ", 1) for value in metadata.get_all("Project-URL", []))
    require(urls == project["urls"], f"{label}: project URL mismatch")
    description = metadata.get_payload()
    require("Sentinel" in description and len(description) > 100, f"{label}: description missing")
    require(not re.search(r"\]\((?!https?://|mailto:|#)[^)]+\)", description),
            f"{label}: PyPI README contains unresolved relative links")


def check(directory: Path, require_publishable: bool) -> dict:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    manifest = json.loads((ROOT / "module.json").read_text())
    require(project["version"] == manifest["version"], "Source package/module versions differ")
    require(manifest["contract_version"] == "1.1.0", "Observation contract unexpectedly changed")
    wheels = sorted(directory.glob("*.whl"))
    sources = sorted(directory.glob("*.tar.gz"))
    require(len(wheels) == len(sources) == 1, "Use a clean artifact directory with exactly one wheel and one sdist")
    expected = f"sentinel_openrig-{project['version']}"
    require(wheels[0].name == f"{expected}-py3-none-any.whl", "Unexpected wheel name/tag")
    require(sources[0].name == f"{expected}.tar.gz", "Unexpected sdist name")

    with zipfile.ZipFile(wheels[0]) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate wheel members")
        require(all((item.external_attr >> 16) & 0o170000 != 0o120000 for item in archive.infolist()),
                "Wheel contains a symlink")
        wheel = {name: archive.read(name) for name in names if not name.endswith("/")}
    with tarfile.open(sources[0], "r:gz") as archive:
        members = archive.getmembers()
        require(all(member.isfile() or member.isdir() for member in members), "Sdist contains a link or special file")
        require(len(members) == len({member.name for member in members}), "Duplicate sdist members")
        require(all(PurePosixPath(member.name).parts[0] == expected for member in members), "Unexpected sdist root")
        source = {str(PurePosixPath(member.name).relative_to(expected)): archive.extractfile(member).read()
                  for member in members if member.isfile()}
    inspect_files(wheel, "wheel")
    inspect_files(source, "sdist")
    info = f"{expected}.dist-info"
    require(f"{info}/METADATA" in wheel and "PKG-INFO" in source, "Distribution metadata missing")
    inspect_metadata(wheel[f"{info}/METADATA"], project, "wheel")
    inspect_metadata(source["PKG-INFO"], project, "sdist")
    record_path = f"{info}/RECORD"
    records = list(csv.reader(io.StringIO(wheel[record_path].decode())))
    require(len(records) == len(wheel) and {row[0] for row in records} == set(wheel), "Wheel RECORD inventory differs")
    for name, digest, size in records:
        if name == record_path:
            require(not digest and not size, "RECORD must omit its own hash and size")
            continue
        expected_digest = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(wheel[name]).digest()).rstrip(b"=").decode()
        require(digest == expected_digest and size == str(len(wheel[name])), f"Wheel RECORD integrity mismatch: {name}")

    entrypoints = configparser.ConfigParser()
    entrypoints.read_string(wheel[f"{info}/entry_points.txt"].decode())
    require(dict(entrypoints["console_scripts"]) == COMMANDS, "Console entry points differ")
    must_ship = ["__init__.py", "module.json", "README.pypi.md", "CHANGELOG.md",
                 "web/live.html", "web/simulation.html", "tools/sentinel.py", "tools/bootstrap.py",
                 "tools/project_skill.py", "plugin/skills/sentinel-monitor/SKILL.md"]
    must_ship += [str(path.relative_to(ROOT)) for path in (ROOT / "contracts").iterdir() if path.is_file()]
    for relative in must_ship:
        package_path = f"{PACKAGE}/{relative}"
        require(package_path in wheel and relative in source, f"Required file missing: {relative}")
        require(wheel[package_path] == source[relative] == (ROOT / relative).read_bytes(),
                f"Source/wheel/sdist differ: {relative}")
    require(wheel[f"{info}/licenses/LICENSE"] == source["LICENSE"] == (ROOT / "LICENSE").read_bytes(),
            "License content differs")

    # Extract only a checked wheel to a disposable directory and import from it.
    # No pip install, daemon startup, agent launch, or caller environment changes.
    with tempfile.TemporaryDirectory(prefix="sentinel-wheel-check-") as temporary:
        location = Path(temporary)
        for name, content in wheel.items():
            output = location / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        for target in COMMANDS.values():
            module, function = target.split(":")
            program = (
                "import importlib, pathlib, sys; "
                "root=pathlib.Path(sys.argv.pop(1)); sys.path.insert(0,str(root)); "
                f"module=importlib.import_module({module!r}); "
                "assert pathlib.Path(module.__file__).is_relative_to(root); "
                f"module.{function}()"
            )
            result = subprocess.run([sys.executable, "-I", "-c", program, str(location), "--help"],
                                    cwd=location, text=True, capture_output=True, timeout=20)
            require(result.returncode == 0 and "usage:" in result.stdout,
                    f"Packaged CLI help failed: {module}")

    if require_publishable:
        require(project.get("license") == "Apache-2.0", "Approved release license missing")
        require(project["urls"].get("Repository") == "https://github.com/OOOffsite/sentinel", "Approved repository URL missing")
        require((ROOT / "LICENSE").stat().st_size > 1000, "Full license text missing")
        repository = os.environ.get("GITHUB_REPOSITORY")
        require(not repository or repository.casefold() == "oooffsite/sentinel", "Workflow repository differs from release owner")

    return {
        "version": project["version"],
        "artifacts": [{"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "bytes": path.stat().st_size} for path in [wheels[0], sources[0]]],
        "checks": ["source/version consistency", "metadata and absolute PyPI links", "license", "wheel RECORD integrity",
                   "archive paths and local-state exclusions", "required package resources", "packaged CLI --help"],
        "publication": "not performed",
        "limits": ["Not a comprehensive secret or dependency audit", "Registry name ownership not checked",
                   "Remote workflow and Trusted Publisher setup not checked", "Live exporter interoperability not checked"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Clean directory containing one wheel and one sdist")
    parser.add_argument("--require-publishable", action="store_true", help="Also require approved license/repository metadata")
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.directory, args.require_publishable), indent=2))
    except (ValueError, OSError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile, tarfile.TarError) as error:
        parser.exit(1, f"Release check failed: {error}\n")


if __name__ == "__main__":
    main()
