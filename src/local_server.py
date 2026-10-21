#!/usr/bin/env python3
"""Local browser UI sharing decision_engine.py's recommendation logic."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from decision_engine import ROOT, load, next_question, requirement_filter, capability

QUESTIONS = json.loads((ROOT/'data/questions.json').read_text())

def filter_state(history):
    rows, _ = load(ROOT/'data/schemes.csv')
    available = QUESTIONS[:]
    answers = {}
    for item in history:
        q = next_question(rows, available)
        if q is None or item.get('id') != q['id'] or item.get('answer') not in ('yes','no',None):
            raise ValueError('Invalid answer sequence. Please restart.')
        value = item['answer']
        answers[q['id']] = value
        rows = requirement_filter(rows, q['id'], value)
        available = [x for x in available if x['id'] != q['id']]
    q = next_question(rows, available)
    candidates = []
    for row in rows:
        pending = [qid for qid, value in answers.items() if value == 'yes' and capability(row,qid) is None]
        candidates.append({**row,'pending':pending})
    return {'question':q,'candidates':candidates,'answered':len(history),
            'unknown':[k for k,v in answers.items() if v is None],
            'unasked':[x['id'] for x in available], 'done':q is None}

def state(history):
    from ranking import next_preference, rank
    base_history=[];preferences={};ranking_started=False
    for item in history:
        if item.get('id','').startswith('R'):
            ranking_started=True
            base=filter_state(base_history)
            if not base['done']:raise ValueError('Requirements must come first')
            q=next_preference(base['candidates'],preferences)
            if q is None or item.get('id')!=q['id'] or item.get('answer') not in ('yes','no',None):raise ValueError('Invalid ranking answer sequence')
            preferences[q['id']]=item['answer']
        else:
            if ranking_started:raise ValueError('Invalid answer order')
            base_history.append(item)
    result=filter_state(base_history)
    result['phase']='requirements'
    if result['done']:
        result['phase']='ranking'
        result['question']=next_preference(result['candidates'],preferences)
        result['done']=result['question'] is None
        result['candidates']=rank(result['candidates'],preferences)
    result['unknown']+= [key for key,val in preferences.items() if val is None]
    result['answered']=len(history)
    return result

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, body, kind='application/json'):
        raw = body.encode()
        self.send_response(code)
        self.send_header('Content-Type',kind+'; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        if self.path not in ('/','/index.html'):
            self.respond(404,'Not found','text/plain');return
        self.respond(200,(ROOT/'web/index.html').read_text(),'text/html')
    def do_POST(self):
        if self.path != '/api/state':
            self.respond(404,'{}');return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length>10000:raise ValueError('Request too large')
            data=json.loads(self.rfile.read(length))
            history=data.get('history',[])
            if not isinstance(history,list) or len(history)>len(QUESTIONS)+3:raise ValueError('Invalid history')
            self.respond(200,json.dumps(state(history)))
        except (ValueError,TypeError,AttributeError,KeyError) as e:
            self.respond(400,json.dumps({'error':str(e)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    print(f'Open http://127.0.0.1:{args.port} — Ctrl-C to stop.',flush=True)
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
