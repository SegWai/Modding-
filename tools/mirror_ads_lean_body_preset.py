"""Mirror F7 model-axis additive offsets. Does not mirror the underlying base animation."""
import argparse,json,math
from pathlib import Path
FIELDS=('X','Y','Z','Pitch','Yaw','Roll')
def opposite(name):
 if name.startswith('Left'):return 'Right'+name[4:]
 if name.startswith('Right'):return 'Left'+name[5:]
 return name

def mirror(data):
 parts=data.get('Parts');assert isinstance(parts,list) and parts,'Missing Parts'
 by_name={p['BoneName']:p for p in parts};assert len(by_name)==len(parts),'Duplicate bones'
 output=[]
 for slot in parts:
  name=slot['BoneName'];source=by_name[opposite(name)];part={'BoneName':name}
  for field in FIELDS:
   value=source[field];assert isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
   assert abs(value)<=(15 if field in ('X','Y','Z') else 45),'Out of editor range'
   value=-value if field in ('X','Yaw','Roll') else value
   part[field]=0.0 if value==0 else value
  output.append(part)
 return {'Parts':output}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
 data=json.loads(args.source.read_text());result=mirror(data);assert mirror(result)==data
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=4)+'\n')
 print('Mirrored',len(result['Parts']),'parts; side swaps and reflection signs verified reversible.')
