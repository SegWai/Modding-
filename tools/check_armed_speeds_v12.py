from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'ctrl-mode-test/MovementLabArmedSpeeds_v12'
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
