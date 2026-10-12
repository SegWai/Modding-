from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'ctrl-mode-test/MovementLabArmedSpeeds_v13'
ORIGINAL=Path('/tmp/player-main-upload/player_main')
plan=json.loads((SOURCE/'Armed-Speed-Plan.json').read_text())
variants={'DZ/anims/anm/player/moves/unarmed/'+v['output']:v for v in plan['variants']}
files={p.relative_to(ORIGINAL).as_posix().lower():p for p in ORIGINAL.rglob('*.asi')}
def clean(s):return re.sub(r'^\{[^}]+\}','',s).lower()
def rows(p):
 s=p.read_text(errors='replace');tail=s.split('$animations',1)[-1]
 return dict(re.findall(r'"([^"\n]+)"\s+"([^"\n]+)"',tail))
patched={k:rows(p) for k,p in files.items()}
for item in plan['instances']:
 p=files[item['file'].lower()];original=rows(p)
 for key,value in item['add'].items():
  tokens=key.split('.');native='Locomotion.'+('Cro' if tokens[0]=='ZZMovementLabCrouchSpeeds' else 'Erc')+'.'+tokens[2]
  assert native in original,(p,key)
  if value in variants:assert clean(variants[value]['source'])==clean(original[native])
  else:assert value==original[native]
 for key,value in item['replace'].items():
  assert re.fullmatch(r'Locomotion.Cro.Walk(?:B|BL|BR|F|FL|FR)',key)
  assert variants[value]['fps']==9
 patched[item['file'].lower()].update(item['add']);patched[item['file'].lower()].update(item['replace'])
# Prove every applicable child inherits the new rows, including individual weapons.
def effective(key,stack=()):
 assert key not in stack
 s=files[key].read_text(errors='replace');out={}
 for parent in re.findall(r'#parent "([^"]+)"',s):
  raw=clean(parent);prefix='dz/anims/workspaces/player/player_main/'
  assert raw.startswith(prefix),(key,parent)
  out.update(effective(raw[len(prefix):],stack+(key,)))
 out.update(patched[key]);return out
count=0
for key,p in files.items():
 if 'player_main.ast' not in p.read_text(errors='replace').split('$animations')[0]:continue
 eff=effective(key)
 for group in ['Cro','Erc']:
  for native,value in eff.items():
   if not native.startswith('Locomotion.'+group+'.'):continue
   slot=native.rsplit('.',1)[-1]
   custom=('ZZMovementLabCrouchSpeeds.L2.' if group=='Cro' else 'ZZMovementLabStandingWalk.L1J2.')+slot
   if custom not in eff:continue
   actual=eff[custom]
   if actual in variants:
    assert clean(variants[actual]['source'])==clean(variants[value]['source'] if value in variants else value),(key,native)
   else:assert actual==value,(key,native,actual,value)
 count+=1
old=ROOT/'ctrl-mode-test/MovementLabCamera_Loadout_v11'
assert (SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_bytes()==(old/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_bytes()
assert (SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()==(old/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes()
print(f'{count} inherited instances checked, {len(plan["instances"])} override providers, {len(variants)} source-specific clip variants; original weapon mappings preserved. Native preparation/playback pending.')

import struct
clips=[Path('/workspace/attachments/e44835eb-ffcd-4e5b-a1a9-184dcd8a8593/p_sur_erc_walkb.anm'),Path('/workspace/attachments/d8337ae6-7dd3-447d-95fb-a0d800ada321/p_cro_walkf.anm')]
for clip in clips:
 data=clip.read_bytes()
 assert data[:4]==b'FORM' and data[8:16] in [b'ANIMSET5',b'ANIMSET6']
 assert data[20:24]==b'FPS\0' and struct.unpack_from('>I',data,24)[0]==4
 assert struct.unpack_from('<I',data,28)[0]==30
 for fps in [9,14,18,22,24,26,30]:
  retimed=bytearray(data);struct.pack_into('<I',retimed,28,fps)
  assert retimed[:28]==data[:28] and retimed[32:]==data[32:]
  assert struct.unpack_from('<I',retimed,28)[0]==fps
 print(clip.name,data[8:16].decode(),'verified; only FPS bytes change')
prior=ROOT/'ctrl-mode-test/MovementLabArmedSpeeds_v12'
assert (SOURCE/'Armed-Speed-Plan.json').read_bytes()==(prior/'Armed-Speed-Plan.json').read_bytes()
