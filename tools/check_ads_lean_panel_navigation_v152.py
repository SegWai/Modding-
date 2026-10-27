"""Offline source contracts and focus lifecycle state-machine checks; no native UI."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];KIT=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v152';BASE=ROOT/'ads-lean-test/MovementLab_ADS_Lean_Mosin_v151'
helper=(KIT/'LogicSource/Scripts/5_Mission/MLPanelNavigation152.c').read_text()
assert 'ResetGameFocus(' not in helper and 'DisableSimulation(' not in helper and 'SetActive(' not in helper
assert 'GetMouseState(MouseState.RIGHT)' in helper and '0x80000000' in helper
assert 'm_Menu.UnlockControls();' in helper and 'm_Menu.LockControls();' in helper
assert 'if (m_Active || !m_Menu || !GetGame().IsAppActive())' in helper
assert 'if (!m_Active || !m_Menu)' in helper
assert helper.index('  End();',helper.index(' void Hide()'))<helper.index('  m_Menu = null;')
for name in ['MLPoseEditorMenu144.c','MLBodyMenu149.c']:
 s=(KIT/'LogicSource/Scripts/5_Mission'/name).read_text()
 assert 'm_Navigation.Show(this);' in s and 'm_Navigation.Hide();' in s and 'm_Navigation.Tick();' in s
 assert s.index('m_Navigation.Hide();')<s.index('super.OnHide();')
 assert 'OnMouseButtonDown' in s and 'OnMouseButtonUp' in s and 'OnVisibilityChanged' in s
 assert 'if (button != MouseState.LEFT)' in s and 'm_Navigation.IsActive()' in s
for p in (BASE/'LogicSource/Scripts/4_World').glob('*.c'):assert p.read_bytes()==(KIT/p.relative_to(BASE)).read_bytes(),p
assert (BASE/'WorkspaceSource/locomotion.agf').read_bytes()==(KIT/'WorkspaceSource/locomotion.agf').read_bytes()
for p in (KIT/'LogicSource').rglob('*.c'):
 s=p.read_text();assert s.count('{')==s.count('}'),p
 for m in re.finditer(r'(?:array<float>|TStringArray) \w+ = \{([^\n]+)\}',s):assert m[1].count(',')<8,p
# Independent focus accounting for normal release, missed UI release/polling,
# repeated events, focus loss, closing while held, switching while held.
class Panel:
 def __init__(self):self.focus=1;self.active=False;self.closed=False
 def begin(self):
  if self.active or self.closed:return
  self.focus-=1;self.active=True
 def end(self):
  if not self.active or self.closed:return
  self.focus+=1;self.active=False
 def poll(self,held,foreground=True):
  if held and foreground:self.begin()
  else:self.end()
 def hide(self):
  self.end();self.focus-=1;self.closed=True
for events in [['down','up','hide'],['down','pollup','hide'],['down','down','up','up','hide'],['down','blur','hide'],['down','hide'],['hide'],['down','up','down','hide']]:
 p=Panel()
 for e in events:
  if e=='down':p.begin()
  elif e=='up':p.end()
  elif e=='pollup':p.poll(False)
  elif e=='blur':p.poll(True,False)
  elif e=='hide':p.hide()
  assert p.focus>=0
 assert p.focus==0 and p.closed
# Simulate switching: first menu regains its temporary lock before base hide;
# new menu receives its own single focus lock, which is released on close.
old=Panel();old.begin();new=Panel();old.hide();assert old.focus==0 and new.focus==1;new.begin();new.hide();assert new.focus==0
print(json.dumps({'focus_lifecycle_cases':8,'both_menus':'mouse+keyboard/gamepad focus borrowed only while physical RMB held; polling restores after missed UI release; hide/visibility balanced','preserved':'World scripts, poses, graph, actual camera implementation, freeze, live controls and smoothing unchanged','native_compile_UI_navigation':'NOT RUN; test Windows first/third/free-camera RMB+WASD and release'},indent=2))
