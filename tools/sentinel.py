#!/usr/bin/env python3
"""Sentinel OpenRig companion. Local-only, metadata-only, no harness writes."""
import argparse, hashlib, json, os, re, sqlite3, sys, time
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[1]
TOKEN=re.compile(r'^[A-Za-z0-9._:-]{1,256}$')
DEC=re.compile(r'^(0|[1-9][0-9]{0,19})$')
ACT={'working','idle','needs-input','unknown'}; PRES={'running','exited','stopped','detached','unknown'}
RUNTIME={'claude-code','codex','pi','omp','terminal','stub'}
QUEUE={'pending','in-progress','done','blocked','failed','denied','canceled','handed-off'}
CLOSURE={'handed_off_to','blocked_on','denied','canceled','no-follow-on','escalation','superseded'}
GAPS={'historical_transitions_not_read','boot_boundary_history_unverified','watermark_regression_history_unverified','before_retained_floor','retained_sequence_gap','conflicting_transition_id','oversized_field','invalid_type','invalid_timestamp','record_byte_limit','gap_details_truncated','page_intervals_suppressed','open_interval_evicted','invalid_interval_boundary'}
GAUGES={'openrig.seat.activity','openrig.seat.presence','openrig.seat.needs_input'}
COUNTERS={'openrig.queue.transition.observed','openrig.telemetry.coverage.gap','openrig.telemetry.failure'}
HIST='openrig.queue.state.duration'
LOG_KINDS={'queue_transition','seat_tenure_change','gap','failure'}
MAX_BODY=2*1024*1024; MAX_POINTS=5376; MAX_LOGS=448

def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def token(s):
    if not isinstance(s,str) or not TOKEN.fullmatch(s): raise ValueError('invalid metadata identifier')
    return s

def decimal(s):
    if not isinstance(s,str) or not DEC.fullmatch(s) or int(s)>18446744073709551615: raise ValueError('invalid uint64 string')
    return s

def enum(s, allowed):
    if s not in allowed: raise ValueError('unsupported enum')
    return s

def attrs(items):
    # OTLP AnyValue supports more than strings. Read strings only; never persist arbitrary values.
    if not isinstance(items,list): raise ValueError('attributes must be list')
    out={}
    for a in items:
        k=a['key']; v=a['value'];
        if k in out: raise ValueError('duplicate attribute')
        out[k]=v.get('stringValue') if isinstance(v,dict) else None
    return out

def res_identity(r, namespace):
    a=attrs(r.get('resource',{}).get('attributes',[]))
    if a.get('service.name')!='openrig-telemetry-exporter' or a.get('openrig.source.namespace')!=namespace: raise ValueError('source mismatch')
    return token(a['service.instance.id'])

def norm(signal, payload, namespace):
    if not isinstance(payload,dict): raise ValueError('expected object')
    rows=[]; key='resourceMetrics' if signal=='metrics' else 'resourceLogs'
    if key not in payload or not isinstance(payload[key],list): raise ValueError('invalid OTLP envelope')
    for resource in payload[key]:
        instance=res_identity(resource,namespace)
        for scope in resource.get('scopeMetrics' if signal=='metrics' else 'scopeLogs',[]):
            expected='openrig.telemetry.metrics' if signal=='metrics' else 'openrig.telemetry.queue_transitions'
            if scope.get('scope',{}).get('name')!=expected or scope.get('scope',{}).get('version')!='1': raise ValueError('unsupported scope/version')
            if signal=='metrics':
                for metric in scope.get('metrics',[]):
                    name=metric['name']; typ='gauge' if name in GAUGES else 'sum' if name in COUNTERS else 'histogram' if name==HIST else None
                    if typ is None: raise ValueError('unsupported metric')
                    for pt in metric[typ]['dataPoints']:
                        a=attrs(pt.get('attributes',[])); ts=decimal(pt['timeUnixNano']); flags=pt.get('flags',0)
                        if type(flags) is not int or flags not in (0,1): raise ValueError('invalid flags')
                        value=None if flags==1 else decimal(pt['count'] if typ=='histogram' else pt['asInt'])
                        data={}
                        if name in GAUGES:
                            data['node_id']=token(a['openrig.seat.node_id'])
                            if a.get('openrig.seat.runtime') is not None: data['runtime']=enum(a['openrig.seat.runtime'],RUNTIME)
                            if name.endswith('.activity'): data['label']=enum(a['openrig.seat.state'],ACT)
                            if name.endswith('.presence'): data['label']=enum(a['openrig.seat.status'],PRES)
                            if name!='openrig.seat.needs_input' and value not in (None,'0','1'): raise ValueError('invalid gauge')
                        elif name in ('openrig.queue.transition.observed',HIST):
                            data['label']=a.get('openrig.queue.state') if a.get('openrig.queue.state') in QUEUE else 'unknown'
                            if name==HIST: data['departure_state']=enum(a['openrig.queue.departure_state'],QUEUE)
                            if a.get('openrig.queue.closure_reason') in CLOSURE: data['closure_reason']=a['openrig.queue.closure_reason']
                        elif name.endswith('.gap'):
                            # Unknown future codes are represented as unknown, never copied verbatim.
                            data['label']=a.get('openrig.gap.code') if a.get('openrig.gap.code') in GAPS else 'unknown'
                        else:
                            data['label']=enum(a['openrig.failure.stage'],{'source','export','ledger'})
                            # Exporter categories can evolve. Do not persist arbitrary strings.
                        if typ!='gauge': data['start_ns']=decimal(pt['startTimeUnixNano'])
                        rows.append(dict(kind='metric',namespace=namespace,instance=instance,observed_ns=ts,name=name,value=value,data=data))
                        if len(rows)>MAX_POINTS: raise ValueError('too many metrics')
            else:
                for log in scope.get('logRecords',[]):
                    a=attrs(log.get('attributes',[])); name=log.get('body',{}).get('stringValue')
                    allowed={'openrig.queue.transition','openrig.seat.tenure_change.observed','openrig.telemetry.gap','openrig.telemetry.failure'}
                    if name not in allowed: raise ValueError('unsupported log')
                    ts=decimal(log['observedTimeUnixNano']); data={}
                    if a.get('openrig.source.boot_epoch') is not None: data['boot_epoch']=token(a['openrig.source.boot_epoch'])
                    if name=='openrig.queue.transition':
                        data['transition_id']=decimal(a['openrig.transition.id']); data['label']=a.get('openrig.queue.state') if a.get('openrig.queue.state') in QUEUE else 'unknown'
                        if a.get('openrig.coverage.status') in {'retained_window','partial','unavailable'}: data['coverage']=a['openrig.coverage.status']
                        if a.get('openrig.identity.provenance') in {'transport:v1','relay:v1','claimed:v1','origin-unknown:v1','principal:v1'}: data['identity_provenance']=a['openrig.identity.provenance']
                        if a.get('openrig.queue.closure_reason') in CLOSURE: data['closure_reason']=a['openrig.queue.closure_reason']
                    elif name=='openrig.seat.tenure_change.observed':
                        data['node_id']=token(a['openrig.seat.node_id']); data['prior_generation']=token(a['openrig.tenure.prior_generation']); data['new_generation']=token(a['openrig.tenure.new_generation']); data['continuity']='intermediate_changes_unknown'
                    elif name=='openrig.telemetry.gap':
                        data['label']=a.get('openrig.gap.code') if a.get('openrig.gap.code') in GAPS else 'unknown'
                        for suffix in ('id','from','through'):
                            if a.get('openrig.gap.'+suffix) is not None: data['gap_'+suffix]=decimal(a['openrig.gap.'+suffix])
                    else: data['label']=enum(a['openrig.failure.stage'],{'source','export','ledger'})
                    if log.get('timeUnixNano') is not None: data['occurred_ns']=decimal(log['timeUnixNano'])
                    rows.append(dict(kind='log',namespace=namespace,instance=instance,observed_ns=ts,name=name,value=None,data=data))
                    if len(rows)>MAX_LOGS: raise ValueError('too many logs')
    return rows

SLUG=re.compile(r'^[a-z][a-z0-9-]{0,62}$')
def roster_index(rows):
    if not isinstance(rows,list) or not 1<=len(rows)<=128: raise ValueError('roster must contain 1–128 seats')
    result={}
    for r in rows:
        if set(r)!={'seat','team','runtime'} or not SLUG.fullmatch(r['team']) or r['team']=='unmapped': raise ValueError('invalid roster team')
        parts=r['seat'].split('.')
        if len(parts)!=2 or parts[0]!=r['team'] or not SLUG.fullmatch(parts[1]) or r['seat'] in result or r['runtime'] not in RUNTIME: raise ValueError('invalid or duplicate seat')
        result[r['seat']]=r
    if len({r['team'] for r in rows})>16: raise ValueError('maximum 16 teams')
    return result

def validate_config(c):
    if not isinstance(c,dict) or set(c)!={'version','project_id','title','namespace','ttl_seconds','bindings','roster'} or c['version']!='1.1.0': raise ValueError('unsupported config; initialize v1.1 with explicit roster, preserve legacy journal')
    if not SLUG.fullmatch(c['project_id']) or not isinstance(c['title'],str) or not 1<=len(c['title'])<=160: raise ValueError('invalid project')
    seats=roster_index(c['roster'])
    token(c['namespace']);
    if len(c['namespace'])>128 or type(c['ttl_seconds']) is not int or not 10<=c['ttl_seconds']<=600: raise ValueError('invalid namespace or TTL')
    if not isinstance(c['bindings'],dict) or len(c['bindings'])>128: raise ValueError('invalid bindings')
    for k,v in c['bindings'].items(): token(k); enum(v,seats)
    if len(set(c['bindings'].values()))!=len(c['bindings']): raise ValueError('duplicate seat binding')
    return c

def load_config(path): return validate_config(json.loads(path.read_text()))

class Store:
    def __init__(self,path,config):
        self.path=path; self.config=validate_config(config); self.seats=roster_index(config['roster'])
        with self.db() as c:
            c.execute('PRAGMA journal_mode=WAL'); c.execute('CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY,value TEXT NOT NULL)'); c.execute('CREATE TABLE IF NOT EXISTS records (seq INTEGER PRIMARY KEY AUTOINCREMENT, identity TEXT UNIQUE NOT NULL,received_ns TEXT NOT NULL, record TEXT NOT NULL, kind TEXT NOT NULL, node TEXT, name TEXT NOT NULL,label TEXT NOT NULL, observed_ns TEXT NOT NULL)'); c.execute('CREATE INDEX IF NOT EXISTS record_series ON records(kind,node,name,label,seq)')
            v=digest(config); old=c.execute("SELECT value FROM meta WHERE key='config'").fetchone()
            if old and old[0]!=v: raise ValueError('journal configuration changed; use a new journal or original config')
            c.execute("INSERT OR IGNORE INTO meta VALUES('config',?)",(v,))
    @contextmanager
    def db(self):
        c=sqlite3.connect(self.path,timeout=5)
        try:
            with c: yield c
        finally: c.close()
    def ingest(self,rows):
        received=str(time.time_ns())
        with self.db() as c:
            for row in rows:
                prior=c.execute("SELECT value FROM meta WHERE key='instance'").fetchone()
                if prior and prior[0]!=row['instance']: raise ValueError('exporter instance changed; use new journal')
                c.execute("INSERT OR IGNORE INTO meta VALUES('instance',?)",(row['instance'],))
                d=row['data']; c.execute('INSERT OR IGNORE INTO records(identity,received_ns,record,kind,node,name,label,observed_ns) VALUES(?,?,?,?,?,?,?,?)',(digest(row),received,canon(row),row['kind'],d.get('node_id'),row['name'],d.get('label',''),row['observed_ns']))
    def status(self):
        with self.db() as c:
            n,high,latest=c.execute('SELECT COUNT(*),COALESCE(MAX(seq),0),MAX(received_ns) FROM records').fetchone()
        return {'module':'sentinel-openrig','version':'0.4.0','project_id':self.config['project_id'],'title':self.config['title'],'namespace':self.config['namespace'],'record_count':n,'cursor':high,'last_received_ns':latest,'history_completeness':'unknown','bindings':len(self.config['bindings']),'scope':'local_metadata_only'}
    def history(self,after,limit):
        with self.db() as c: records=c.execute('SELECT seq,received_ns,record FROM records WHERE seq>? ORDER BY seq LIMIT ?',(after,limit+1)).fetchall()
        rows=[{'seq':s,'received_ns':ts,**json.loads(rec)} for s,ts,rec in records[:limit]]
        return {'rows':rows,'next_cursor':rows[-1]['seq'] if rows else after,'has_more':len(records)>limit}
    def snapshot(self,at=None):
        with self.db() as c:
            high=c.execute('SELECT COALESCE(MAX(seq),0) FROM records').fetchone()[0]
            if at is not None and at>high: raise ValueError('cursor beyond journal')
            cursor=high if at is None else at
            when=str(time.time_ns()) if at is None else (c.execute('SELECT MAX(received_ns) FROM records WHERE seq<=?',(cursor,)).fetchone()[0] or '0')
            # Group by series, use source observation time first, then journal order. Later arrival of older sample cannot resurrect it.
            rs=c.execute('''SELECT seq,record FROM (SELECT seq,record,ROW_NUMBER() OVER (PARTITION BY node,name,label ORDER BY LENGTH(observed_ns) DESC,observed_ns DESC,seq DESC) AS rn FROM records WHERE seq<=? AND kind='metric' AND node IS NOT NULL) WHERE rn=1''',(cursor,)).fetchall()
            logs=c.execute("SELECT seq,record FROM records WHERE seq<=? AND kind='log' ORDER BY seq DESC LIMIT 40",(cursor,)).fetchall()
        nodes={}; ttl=self.config['ttl_seconds']*10**9
        for seq,raw in rs:
            r=json.loads(raw); node=r['data']['node_id']; nodes.setdefault(node,[]).append(r)
        seats=[]; binding=self.config['bindings']
        for node,points in sorted(nodes.items()):
            def pick(name):
                p=[x for x in points if x['name']==name];
                if not p: return 'unknown'
                latest=max(int(x['observed_ns']) for x in p)
                # Source sample time, not arrival time. A clock-skewed future point is unknown.
                if not 0<=int(when)-latest<=ttl: return 'unknown'
                p=[x for x in p if int(x['observed_ns'])==latest];
                if any(x['value'] is None for x in p): return 'unknown'
                if name.endswith('.needs_input'): return 'yes' if int(p[0]['value'])>0 else 'no'
                ones=[x['data']['label'] for x in p if x['value']=='1']; return ones[0] if len(ones)==1 else 'unknown'
            label=binding.get(node); presence=pick('openrig.seat.presence'); activity=pick('openrig.seat.activity')
            if presence!='running': activity='unknown'
            newest=max(points,key=lambda x:int(x['observed_ns']));
            seats.append({'node_id':node,'seat':label,'team':self.seats[label]['team'] if label else 'unmapped','runtime':newest['data'].get('runtime'),'presence':presence,'activity':activity,'needs_input':pick('openrig.seat.needs_input'),'sample_ns':newest['observed_ns']})
        return {'cursor':cursor,'high_watermark':high,'as_of_ns':when,'mode':'observed' if at is None else 'replay','history_completeness':'unknown','ttl_seconds':self.config['ttl_seconds'],'seats':seats,'recent':[{'seq':s,**json.loads(r)} for s,r in logs],'communication_available':False}

def server(store,port):
    class Handler(BaseHTTPRequestHandler):
        def setup(self): super().setup(); self.connection.settimeout(10)
        def log_message(self,*a): pass
        def send(self,status,obj,ctype='application/json'):
            body=canon(obj).encode() if ctype=='application/json' else obj
            self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('X-Frame-Options','DENY'); self.send_header('Referrer-Policy','no-referrer'); self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'"); self.end_headers(); self.wfile.write(body)
        def allowed(self): return self.headers.get('Host') in {f'127.0.0.1:{port}',f'localhost:{port}'} and self.headers.get('Origin') in {None,f'http://127.0.0.1:{port}',f'http://localhost:{port}'} and self.headers.get('Sec-Fetch-Site') not in {'cross-site','same-site'}
        def do_GET(self):
            if not self.allowed(): return self.send(403,{'error':'local requests only'})
            p=urlsplit(self.path); q=parse_qs(p.query)
            try:
                if p.path in {'/','/simulation.html'}: return self.send(200,(ROOT/'web'/('live.html' if p.path=='/' else 'simulation.html')).read_bytes(),'text/html; charset=utf-8')
                if p.path=='/api/v1/status': return self.send(200,store.status())
                if p.path=='/api/v1/roster': return self.send(200,store.config['roster'])
                if p.path=='/api/v1/snapshot':
                    at=int(q['at'][0]) if 'at' in q else None
                    if at is not None and at<0: raise ValueError()
                    return self.send(200,store.snapshot(at))
                if p.path=='/api/v1/history':
                    after=int(q.get('after',['0'])[0]); limit=int(q.get('limit',['100'])[0]);
                    if after<0 or not 1<=limit<=500: raise ValueError()
                    return self.send(200,store.history(after,limit))
                return self.send(404,{'error':'not found'})
            except (ValueError,OverflowError): return self.send(400,{'error':'invalid query'})
            except sqlite3.Error: return self.send(503,{'error':'journal unavailable'})
        def do_POST(self):
            if not self.allowed() or self.headers.get('Origin') is not None or self.headers.get('Sec-Fetch-Site') is not None: return self.send(403,{'error':'local exporter only'})
            if self.path not in {'/v1/logs','/v1/metrics'}: return self.send(404,{'error':'unsupported OTLP signal'})
            if self.headers.get_content_type()!='application/json' or self.headers.get('Content-Encoding','identity')!='identity' or self.headers.get('Transfer-Encoding'): return self.send(415,{'error':'OTLP JSON only'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=MAX_BODY: return self.send(413,{'error':'invalid batch length'})
                raw=self.rfile.read(size); rows=norm(self.path.split('/')[-1],json.loads(raw),store.config['namespace']); store.ingest(rows)
                return self.send(200,{})
            except (ValueError,KeyError,TypeError,AttributeError,OverflowError,RecursionError): return self.send(400,{'error':'unsupported or malformed telemetry batch'})
            except sqlite3.Error: return self.send(503,{'error':'journal unavailable'})
    httpd=ThreadingHTTPServer(('127.0.0.1',port),Handler); print(f'Sentinel http://127.0.0.1:{port}/',flush=True); httpd.serve_forever()

def main():
    os.umask(0o077); p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('init'); i.add_argument('--config',type=Path,required=True); i.add_argument('--namespace',required=True); i.add_argument('--ttl',type=int,default=90); i.add_argument('--project-id',required=True); i.add_argument('--title',required=True); i.add_argument('--roster',type=Path,required=True)
    b=sub.add_parser('bind'); b.add_argument('--config',type=Path,required=True); b.add_argument('--node',required=True); b.add_argument('--seat',required=True)
    s=sub.add_parser('serve'); s.add_argument('--config',type=Path,required=True); s.add_argument('--db',type=Path,required=True); s.add_argument('--port',type=int,default=8766)
    a=p.parse_args()
    if a.cmd=='init':
        token(a.namespace)
        if len(a.namespace)>128 or not 10<=a.ttl<=600: p.error('invalid namespace/TTL')
        a.config.parent.mkdir(parents=True,exist_ok=True)
        c=validate_config({'version':'1.1.0','project_id':a.project_id,'title':a.title,'namespace':a.namespace,'ttl_seconds':a.ttl,'bindings':{},'roster':json.loads(a.roster.read_text())})
        with a.config.open('x') as f: json.dump(c,f,indent=2)
    elif a.cmd=='bind':
        c=load_config(a.config); token(a.node); enum(a.seat,roster_index(c['roster']))
        if a.node in c['bindings'] or a.seat in c['bindings'].values(): p.error('binding already exists; inspect rather than overwrite')
        c['bindings'][a.node]=a.seat; tmp=a.config.with_suffix(a.config.suffix+'.new')
        with tmp.open('x') as f: json.dump(c,f,indent=2)
        tmp.replace(a.config)
    else:
        a.db.parent.mkdir(parents=True,exist_ok=True); server(Store(a.db,load_config(a.config)),a.port)
if __name__=='__main__': main()
