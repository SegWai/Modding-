#!/usr/bin/env python3
"""Summarize v96 runtime logs without inferring physics from an animation."""
import argparse
import json
import re
import zipfile
from pathlib import Path


def analyze(text):
    groups={}
    for line in text.splitlines():
        if '[MLPHY96]' not in line:
            continue
        values=dict(re.findall(r'(\w+)=([^\s]+)',line.split('[MLPHY96]',1)[1]))
        if not all(k in values for k in ('type','event','t','stage')):
            continue
        key=tuple(values[k] for k in ('type','event','t'))
        state=groups.setdefault(key,{'type':key[0],'event':key[1],'t':key[2]})
        state['last_stage']=values['stage']
        if values['stage']=='begin':state['alive']=values.get('alive')
        if values['stage']=='human':state['ragdoll']=values.get('ragdoll')
        if values['stage']=='complete':
            state.update({k:v for k,v in values.items() if k not in ('type','event','t','stage')})
            state['complete']=True
    snapshots=list(groups.values())
    human=[s for s in snapshots if s['event'].startswith('human_death') and s.get('complete') and s.get('ragdoll','').lower() in ('1','true')]
    infected=[s for s in snapshots if s['event'].startswith('infected_death') and s.get('complete') and s.get('alive','').lower() in ('0','false')]
    def max_count(rows,key):
        return max((int(s.get(key,-1)) for s in rows),default=-1)
    if not snapshots:
        verdict='No v96 probe markers found. This log cannot diagnose the physics path.'
    elif not human or not infected:
        verdict='Incomplete comparison: need completed dead-infected and active-human-ragdoll samples. Check unfinished stages and any compile/runtime errors.'
    elif max_count(human,'bones')==0 and max_count(infected,'bones')==0:
        verdict='Both the active human ragdoll and dead infected expose zero bones through this API. The positive control shows this enumeration cannot distinguish their articulated physics. Do not infer infected ragdoll absence from it.'
    elif max_count(human,'present')>1 and max_count(infected,'bones')==0:
        verdict='Working human exposes multiple bone physics bodies; dead infected exposes none through this API. Changing simulation flags on existing infected bones is not supported by these observations.'
    elif max_count(infected,'present')>1:
        verdict='Dead infected exposes multiple bone physics bodies. Inspect their dynamic/kinematic state and animation ownership before selecting an activation experiment; this is not proof of a working ragdoll.'
    else:
        verdict='The API does not provide a decisive articulated-body comparison. Do not infer native ragdoll availability from these counts alone.'
    return {'verdict':verdict,'human_ragdoll_samples':len(human),'dead_infected_samples':len(infected),
            'unfinished_samples':[s for s in snapshots if not s.get('complete')], 'snapshots':snapshots}


def read_logs(path):
    if path.suffix.lower()!='.zip':
        return path.read_text(errors='replace')
    with zipfile.ZipFile(path) as archive:
        selected=[i for i in archive.infolist() if not i.is_dir() and Path(i.filename).suffix.lower() in ('.log','.rpt')]
        if sum(i.file_size for i in selected)>128*1024*1024:
            raise ValueError('Log input exceeds size budget')
        return '\n'.join(archive.read(i).decode('utf-8',errors='replace') for i in selected)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('logs',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=json.dumps(analyze(read_logs(args.logs)),indent=2)+'\n'
    if args.output:args.output.write_text(result)
    else:print(result,end='')
