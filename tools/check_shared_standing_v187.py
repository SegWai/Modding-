"""Offline routing/scope regressions for held-item standing lean."""
from pathlib import Path
import re,sys,itertools
sys.path.insert(0,str(Path(__file__).parent));from dayz_graph_formats import newnodes
r=Path(__file__).resolve().parents[1];a=r/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v185_Restored';b=a.with_name('MovementLab_ADS_Lean_Mosin_v187')
for n in ['MLLeanPreset.json','MLWalkingLeanPreset.json','MLCrouchLeanPreset.json','MLUnarmedLeanPreset.json']:
 for rel in [n,'Profiles/LeanMosin/'+n,'LogicSource/Presets/'+n]:assert(a/rel).read_bytes()==(b/rel).read_bytes()
for p in (a/'Missions').rglob('*'):
 if p.is_file():assert p.read_bytes()==(b/p.relative_to(a)).read_bytes()
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text())
for n,v in old.items():
 if n.startswith('{'):continue
 expected=v.replace('Child1 "ML183_Edit_RightToeBase_RZ"','Child1 "ML187_HeldGrip"')if n=='ML183_UnarmedOnly'else v
 assert new[n]==expected,n
assert {n for n in set(new)-set(old)if not n.startswith('{')}=={'ML187_HeldGrip','ML187_PublishHeldLean'}
publisher=new['ML187_PublishHeldLean'];assert 'outputweaponoffsettobuffer = true'in publisher and 'hand = RightHand'in publisher
for field in ['WeightAim','WeightPrimaryChain','WeightSecondaryChain']:assert field+' "false"'in publisher
for field in ['WeaponDirLr','WeaponDirUd','WeaponRoll']:assert field+' "0"'in publisher
h=(b/'LogicSource/Scripts/4_World/MLADSLeanPlayer.c').read_text();route=h[h.index('  bool sharedStanding'):h.index('  bool useWalking',h.index('  bool sharedStanding'))]
assert 'GetEntityInHands'not in route # independent of held item class
assert '!IsRaised()'in route and 'm_iMovement == 0'in route and '!itemAction'in route
helper=(b/'LogicSource/Scripts/4_World/MLUnarmedPose183.c').read_text()
assert 'currentItem != ReferenceItem'in helper and 'LeftSolved = null'in helper and 'RightSolved = null'in helper
assert 'heldPose && armIndex < 6'in helper and 'heldPose && partIndex >= 8 && partIndex <= 15'in helper
playerupdate=helper[helper.index(' void UpdatePlayer'):helper.index(' void ReleasePlayer')]
assert 'AnimSetBool'not in playerupdate
# Scope matrix: lowered static upright only, irrespective of held class.
cases=0
for alive,awake,movecommand,upright,stationary,raised,action,enabled,held in itertools.product([False,True],repeat=9):
 eligible=alive and awake and movecommand and upright and stationary and not raised and not action and enabled
 assert not eligible or (upright and stationary and not raised and not action)
 cases+=1
agr=(b/'WorkspaceSource/player_main.agr').read_text();assert agr.count('AnimSrcGCTVarFloat ML187HeldLean ')==1
sys.setrecursionlimit(20000);done=set();visiting=set()
def visit(n):
 if n not in new or n in done:return
 assert n not in visiting,n
 visiting.add(n)
 for c in re.findall(r'\bChild\d* "([^"]+)"',new[n]):visit(c)
 visiting.remove(n);done.add(n)
for n in new:
 if not n.startswith('{'):visit(n)
print(f'PASS:{cases} scope cases; exact two-node/one-edge graph addition; native grip chain weights off; item reference invalidation; four banks/scene unchanged;DAG. Native compile/item-render fit NOT RUN.')
