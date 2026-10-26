"""Compare clean vanilla/custom standing lean measurements; do not choose a target blindly."""
from pathlib import Path
import json,re,math,argparse,zipfile

def analyze(texts):
 sessions={};completed=[]
 for text in texts:
  for line in text.splitlines():
   m=re.search(r'\[MLDIST49\] SESSION id=(\S+) setup=(\S+) native_workspace=(true|false)',line)
   if m:
    sid,setup,native=m.groups();sessions[(sid,setup,native=='true')]={'states':{},'setup':setup,'session':sid,'native':native=='true'};continue
   m=re.search(r'\[MLDIST49\] RESULT session=(\S+) mode=(native|custom) setup=(\S+) sign=(-?\d+) samples=(\d+) duration_ms=(\d+)',line)
   if m:
    sid,mode,setup,sign,count,duration=m.groups();key=(sid,setup,mode=='native');session=sessions.get(key)
    if not session:raise ValueError('Result has no matching native/custom session proof')
    sign=int(sign);count=int(count);duration=int(duration)
    if sign not in (-1,0,1) or count<20 or duration<500:raise ValueError('Unstable or incomplete state measurement')
    row={'samples':count,'duration_ms':duration}
    for field in ('head_ms','chest_ms','pelvis_ms','left_foot_ms','right_foot_ms','eye_centre_ms','root_ws','actor_ypr'):
     vm=re.search(r'\b'+field+r'=<([^>]+)>',line)
     if not vm:raise ValueError('Missing measurement '+field)
     values=list(map(float,vm[1].split(',')))
     if len(values)!=3 or not all(math.isfinite(x) for x in values):raise ValueError('Invalid measurement vector')
     row[field]=values
    for field in ('head_x_min','head_x_max'):
     fm=re.search(r'\b'+field+r'=([-+\d.eE]+)',line)
     if not fm:raise ValueError('Missing head range')
     row[field]=float(fm[1])
     if not math.isfinite(row[field]):raise ValueError('Invalid head range')
    session['states'][sign]=row;continue
   m=re.search(r'\[MLDIST49\] COMPLETE mode=(native|custom) session=(\S+)',line)
   if m:
    mode,sid=m.groups()
    found=[s for s in sessions.values() if s['session']==sid and s['native']==(mode=='native') and set(s['states'])=={-1,0,1}]
    if found:completed.append(found[-1])
 latest={}
 for s in completed:latest['native' if s['native'] else 'custom']=s
 if set(latest)!={'native','custom'}:raise ValueError('Need completed clean native AND custom neutral/left/right runs')
 if latest['native']['setup']!=latest['custom']['setup']:raise ValueError('Weapon or raised/ADS/optics modes do not match across runs')
 report={'setup':latest['native']['setup'],'measurement_basis':'Head-bone model-X displacement from each run\'s neutral. Eyes/chest/root/feet retained for exposure and footprint review.','runs':{},'native_target_chosen':False}
 for mode,s in latest.items():
  states=s['states'];base=states[0]
  extents={};details={}
  for sign,side in ((-1,'left'),(1,'right')):
   delta=states[sign]['head_ms'][0]-base['head_ms'][0]
   if (sign<0 and delta>=-.001) or (sign>0 and delta<=.001):raise ValueError('Head did not move to the expected '+side+' side in '+mode)
   extents[side]=abs(delta)
   root=states[sign]['root_ws'];root0=base['root_ws']
   details[side]={'head_signed_dx_m':delta,'chest_signed_dx_m':states[sign]['chest_ms'][0]-base['chest_ms'][0],'eye_centre_signed_dx_m':states[sign]['eye_centre_ms'][0]-base['eye_centre_ms'][0],'root_translation_m':math.sqrt(sum((a-b)**2 for a,b in zip(root,root0))),'left_foot_ms':states[sign]['left_foot_ms'],'right_foot_ms':states[sign]['right_foot_ms']}
  report['runs'][mode]={'session':s['session'],'head_extent_m':extents,'details':details,'samples':states}
 n=report['runs']['native']['head_extent_m'];c=report['runs']['custom']['head_extent_m'];asym=abs(n['left']-n['right'])
 noise=max(v['head_x_max']-v['head_x_min'] for v in latest['native']['states'].values())
 report.update(native_left_right_asymmetry_m=asym,native_observed_head_x_range_max_m=noise,meaningful_native_asymmetry=asym>max(.005,2*noise),shared_vanilla_midpoint_candidate_m=(n['left']+n['right'])/2,custom_minus_native_extent_m={side:c[side]-n[side] for side in ('left','right')})
 report['next_step']='Report native side difference before selecting a symmetric target; no pose correction applied by this analyzer.'
 return report

def load(path):
 path=Path(path)
 if zipfile.is_zipfile(path):
  with zipfile.ZipFile(path) as z:return analyze([z.read(n).decode('utf8',errors='replace') for n in sorted(z.namelist()) if Path(n).name.startswith('script_') and n.endswith('.log')])
 if path.is_dir():return analyze([p.read_text(encoding='utf8',errors='replace') for p in sorted(path.rglob('script_*.log'))])
 return analyze([path.read_text(encoding='utf8',errors='replace')])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('logs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();report=load(a.logs);text=json.dumps(report,indent=2)
 if a.output:a.output.write_text(text+'\n')
 print(text)
