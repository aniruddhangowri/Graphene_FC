from string import split, strip, join
from tempfile import NamedTemporaryFile
import json

def _validate(data):
    # nothing being done here for now. only comment removal.
    lines = [x for x in map(strip, split(data, '\n')) if x!='' and x[0]!='#' ]
    script = ''
    t0, t, d, c, a = None, None, None, None, None
    for l in lines:
        t, d, c, a = l.split(' ', 3)
        t = int(t)
        if t0 == None: t0 = t
        t = str(t-t0)
        script += ' '.join([t, d, c, a])+'\n'
    return script

import os.path
script_format = """timestamp dev cmd args.
args can be empty. others cannot be. Timestamp is in milisecond"""
def _save_script(data):
    # parse data to a script and offer it for saving
    script = _validate(data)
    print script
    f = NamedTemporaryFile(suffix='.txt', dir='./public/tmp-scripts/', delete=False)
    f.write(script)
    f.close()
    return '/static/tmp-scripts/'+os.path.basename(f.name)

def process_req(data):
    print data
    resp = []
    for d in data:
        if d['cmd'] == 'save':
            d['args'] = [_save_script(d['args'][0])]
            resp.append(d)
            return json.dumps(resp)
        if d['cmd'] == 'load':
            pass
