from pathlib import Path
import shutil,sys,json
from psd_tools import PSDImage
from PIL import Image,ImageDraw
R=Path('/workspace/Modding-');B=R/'hud-icons-test/MovementLabHUDIcons_v2';S=R/'hud-icons-test/MovementLabPSDHUD_v1'
shutil.copytree(B,S,dirs_exist_ok=True)
sys.path.insert(0,str(R/'tools'))
from build_hud_icon_textures import paa
p=PSDImage.open('/workspace/attachments/758117cf-8fd4-4cd9-b4b7-537aab9763c0/Untitled-2.psd')
for l in p.descendants():l.visible=True
layers=list(p.descendants());out=S/'ImageSources/PSD';out.mkdir(exist_ok=True)
shutil.copyfile('/workspace/attachments/758117cf-8fd4-4cd9-b4b7-537aab9763c0/Untitled-2.psd',out/'Untitled-2.psd')
# Existing read-only HUD ids retained, plus prone idle/aim.
maprows=[(25,i+1) for i in range(4)]+[(31,0)]+[(33,i+1) for i in range(4)]+[(1,0),(23,0),(3,1),(3,2),(7,1),(7,2),(11,0),(31,0),(13,1),(13,2),(17,1),(17,2),(17,3),(21,0),(13,3),(45,0),(43,0),(41,0)]
for n,(li,count) in enumerate(maprows):
 a=layers[li].composite(force=True).convert('RGBA');a.save(out/f'layer_{li}.png')
 canvas=Image.new('RGBA',(600,330));canvas.paste(a,((420-a.width)//2,320-a.height))
 if count:
  bars=layers[{1:26,2:27,3:28,4:29}[count]].composite(force=True).convert('RGBA')
  canvas.paste(bars,(450+(140-bars.width)//2,320-bars.height))
 canvas.thumbnail((512,256),Image.Resampling.LANCZOS)
 fitted=Image.new('RGBA',(512,256));fitted.paste(canvas,((512-canvas.width)//2,(256-canvas.height)//2));canvas=fitted
 png=out/f'icon_{n:02}.png';canvas.save(png);paa(png,S/f'StartGateSource/GUI/Textures/icon_{n:02}.paa')
preview=Image.new('RGB',(1024,7*150),(45,45,45));d=ImageDraw.Draw(preview)
for n in range(27):
 a=Image.open(out/f'icon_{n:02}.png');a.thumbnail((256,128));x=(n%4)*256;y=(n//4)*150;preview.paste(a,(x,y),a);d.text((x+8,y+130),str(n),fill='white')
preview.save(R/'artifacts/MovementLab_PSD_HUD_Preview.png')
f=S/'StartGateSource/Scripts/5_Mission/MovementLabSpeedHUD.c';t=f.read_text()
t=t.replace('132, 104','70, 36').replace('iconIndex < 24','iconIndex < 27').replace('Count() == 24','Count() == 27').replace('speedIcon > 23','speedIcon > 26')
start=t.index('        m_MovementLabSpeedLabel =');end=t.index('        for (int iconIndex',start);t=t[:start]+t[end:]
start=t.index('            speedImage.SetPos(0, 0);');end=t.index('            string iconNumber',start)
t=t[:start]+'''            speedImage.SetPos(0, 0);
            speedImage.SetSize(70, 35);
            int expectedWidth = 512;
'''+t[end:]
t=t.replace('        if (speedIcon != m_MovementLabLastIcon)', '        HumanMovementState hudState = new HumanMovementState();\n        speedPlayer.GetMovementState(hudState);\n        if (speedMode == "AIM CROUCH" && hudState.m_iMovement == 0)\n            speedIcon = 26;\n        if (speedIcon != m_MovementLabLastIcon)')
start=t.index('        string speedLabel =');t=t[:start]+'''        // Anchor above the full native stamina strip, not its changing filled width.
        if (!m_Stamina)
            return;
        Widget speedAnchor = m_Stamina.GetParent();
        if (!speedAnchor)
            return;
        float speedX;
        float speedY;
        float speedW;
        float speedH;
        speedAnchor.GetScreenPos(speedX, speedY);
        speedAnchor.GetScreenSize(speedW, speedH);
        m_MovementLabSpeedRoot.SetScreenPos(speedX + speedW - 70, speedY - 38);
        // Native DisplayStance can re-show these every frame; hide after super.Update.
        m_StanceStand.Show(false);
        m_StanceStandWalk.Show(false);
        m_StanceCrouch.Show(false);
        m_StanceProne.Show(false);
    }
}
'''
# Keep native vehicle icon and HUD visibility rules. Custom prone now covers native prone.
f.write_text(t)
f=S/'StartGateSource/Scripts/4_World/MovementLabStartGate.c';t=f.read_text();t=t.replace('''        if (mode == "PRONE")
            return;''','''        if (mode == "PRONE")
        {
            icon = 24;
            if (IsRaised())
                icon = 25;
            return;
        }''',1);f.write_text(t)
(S/'README-PSD-HUD.txt').write_text('PSD indicator test. Native TAB retained. Movement and speeds unchanged. Exact supplied PSD silhouettes and line marks, 1-4 crouch walk, fast crouch unnumbered, aiming slow/fast1-3, crouch aim1-4, walking/jogging1-2. Prone supplied variants. No text captions. Positioned above right end of stamina strip. Native pedestrian stance images hidden only when custom HUD active; vehicle indicator retained. Native DayZ compilation and rendering must be tested locally. Launch from a fresh extracted folder.\n')
print(S)
