#!/usr/bin/env python3
"""Extract a static marketing preview from Sentinel's existing application UI.

Regeneration runs the original JavaScript reducer with Node, and compares its
output to an independent deterministic Python projection. --check needs only
Python and verifies the complete generated asset against current source files.
No application is launched, and no network or runtime state is accessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site/assets/product-preview-data.js"
MOMENTS = (45000, 90000, 150000)
STATES = ("idle", "planning", "coding", "review", "testing", "syncing", "blocked", "offline", "unknown")
TEAMS = [
    {"id": "foundation", "name": "Foundation", "color": "#47c5f4", "lead": "Codex"},
    {"id": "intelligence", "name": "Intelligence", "color": "#ab91ff", "lead": "Claude Code"},
    {"id": "markets", "name": "Markets", "color": "#49e7ad", "lead": "Codex"},
    {"id": "assurance", "name": "Assurance", "color": "#ff9b77", "lead": "Claude Code"},
]


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def between(source: str, start: str, end: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Source renderer boundary changed: {start!r}")
    return source.split(start, 1)[1].split(end, 1)[0]


def function(source: str, name: str, next_name: str) -> str:
    start = f"function {name}("
    return start + between(source, start, f"function {next_name}(").rstrip()


def kind(event: dict) -> str:
    return event["type"][6:-3]


def project(data: dict, at: int) -> dict:
    """Equivalent projection of the original blank/apply/advance reducer."""
    scenario = data["scenarios"][0]
    agents = {f"{r['team']}.{r['seat']}": {"state": "unknown", "mission": None,
              "heartbeat": None, "tx": 0, "rx": 0, "last": None, "lastPulse": None}
              for r in data["roster"]}
    tasks = {task["id"]: "queued" for task in data["backlog"]}
    incidents, sent, builds, events = {}, [], [], []
    cursor = 0
    for event in scenario["events"]:
        if event["atlasoffset"] > at:
            break
        d, k = event["data"], kind(event)
        agent = agents.get(d.get("agent"))
        if agent is not None and k != "agent.heartbeat":
            agent["last"], agent["lastPulse"] = event, event["atlasoffset"]
        if k == "agent.state":
            agent["state"] = d["state"]
            if d.get("mission") is not None:
                agent["mission"] = d["mission"]
        elif k == "agent.heartbeat":
            agent["heartbeat"] = event["atlasoffset"]
        elif k == "message.sent":
            agent["tx"] += 1
            sent.append(event)
        elif k == "message.delivered":
            agents[d["target"]]["rx"] += 1
        elif k == "task.transition":
            tasks[d["mission"]] = d["state"]
        elif k == "build.completed":
            builds.append(event)
        elif k == "incident.opened":
            incidents[d["incident_id"]] = event
        elif k == "incident.resolved":
            incidents.pop(d["incident_id"], None)
        elif k == "coverage.gap":
            for item in agents.values():
                item["state"] = "unknown"
        events.append(event)
        cursor = event["atlasseq"]
    counts = {state: sum(a["state"] == state for a in agents.values()) for state in STATES}
    return {"at": at, "agents": list(map(list, agents.items())), "incidents": list(map(list, incidents.items())),
            "sent": [e for e in sent if at - e["atlasoffset"] <= 2200],
            "events": [e for e in events if kind(e) != "agent.heartbeat"][-5:][::-1],
            "cursor": cursor, "summary": {"counts": counts,
            "accepted": sum(x == "accepted" for x in tasks.values()), "builds": len(builds),
            "passed": sum(e["data"]["result"] == "pass" for e in builds),
            "busy": len(agents) - sum(counts[k] for k in ("idle", "offline", "unknown", "blocked"))}}


def generate(check: bool) -> str:
    simulation = (ROOT / "web/simulation.html").read_text()
    observed = (ROOT / "web/live.html").read_text()
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", simulation, re.S)
    data, source = json.loads(scripts[0]), scripts[1]
    live = re.search(r"<script>(.*?)</script>", observed, re.S).group(1)
    scenario = data["scenarios"][0]
    assert len(data["roster"]) == 128 and len(TEAMS) == 4
    assert scenario["duration_ms"] >= max(MOMENTS)
    assert all(e["atlasorigin"] == "simulated" for e in scenario["events"])
    reducer = "\n".join(function(source, a, b) for a, b in
                        (("blank", "apply"), ("apply", "advance"), ("advance", "at"), ("at", "seek")))
    original_draw = function(source, "draw", "desc")
    original_observed_draw = function(live, "draw", "pull").removesuffix("async").rstrip()
    parts = {name: function(source, name, following) for name, following in
             (("posLayout", "resize"), ("resize", "col"), ("col", "draw"), ("desc", "recent"))}
    snapshots = [project(data, at) for at in MOMENTS]
    if not check:
        node_program = """const data=JSON.parse(require('fs').readFileSync(0,'utf8'));
const {roster,backlog,scenarios}=data, scenario=scenarios[0];
const ids=roster.map(r=>r.team+'.'+r.seat),kind=e=>e.type.slice(6,-3);
""" + reducer + "\nconst states=" + json.dumps(STATES) + ";\n" + """
const result=[45000,90000,150000].map(time=>{const m=at(time);
const counts=Object.fromEntries(states.map(s=>[s,[...m.agents.values()].filter(a=>a.state===s).length]));
return {at:time,agents:[...m.agents],incidents:[...m.incidents],sent:m.sent.filter(e=>time-e.atlasoffset<=2200),
events:m.events.filter(e=>kind(e)!=='agent.heartbeat').slice(-5).reverse(),cursor:m.cursor,
summary:{counts,accepted:[...m.tasks.values()].filter(x=>x==='accepted').length,builds:m.builds.length,
passed:m.builds.filter(e=>e.data.result==='pass').length,busy:ids.length-counts.idle-counts.offline-counts.unknown-counts.blocked}}});
process.stdout.write(JSON.stringify(result));
"""
        actual = json.loads(subprocess.run(["node", "-e", node_program], input=json.dumps(data),
                            text=True, capture_output=True, check=True).stdout)
        if actual != snapshots:
            raise ValueError("Python projection differs from original JavaScript reducer")
    fixtures = []
    planned = [{"seat": f"{r['team']}.{r['seat']}", "team": r["team"], "runtime": r["runtime"]}
               for r in data["roster"]]
    for stale in (False, True):
        seats = []
        for t in TEAMS:
            for i, r in enumerate([r for r in planned if r["team"] == t["id"]][:4]):
                seats.append({"node_id": f"fixture-{t['id']}-{i+1}", "seat": r["seat"],
                              "runtime": r["runtime"], "presence": "unknown" if stale else "running",
                              "activity": "unknown" if stale else ("working" if i % 2 == 0 else "idle"),
                              "needs_input": "unknown", "sample_age_seconds": 120 if stale else 5})
        fixtures.append({"label": "Stale sample" if stale else "Fresh sample", "seats": seats,
                         "ttl_seconds": 90, "communication_available": False,
                         "historical_completeness": "unknown", "origin": "synthetic-preview-fixture"})
    payload = {"provenance": {"simulation_sha256": digest(simulation), "observed_sha256": digest(observed),
                "reducer_sha256": digest(reducer), "simulation_draw_sha256": digest(original_draw),
                "observed_draw_sha256": digest(original_observed_draw), "scenario": scenario["id"],
                "seed": scenario["seed"], "origin": "included-simulation", "moments_ms": MOMENTS,
                "renderer_adaptations": ["namespaced DOM callbacks", "canvas text label sizes increased to 12px",
                                         "no startup loop, streaming, or polling"]},
               "teams": TEAMS, "roster": data["roster"], "planned": planned,
               "missions": [{"id": t["id"], "title": t["title"]} for t in data["backlog"]],
               "scenario": {k: v for k, v in scenario.items() if k != "events"},
               "snapshots": snapshots, "observed": fixtures}
    draw = original_draw.replace("600 10px monospace", "600 12px monospace").replace("'10px monospace'", "'12px monospace'").replace("'9px monospace'", "'12px monospace'")
    # Exact source renderers run in an isolated adapter, with no original startup code.
    generated = "/* Generated by tools/build_product_preview.py; do not edit. */\n"
    generated += "window.SentinelProductPreviewData=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    generated += """window.SentinelProductPreviewRenderers={
simulation(canvas,onEdges){
 const data=window.SentinelProductPreviewData,roster=data.roster,teams=data.teams;
 const ctx=canvas.getContext('2d'),ids=roster.map(r=>r.team+'.'+r.seat),rmap=new Map(roster.map((r,i)=>[ids[i],r])),tm=new Map(teams.map(t=>[t.id,t]));
 const glyph={idle:'·',planning:'◇',coding:'▪',review:'◈',testing:'+',syncing:'↔',blocked:'!',offline:'×',unknown:'?'};
 const tone={idle:.28,planning:.65,coding:1,review:.85,testing:.9,syncing:.95,blocked:.65,offline:.15,unknown:.35};
 const kind=e=>e.type.slice(6,-3),$txt=(id,text)=>onEdges(text);
 let points=new Map(),model,time=45000,selected='foundation.lead',visible=new Set(ids),trace=false,layout='orbital',zoom=1,pan={x:0,y:0},motion=false,hover=null;
""" + "\n".join(parts[k] for k in ("posLayout", "resize", "col")) + "\n" + draw + "\n" + parts["desc"] + """
 return {render(snapshot,seat,team){model={...snapshot,agents:new Map(snapshot.agents),incidents:new Map(snapshot.incidents)};time=snapshot.at;selected=seat;visible=new Set(ids.filter(id=>team==='all'||id.startsWith(team+'.')));draw();},
 hit(event){const box=canvas.getBoundingClientRect();let chosen=null,dist=14;for(const [id,p] of points){const d=Math.hypot(p.x-(event.clientX-box.left),p.y-(event.clientY-box.top));if(d<dist&&visible.has(id)){chosen=id;dist=d;}}return chosen;},describe:desc};
},
observed(graph,onSelect){
 const data=window.SentinelProductPreviewData,roster=data.planned,colors=Object.fromEntries(data.teams.map(t=>[t.id,t.color])),ns='http://www.w3.org/2000/svg';
 let selected='',current=[];
 function el(tag,attrs,text){const node=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,v));if(text)node.textContent=text;return node;}
 function label(x,y,text,color,size=13){graph.append(el('text',{x,y,fill:color,'font-size':size,'text-anchor':'middle','font-family':'monospace'},text));}
 function show(){onSelect(selected);}
""" + original_observed_draw + """
 return {render(fixture,node){current=fixture.seats;selected=node;draw(current);}};
}};
"""
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated asset using Python only")
    args = parser.parse_args()
    expected = generate(args.check)
    if args.check:
        if not OUT.exists() or OUT.read_text() != expected:
            print("Product preview is stale; run python3 tools/build_product_preview.py", file=sys.stderr)
            return 1
        print("Product preview verified: source hashes, original renderers, and 3 frozen snapshots agree.")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(expected)
        print(f"Generated {OUT.relative_to(ROOT)} ({len(expected.encode()):,} bytes); original reducer agrees.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
