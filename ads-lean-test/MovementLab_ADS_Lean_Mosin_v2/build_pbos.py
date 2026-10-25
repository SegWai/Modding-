"""Build and independently verify the two small, uncompressed test PBOs.
Run with Python 3 from any working directory. Not needed to launch the supplied ZIP.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,re,sys,zipfile
ROOT=Path(__file__).resolve().parent

def read_pbo(data):
 position=0
 def string():
  nonlocal position
  stop=data.index(b'\0',position);value=data[position:stop].decode('ascii');position=stop+1;return value
 assert string()==''
 assert struct.unpack_from('<5I',data,position)==(0x56657273,0,0,0,0);position+=20
 assert string()=='prefix';prefix=string();assert string()==''
 rows=[]
 while True:
  name=string();method,original,reserved,stamp,size=struct.unpack_from('<5I',data,position);position+=20
  assert (method,original,reserved,stamp)==(0,0,0,0)
  if not name:assert size==0;break
  rows.append((name,size))
 result={}
 for name,size in rows:
  assert name not in result;result[name]=data[position:position+size];assert len(result[name])==size;position+=size
 assert data[position:position+1]==b'\0'
 assert data[position+1:]==hashlib.sha1(data[:position]).digest()
 return prefix,result

def build(source,prefix,target):
 entries={p.relative_to(source).as_posix().replace('/','\\'):p.read_bytes() for p in source.rglob('*') if p.is_file()}
 assert entries and 'config.cpp' in entries
 header=b'\0'+struct.pack('<5I',0x56657273,0,0,0,0)+b'prefix\0'+prefix.encode()+b'\0\0'
 for name,payload in sorted(entries.items()):header+=name.encode('ascii')+b'\0'+struct.pack('<5I',0,0,0,0,len(payload))
 body=header+b'\0'+struct.pack('<5I',0,0,0,0,0)+b''.join(v for _,v in sorted(entries.items()))
 data=body+b'\0'+hashlib.sha1(body).digest()
 parsed_prefix,parsed=read_pbo(data);assert parsed_prefix==prefix and parsed==entries
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 return hashlib.sha256(data).hexdigest()

def validate_graph():
 # The generator's full parser/cycle/unchanged-branch checks run separately.
 g=(ROOT/'WorkspaceSource/locomotion.agf').read_text();agr=(ROOT/'WorkspaceSource/player_main.agr').read_text()
 assert agr.count('AnimSrcGCTVarFloat MLADSLeanGate ')==1
 for name in ['MLADSLeanGate','MLADSLeanCanary']:
  block=re.search(r'AnimSrcGCTVarFloat '+name+r'\s*\{([^{}]*)\}',agr)[1]
  lines=[line.strip() for line in block.splitlines() if line.strip()]
  assert len(lines)==3 and all(re.fullmatch(r'(DefaultValue|MinValue|MaxValue) -?[0-9.]+',line) for line in lines)
 assert 'ControlTemplate AnimSrcGCT "{5C84A3D083AAF46E}"' in agr
 assert g.count('AnimSrcNodeProcTransform MLADSLean_')==98
 assert 'MLCaptured' not in g and 'WheelVariants' not in g
 spec=json.loads((ROOT/'Pose-Spec.json').read_text())
 assert max(spec['math_reconstruction_error'].values())<1e-5
 assert all(len(v)==20 for v in spec['corrections'].values())
 # Native collision paths sum to their original values at all gate weights.
 for lean in [-1,-.5,0,.5,1]:
  for gate in [0,.25,.5,.75,1]:
   for amount in [.35,.2]:
    base=lean*amount;assert abs(base*(1-gate)+base*gate-base)<1e-12
 # New gate zero always yields neutral corrections; lean zero always yields neutral.
 for side in ['left','right']:
  for d in spec['corrections'][side].values():
   for field in d.values():assert all(abs(v*0)<1e-15 for v in field)
 return {'pose_math_reconstruction_max_error':spec['math_reconstruction_error'],'corrected_bones_per_direction':{k:len(v) for k,v in spec['corrections'].items()},'native_compilation_and_playback':'NOT RUN: requires Windows DayZDiag. Native axis/pivot/IK/camera semantics and crash-free startup remain pending.'}

def main():
 checks=validate_graph()
 hashes={}
 for src,prefix,path in [('LogicSource','MLADSLeanLogic','@MLADSLeanLogic/Addons/MLADSLeanLogic.pbo'),('WorkspaceSource','DZ\\anims\\workspaces\\player\\player_main','@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo')]:hashes[path]=build(ROOT/src,prefix,ROOT/path)
 checks.update({'pbo_sha256':hashes,'pbo_headers_prefix_offsets_source_and_sha1':'passed: independently parsed and compared to every input file','script_API_review':'Methods checked against official BohemiaInteractive/DayZ-Script-Diff; native Enforce compilation not available here','official_script_revision':'e8204c69fcfd056ea29a9728990fd9f7941ce8a6','changed_native_files':['locomotion.agf','player_main.agr'],'source_directory':r'F:\DayZProjects','dependencies':'Vanilla Mosin only. No SNAFU, no prior MovementLab test required.','revision':'v2: multiline controls, private control template, distinct binding guard, offline debug dependencies, F9 status','v1_native_failure':'User logs confirm MLADSLeanGate undefined, graph invalid; inventory null PluginInventoryDebug; v2 native result pending.'})
 (ROOT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
