import json, pathlib, sys, tempfile, time, unittest, subprocess, socket, urllib.request, urllib.error
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'));import sentinel as s
from jsonschema import Draft202012Validator
ROOT=s.ROOT
NAMESPACE='atlas-test'; INSTANCE='test-instance'; NODE='test-node'; CFG={'version':'1.1.0','project_id':'test-project','title':'Test Project','roster':[{'seat':'platform.lead','team':'platform','runtime':'codex'}],'namespace':NAMESPACE,'ttl_seconds':90,'bindings':{NODE:'platform.lead'}}
def kv(k,v):return {'key':k,'value':{'stringValue':v}}
def envelope(signal,entries,instance=INSTANCE):
    metrics=signal=='metrics'; suffix='Metrics' if metrics else 'Logs'; scope={'name':'openrig.telemetry.metrics' if metrics else 'openrig.telemetry.queue_transitions','version':'1'}
    return {'resource'+suffix:[{'resource':{'attributes':[kv('service.name','openrig-telemetry-exporter'),kv('openrig.source.namespace',NAMESPACE),kv('service.instance.id',instance)]},'scope'+suffix:[{'scope':scope,'metrics' if metrics else 'logRecords':entries}]}]}
def sample(t,activity='working',presence='running',stale=False):
    ms=[]
    for n,k,states,val in [('activity','state',s.ACT,activity),('presence','status',s.PRES,presence)]:
        pts=[{'attributes':[kv('openrig.seat.node_id',NODE),kv('openrig.seat.'+k,st),kv('openrig.seat.runtime','codex'),kv('private.prompt','SHOULD_NOT_STORE')],'timeUnixNano':str(t),**({'flags':1} if stale else {'asInt':'1' if st==val else '0'})} for st in sorted(states)]
        ms.append({'name':'openrig.seat.'+n,'gauge':{'dataPoints':pts}})
    return envelope('metrics',ms)
def log(t):return envelope('logs',[{'body':{'stringValue':'openrig.queue.transition'},'observedTimeUnixNano':str(t),'attributes':[kv('openrig.transition.id','9223372036854775807'),kv('openrig.queue.state','pending'),kv('openrig.source.boot_epoch','test-boot')]}])
def validate(name,x):Draft202012Validator(json.loads((ROOT/'contracts'/f'{name}.schema.json').read_text())).validate(x)
class Tests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.path=pathlib.Path(self.tmp.name);self.db=s.Store(self.path/'db.sqlite',CFG)
    def tearDown(self):self.tmp.cleanup()
    def test_contracts(self):
        for p in (ROOT/'contracts').glob('*.schema.json'):Draft202012Validator.check_schema(json.loads(p.read_text()))
        validate('module-manifest',json.loads((ROOT/'module.json').read_text()));validate('module-config',CFG)
    def test_ingest_replay_ttl(self):
        t=time.time_ns()-1000000;rows=s.norm('metrics',sample(t),NAMESPACE)
        for r in rows:validate('observation',r)
        self.db.ingest(rows);self.db.ingest(rows);self.assertEqual(self.db.status()['record_count'],9)
        first=self.db.status()['cursor'];snap=self.db.snapshot();validate('snapshot',snap);self.assertEqual(snap['seats'][0]['activity'],'working');self.assertEqual(snap['seats'][0]['needs_input'],'unknown')
        self.db.ingest(s.norm('metrics',sample(time.time_ns()-1000000,activity='idle',presence='stopped'),NAMESPACE));self.assertEqual(self.db.snapshot()['seats'][0]['activity'],'unknown');self.assertEqual(self.db.snapshot(first)['seats'][0]['activity'],'working')
        self.db.ingest(s.norm('metrics',sample(time.time_ns()-1000000,stale=True),NAMESPACE));self.assertEqual(self.db.snapshot()['seats'][0]['presence'],'unknown')
        h=self.db.history(0,500);validate('history',h);self.assertNotIn('SHOULD_NOT_STORE',json.dumps(h));validate('status',self.db.status())
        self.assertEqual(s.Store(self.path/'db.sqlite',CFG).status()['record_count'],27)
    def test_late_and_ttl(self):
        t=time.time_ns()-100000000000;self.db.ingest(s.norm('metrics',sample(t),NAMESPACE));self.assertEqual(self.db.snapshot()['seats'][0]['presence'],'unknown')
        now=time.time_ns()-1000000;self.db.ingest(s.norm('metrics',sample(now,activity='idle'),NAMESPACE));self.db.ingest(s.norm('metrics',sample(now-1,activity='working'),NAMESPACE));self.assertEqual(self.db.snapshot()['seats'][0]['activity'],'idle')
    def test_logs_and_instance(self):
        rows=s.norm('logs',log(time.time_ns()),NAMESPACE);self.db.ingest(rows);self.assertEqual(self.db.snapshot()['recent'][0]['data']['transition_id'],'9223372036854775807');bad=[dict(rows[0],instance='different')];self.assertRaises(ValueError,self.db.ingest,bad);self.assertEqual(self.db.status()['record_count'],1)
        self.assertRaises(ValueError,s.Store,self.path/'db.sqlite',dict(CFG,ttl_seconds=100))
    def test_http(self):
        conf=self.path/'cfg.json';conf.write_text(json.dumps(CFG));sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close();base=f'http://127.0.0.1:{port}'
        proc=subprocess.Popen([sys.executable,str(ROOT/'tools/sentinel.py'),'serve','--config',str(conf),'--db',str(self.path/'http.sqlite'),'--port',str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            self.assertIn(b'Sentinel',proc.stdout.readline());
            def post(obj,headers={}):return urllib.request.urlopen(urllib.request.Request(base+'/v1/metrics',data=json.dumps(obj).encode(),headers={'Content-Type':'application/json',**headers}),timeout=5)
            with post(sample(time.time_ns()-1000000)) as r:self.assertEqual(r.status,200)
            with urllib.request.urlopen(base+'/api/v1/snapshot') as r:validate('snapshot',json.load(r))
            with self.assertRaises(urllib.error.HTTPError) as cm:post(sample(time.time_ns()),{'Origin':'https://other.example'})
            self.assertEqual(cm.exception.code,403)
            with self.assertRaises(urllib.error.HTTPError) as cm:post({'invalid':[]})
            self.assertEqual(cm.exception.code,400)
            with urllib.request.urlopen(base+'/') as r:self.assertIn(b'OBSERVED MESH',r.read())
        finally:proc.terminate();proc.communicate(timeout=5)
    def test_projection(self):
        for name in ['claude','codex']:
            f=self.path/'agents'/name/'agent.yaml';f.parent.mkdir(parents=True);f.write_text(json.dumps({'version':'1.0','profiles':{'default':{'uses':{}}}}))
        cmd=[sys.executable,str(ROOT/'tools/project_skill.py'),'--rig-dir',str(self.path)]
        subprocess.run(cmd,check=True,capture_output=True);self.assertFalse((self.path/'agents/claude/skills').exists())
        subprocess.run(cmd+['--apply'],check=True,capture_output=True);subprocess.run(cmd+['--apply'],check=True,capture_output=True)
        for f in self.path.glob('agents/*/agent.yaml'):self.assertEqual(json.loads(f.read_text())['profiles']['default']['uses']['skills'],['sentinel-monitor'])
if __name__=='__main__':unittest.main(verbosity=2)
