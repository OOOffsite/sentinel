"""Prepare a project-specific OpenRig topology and Sentinel configuration; never launch agents."""
import argparse, itertools, json, os, re, shutil, subprocess
from pathlib import Path
try:
    from . import sentinel as monitor
except ImportError:
    import sentinel as monitor
ROOT=Path(__file__).resolve().parents[1]
SLUG=re.compile(r'^[a-z][a-z0-9-]{0,62}$')
COMMIT='1beecce96befec880a93f60b11d83b44d7347620'
def require(ok,msg):
    if not ok: raise ValueError(msg)
def read(p): return json.loads(p.read_text())
def put(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f: json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def rel(base,value):
    p=Path(value); q=(base/p).resolve();require(not p.is_absolute() and q.is_relative_to(base) and q!=base and q.exists(),f'invalid project resource: {value}');return q
def git(repo,*args): return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def load(path):
    path=path.resolve(); base=path.parent; p=read(path)
    require(p['schema_version']=='1.0.0' and SLUG.fullmatch(p['project_id']) and 1<=len(p['title'])<=160,'invalid project')
    ts=p['teams']; teams={t['id']:t for t in ts};require(1<=len(ts)<=16 and len(teams)==len(ts) and all(SLUG.fullmatch(t['id']) and t['id']!='unmapped' for t in ts),'invalid teams')
    rows=read(rel(base,p['roster']));seats={r['team']+'.'+r['seat']:r for r in rows}; require(len(seats)==len(rows),'duplicate seat')
    monitor.roster_index([{'seat':sid,'team':r['team'],'runtime':r['runtime']} for sid,r in seats.items()]);require(all(r['team'] in teams and r['role'] and r['scope'] and r['cell'] for r in rows),'invalid seat declaration')
    pilots=[]
    for t in ts:
        ids=[t['id']+'.'+x for x in t['pilot_seats']];require(ids and len(set(ids))==len(ids) and t['id']+'.'+t['lead'] in ids and set(ids)<=seats.keys(),'invalid pilot or lead');pilots.extend(ids)
    pol=p['policy'];require(pol['approval_required'] is True and pol['require_clean_repo'] is True and pol['live_execution_allowed'] is False and pol['permission_policy']=='builtin:standard','unsafe or unsupported policy');require(len(pilots)==pol['initial_seats'] and len(pilots)<=len(rows)<=pol['max_seats']<=128,'invalid capacity')
    tasks=read(rel(base,p['missions']));seen=set();briefs=rel(base,p['briefs']);require(isinstance(tasks,list),'missions must be array')
    for m in tasks:
        mid=m['id'];require(re.fullmatch(r'[A-Za-z0-9_-]{1,64}',mid) and mid not in seen and set(m['depends_on'])<=seen,'missions must be unique and topologically ordered');require(m['owner'] in seats and m['reviewer'] in seats and m['owner']!=m['reviewer'] and m['status']=='proposed' and m['acceptance'] and m['write_paths'],'invalid mission');rel(briefs,mid+'.md');seen.add(mid)
    cfg=p['sentinel'];require(cfg['enabled'] is True and cfg['exporter_commit']==COMMIT and cfg['start'] in ('latest','retained') and type(cfg['default_port']) is int and 1024<=cfg['default_port']<=65535 and 10<=cfg['ttl_seconds']<=600 and 10<=cfg['poll_ms']<=60000 and 10<=cfg['seat_poll_ms']<=600000 and type(cfg['pseudonymize_seats']) is bool,'invalid Sentinel policy')
    rel(base,p['guidance']); [rel(base,d) for d in p['context_dirs']];
    for source in p['source_repositories']:
        if source['kind']=='snapshot': rel(base,source['path'])
        else: require(source['kind']=='git' and source['url'].startswith('https://'),'unsupported source declaration')
    return p,rows,seats,pilots,tasks

def prepare(args):
    manifest=args.project.resolve(); p,rows,seats,pilots,tasks=load(manifest); base=manifest.parent; repo=args.repo.resolve(); out=args.output.resolve()
    require(out!=repo and not out.is_relative_to(repo) and not repo.is_relative_to(out) and not out.exists(),'output must be new and separate from checkout'); require(git(repo,'rev-parse','--show-toplevel')==str(repo),'repo must be checkout root');require(not git(repo,'status','--porcelain'),'checkout is dirty')
    sha=git(repo,'rev-parse','HEAD'); selected=list(seats) if args.fleet=='full' else pilots; port=args.port or p['sentinel']['default_port'];require(1024<=port<=65535,'invalid port'); namespace=args.namespace; monitor.token(namespace);require(len(namespace)<=128,'namespace too long');require(len({sid.replace('.', '--') for sid in selected})==len(selected),'agent name collision')
    branches={sid:f"{p['project_id']}/{sid.replace('.','/')}" for sid in selected};existing=set(git(repo,'for-each-ref','--format=%(refname:short)','refs/heads').splitlines());require(not set(branches.values())&existing,'branches already exist')
    cfg=monitor.validate_config({'version':'1.1.0','project_id':p['project_id'],'title':p['title'],'namespace':namespace,'ttl_seconds':p['sentinel']['ttl_seconds'],'bindings':{},'roster':[{'seat':sid,'team':seats[sid]['team'],'runtime':seats[sid]['runtime']} for sid in seats]})
    plan={'project_id':p['project_id'],'repo':str(repo),'base_sha':sha,'output':str(out),'declared_seats':selected,'logical_seats':len(seats),'branches':branches,'port':port,'namespace':namespace,'launches_agents':False,'approval_required':True,'ready_candidates':[m['id'] for m in tasks if not m['depends_on'] and m['owner'] in selected and m['reviewer'] in selected]}
    print(json.dumps(plan,indent=2));
    if not args.apply:return
    os.umask(0o077);out.mkdir(parents=True);put(out/'preparation-plan.json',plan)
    prepared=[]
    try:
        # Copies only declared assets; the source package stays immutable.
        for d in p['context_dirs']+[p['briefs']]:
            src=rel(base,d); dest=out/'context'/d
            if not dest.exists():shutil.copytree(src,dest)
        shutil.copy2(rel(base,p['guidance']),out/'project-invariants.md');put(out/'mission-registry.json',tasks);put(out/'source-project-manifest.json',p);put(out/'sentinel'/'config.json',cfg);put(out/'sentinel'/'roster.json',cfg['roster'])
        rig={'version':'0.2','name':p['project_id'],'summary':p['summary'],'permission_policy':p['policy']['permission_policy'],'managed_blocks':{'claude-code':'CLAUDE.local.md'},'pods':[],'edges':[]}
        leads=[]
        for team in p['teams']:
            t=team['id']; lead=team['lead'];leads.append(t+'.'+lead);pod={'id':t,'label':team['label'],'members':[],'edges':[]}
            for sid in selected:
                r=seats[sid];
                if r['team']!=t:continue
                # Separator avoids collisions between team/seat names with hyphens.
                key=sid.replace('.','--');wt=out/'worktrees'/key;wt.parent.mkdir(exist_ok=True);git(repo,'worktree','add','-b',branches[sid],str(wt),sha);prepared.append(sid)
                ad=out/'agents'/key;skill=ad/'skills'/'sentinel-monitor';skill.mkdir(parents=True);text=(ROOT/'plugin/skills/sentinel-monitor/SKILL.md').read_text().replace('127.0.0.1:8766',f'127.0.0.1:{port}');(skill/'SKILL.md').write_text(text)
                spec={'name':key,'version':'1.0','description':r['role'],'defaults':{'runtime':r['runtime']},'profiles':{'default':{'uses':{'skills':['sentinel-monitor'],'guidance':[],'subagents':[],'plugins':[],'runtime_resources':[]}}},'resources':{'skills':[{'id':'sentinel-monitor','path':'skills/sentinel-monitor'}]},'startup':{'files':[{'path':'role.md','delivery_hint':'send_text','required':True}],'actions':[]}}
                put(ad/'agent.yaml',spec);(ad/'role.md').write_text(f"# {sid}\n\n{r['role']}\n\nScope hint: {r['scope']}. Read {out/'project-invariants.md'} and {out/'context'}. Mission registry: {out/'mission-registry.json'}. Base: {sha}.\nAwait explicit approved ready task. Use native OpenRig queue; only task path lease permits writes. Do not launch peers, change security settings, modify the shared checkout or access live execution. Sentinel read-only status: http://127.0.0.1:{port}/api/v1/status.\n")
                pod['members'].append({'id':r['seat'],'agent_ref':f'local:agents/{key}','profile':'default','runtime':r['runtime'],'cwd':str(wt)})
                if r['seat']!=lead:pod['edges'].append({'kind':'delegates_to','from':lead,'to':r['seat']})
            rig['pods'].append(pod)
        for a,b in itertools.combinations(leads,2):
            rig['edges'] += [{'kind':'collaborates_with','from':a,'to':b},{'kind':'collaborates_with','from':b,'to':a}]
        put(out/'rig.yaml',rig);put(out/'preparation-result.json',{'prepared':prepared,'base_sha':sha,'launches_agents':False});put(out/'sentinel'/'exporter-plan.json',{'source_required':True,'rig_id_required':True,'commit':COMMIT,'namespace':namespace,'port':port,'signals':'logs,metrics','checkpoint':str(out/'sentinel'/'checkpoint.json'),**{k:p['sentinel'][k] for k in ['start','poll_ms','seat_poll_ms','pseudonymize_seats']}})
    except Exception:
        put(out/'preparation-incomplete.json',{'prepared':prepared,'base_sha':sha,'action':'Inspect partial worktrees and branches; do not retry blindly.'});raise

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='command',required=True)
    v=sub.add_parser('validate');v.add_argument('project',type=Path)
    p=sub.add_parser('prepare');p.add_argument('project',type=Path);p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--namespace',required=True);p.add_argument('--fleet',choices=['pilot','full'],default='pilot');p.add_argument('--port',type=int);p.add_argument('--apply',action='store_true')
    a=ap.parse_args()
    try:
        if a.command=='validate':
            p,rows,seats,pilots,tasks=load(a.project);print(json.dumps({'project_id':p['project_id'],'teams':len(p['teams']),'logical_seats':len(rows),'pilot_seats':pilots,'missions':len(tasks),'status':'valid'},indent=2))
        else:prepare(a)
    except (ValueError,KeyError,TypeError,OSError,subprocess.CalledProcessError) as e:ap.exit(2,f'Validation/preparation failed: {e}\n')
if __name__=='__main__':main()
