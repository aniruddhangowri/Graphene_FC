import sys
import json
from string import strip, split
import datetime
import pickle
import numpy as np
from collections import defaultdict
import os

datadir = '../controlserver/log/'
logview = open('../controlserver/logview.txt')

def _pickle_logfiles(fnames):
    flowdict = {'flow': 1, 'noflow':0}
    devdict = defaultdict(list)
    for f in fnames:
        logfile = open(f);

        t0 = None
        for l in logfile:
            if l=='\n': continue
            i1, i2 = l.find(')'), l.find('[')
            if i2==-1: continue
            ip, t, msg = l[:i1+1], strip(l[i1+2:i2-2]), l[i2:]
            try: s = json.loads(msg)
            except: pass
            t = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S,%f')
            #print ip, t, msg
            if t0==None: t0 = t
            tdiff = t-t0
            tsec = tdiff.seconds + tdiff.microseconds/1E6
            for d in s:
                if 'status' not in d: continue
                if d['status'] == 'Error': continue
                points = devdict[d['dev']]
                if d['dev'][:2] == 'sw':
                    points.append([tsec, flowdict[d['value'][0]]])
                if d['dev'][:3] == 'mfc':
                    if d['cmd'] == 'get_flow':
                        points.append([tsec, float(d['value'][0])])
                if d['dev'][:3] == 'tvc':
                    if d['cmd'][:9] == 'get_press':
                        press, pos = map(float, split(d['value'][0], ','))
                        points.append([tsec, press])
        devdict1 = {}
        for k, v in devdict.iteritems():
            devdict1[k] = np.array(v)
        pickle.dump(devdict1, open(f+'.processed', 'w+'))

def _procfiles():
    global datadir
    txtfiles = [f for f in os.listdir(datadir) if f[-3:]=='txt']
    procedfiles = [f for f in os.listdir(datadir) if f[-9:]=='processed']
    for t in txtfiles:
        if t=='logview.txt': continue
        t1 = t+'.processed'
        if t1 not in procedfiles: 
            _pickle_logfiles([datadir+t])
            print 'processed:', t1

import threading
def background_proc():
    proc_thread = threading.Thread(target=_procfiles)
    proc_thread.start()
background_proc()

_d, _fname = None, ''
def _loaddata(fname):
    global _d, _fname
    if _d == None or _fname != fname:
        _fname = fname
        _d = pickle.load(open(_fname))
    return _d


logview.seek(0, 2)
def _tail(f):
    #loc = f.tell()
    retlines = []
    for l in f.readlines():
        if 'status' in l:
            retlines.append('[{'+split(l, ': [{')[1])
    # we send only the latest data point.
    return retlines[-1]
    
def get_plotdata(data):
    global logview
    global datadir
    d = None
    if data['cmd']=='get_filelist':
        files = [f for f in os.listdir(datadir) if f[-9:]=='processed']
        data['args'] = files
        return json.dumps(data)
    if data['cmd']=='get_view':
        args = data['args']
        dstr = ""
        #args[0] is filename, [1] is list of devices, [2] is plot name
        lo, hi = map(int, args['range'])
        d = _loaddata(datadir+args['fname'])
        for i in range(len(args['plots'])):
            skip = 1
            displaylen = 100
            ary = d[args['plots'][i]][lo:hi]
            #print len(ary), displaylen
            datnum = 1
            if len(ary) > displaylen: skip = int(len(ary)/displaylen)
            if len(ary) < displaylen: displaylen = len(ary)
            dstr += "var dat%d = new Float32Array(%d); dat%d = ["%(i, displaylen, i)
            for j in range(displaylen): dstr += "[%f, %f], "%(ary[j*skip][0], ary[j*skip][datnum])
            dstr += "];"
        data['args']['dat'] = dstr
        return json.dumps(data)
    if data['cmd']=='get_single':
        return _tail(logview)


