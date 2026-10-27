"""Check firearm-category routing, handgun grip isolation, and preserved body nodes."""
from pathlib import Path
import re,json,sys
from dayz_graph_formats import newnodes
root=Path(__file__).resolve().parents[1];a=root/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v105';b=root/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v106'
old=newnodes((a/'WorkspaceSource/locomotion.agf').read_text());new=newnodes((b/'WorkspaceSource/locomotion.agf').read_text());changed=[];arms=[];body=[]
for name,node in old.items():
 if name.startswith('{'):continue
 expected=node
 if name.startswith('ML'):
  if node.startswith('AnimSrcNodeProcTransform'):
   bones=re.findall(r'\bBone "([^"]+)"',node)
   if any(re.search(r'(?:Arm|Hand|Shoulder|Finger)',bone) for bone in bones):
    assert all(re.search(r'(?:Arm|Hand|Shoulder|Finger)',bone) for bone in bones)
    expected=re.sub(r'Expression "([^"]+)"',lambda m:'Expression "('+m[1]+')*ML106ShoulderedGrip"',expected);arms.append(name)
   else:body.append(name)
  if node.startswith('AnimSrcNodeWeaponIk'):
   expected=re.sub(r'(Weight(?:Aim|PrimaryChain|SecondaryChain)) "([^"]+)"',lambda m:m[1]+' "('+m[2]+') && (ML106ShoulderedGrip > 0.5)"' if m[2]!='false' else m[0],expected)
  if name in ['ML37_RightElbowBlend','ML51_StandingLeftElbowOnly','ML104_LeftElbowDirections']:
   expected=re.sub(r'BlendWeight "([^"]+)"',lambda m:'BlendWeight "('+m[1]+')*ML106ShoulderedGrip"',expected)
 assert new[name]==expected,name
 if expected!=node:changed.append(name)
assert len(arms)>900 and len(body)>100
# Handgun factor 0 zeros rifle-only arm operations, while body transforms remain
# byte-identical. Shouldered factor 1 preserves every prior numerical coefficient.
for name in arms:
 expression=re.search(r'Expression "([^"]+)"',new[name])[1]
 assert expression.endswith('*ML106ShoulderedGrip')
for name in body:assert new[name]==old[name]
assert set(new)==set(old)
agr=(b/'WorkspaceSource/player_main.agr').read_text();assert agr.count('AnimSrcGCTVarFloat ML106ShoulderedGrip {')==1
assert 'MLADSLeanLocomotion_v106.agf' in agr and 'MLADSLeanLocomotion_v104.agf' not in agr
world=b/'LogicSource/Scripts/4_World';player=(world/'MLADSLeanPlayer.c').read_text();camera=(world/'MLADSLeanCamera.c').read_text();support=(world/'MLADSLeanWeaponSupport106.c').read_text()
for source in [player,camera,support]:
 assert 'IsKindOf("AK74")' not in source and 'IsKindOf("Mosin9130")' not in source
assert 'Weapon_Base.Cast(item)' in support and 'GetMuzzleCount()' in support
assert '"Pistol_Base"' in support and '"Magnum_Base"' in support and '"PistolCore"' in support
assert '"Archery_Base"' in support
assert 'MLADSLeanWeaponSupport106.Profile(held)' in player
assert 'MLADSLeanWeaponSupport106.Supported(weapon)' in camera
assert 'm_ML106ProfileVar >= 0' in player
for match in re.finditer(r'AnimSetFloat\(m_ML106ProfileVar',player):
 assert player.index('super.CommandHandler(')<match.start()<player.index(' // Read-only camera weight')
assert 'm_ML106ProfileVar != m_ML104PoleVars[poleIndex]' in player
assert 'if (m_ML106Profile != 1)' in player
assert 'm_ML104PoleWeapon = null;' in player
# Category gating never adds firearm/FSM/input or item-profile overrides.
assert 'AddItemInHandsProfile' not in support and 'OverrideRaise' not in support
assert (a/'LogicSource/Scripts/4_World/MLADSLeanRangeAmmo.c').read_bytes()==(world/'MLADSLeanRangeAmmo.c').read_bytes()
assert (a/'LogicSource/Scripts/4_World/MLADSLeanPanacea104.c').read_bytes()==(world/'MLADSLeanPanacea104.c').read_bytes()
# Actual SDK inheritance checks show why a Rifle_Base-only test is insufficient:
# bolt-action rifles, revolvers and pistols can derive straight from Weapon_Base.
sdk=Path('/tmp/dayz-lean-sdk/scripts/4_world/entities/firearms');parents={}
for p in sdk.rglob('*.c'):
 for cls,parent in re.findall(r'\bclass\s+(\w+)\s*(?:extends|:)\s*(\w+)',p.read_text(errors='replace')):parents[cls]=parent
for cls in ['M4A1_Base','Mosin9130','Magnum_Base','Pistol_Base','MP5K_Base']:
 lineage=[];current=cls
 while current != 'Weapon_Base' and current in parents and current not in lineage:lineage.append(current);current=parents[current]
 assert current=='Weapon_Base',(cls,lineage,current)
print(f'PASS: {len(arms)} rifle arm nodes masked for handguns; {len(body)} custom body nodes unchanged; all old graph nodes accounted for; category paths/name-check removal/SDK ancestry and binding isolation checked. Native compile/render/firing untested.')
