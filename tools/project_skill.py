#!/usr/bin/env python3
"""Explicitly project a shared skill into generated project AgentSpecs; no daemon changes."""
import argparse,json,shutil,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rig-dir',type=pathlib.Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args();files=sorted((a.rig_dir/'agents').glob('*/agent.yaml'));assert files,'No generated project AgentSpecs found';plans=[]
for f in files:
 d=json.loads(f.read_text());assert d['version']=='1.0';skills=d.setdefault('resources',{}).setdefault('skills',[]);uses=d['profiles']['default']['uses'].setdefault('skills',[]);target=f.parent/'skills'/'sentinel-monitor';src=ROOT/'plugin'/'skills'/'sentinel-monitor';desired={'id':'sentinel-monitor','path':'skills/sentinel-monitor'}
 if any(x.get('id')=='sentinel-monitor' and x!=desired for x in skills): raise SystemExit('Conflicting resource: '+str(f))
 if target.exists() and (not (target/'SKILL.md').is_file() or (target/'SKILL.md').read_bytes()!=(src/'SKILL.md').read_bytes()): raise SystemExit('Conflicting existing skill: '+str(target))
 if desired not in skills:skills.append(desired)
 if 'sentinel-monitor' not in uses:uses.append('sentinel-monitor')
 plans.append((f,d,target,src))
print(json.dumps({'agent_specs':len(plans),'apply':a.apply,'starts_agents':False,'installs_hooks':False},indent=2))
if a.apply:
 for f,d,target,src in plans:
  if not target.exists():shutil.copytree(src,target)
  tmp=f.with_suffix('.yaml.sentinel-new');
  with tmp.open('x') as out:json.dump(d,out,indent=2);out.write('\n')
  tmp.replace(f)
