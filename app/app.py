import json
import os
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STARTED = time.monotonic()
VERSION = os.environ.get('APP_VERSION', '1.0.0')
SID = os.environ.get('STUDENT_ID', '02230140')
NOTICES = [
    {'id': 1, 'title': 'Campus library hours', 'message': 'Study hall opens at 8:00 AM'},
    {'id': 2, 'title': 'ICT support', 'message': 'Submit support requests to the service desk'},
    {'id': 3, 'title': 'Student Services', 'message': 'Collect your student ID at the office'},
]

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data):
        body = json.dumps(data, separators=(',', ':')).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/version':
            return self.reply(200, {'version': VERSION, 'student': SID, 'pod': socket.gethostname()})
        if self.path == '/healthz':
            if VERSION == '1.2.0-broken':
                return self.reply(503, {'status':'unhealthy', 'reason':'intentional broken release'})
            if time.monotonic() - STARTED < 5:
                return self.reply(503, {'status':'warming-up'})
            return self.reply(200, {'status':'healthy'})
        if self.path == '/notices':
            if VERSION == '1.0.0':
                return self.reply(200, NOTICES)
            notices = [dict(n, category=c, pinned=(n['id']==3)) for n,c in zip(NOTICES, ['academic', 'technical', 'administration'])]
            enabled = os.environ.get('FEATURE_PINNED', 'false').lower() == 'true'
            if enabled:
                notices.sort(key=lambda n: not n['pinned'])
            return self.reply(200, {'pinnedFirst':enabled, 'notices':notices})
        return self.reply(404, {'error':'not found'})

if __name__ == '__main__':
    print(f'Starting Campus Notice Board {VERSION} for {SID}',flush=True)
    ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
