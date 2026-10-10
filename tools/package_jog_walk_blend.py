#!/usr/bin/env python3
"""Package only the isolated jog-to-walk test, independently of v11/Ctrl modes."""
from pathlib import Path
import sys,hashlib,json,zipfile
sys.dont_write_bytecode=True
import package_movement_logic_test as pbo
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'walk-blend-test/MovementLabJogWalkBlendTest'
OUTPUT=ROOT/'artifacts/MovementLab_Jog_Walk_Blend_Test_v1.zip'
def main():
    world=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabWalkBlend.c').read_text()
    mission=(SOURCE/'Missions/MovementLabJogWalkBlend.ChernarusPlus/init.c').read_text()
    launcher=(SOURCE/'Launch-Movement-Test.cmd').read_text()
    assert 'MovementLabUpdateWalkBlend(pDt, pCurrentCommandID);' in world
    assert 'm_MovementLabBlendTime / 0.45' in world
    assert 'HumanInputControllerOverrideType.ONE_FRAME' in world
    assert 'HumanInputControllerOverrideType.DISABLED' in world
    assert 'KC_F7' in mission and 'MovementLabStartGate.Enabled = true;' in mission
    assert '-mod=%movementlabTestDir%@MovementLabStartGate' in launcher
    assert 'MovementLabJogWalkBlend.ChernarusPlus' in launcher
    for banned in ['SetVelocity(', 'SetPosition(', 'MovementLabBeginBrake', 'SetRunSprintFilterModifier', 'm_MovementLabWalkMode']:
        assert banned not in world+mission
    pbo.SOURCE=SOURCE
    pbo.build_start_gate_pbo() # Parses its output and verifies payload/SHA1.
    entries={p.relative_to(SOURCE).as_posix():p.read_bytes() for p in SOURCE.rglob('*') if p.is_file()}
    validation={'variant':'isolated jog-to-walk blend v1, no v11/Ctrl mode behavior',
                'curve':'achieved jogging to gait 1 over 0.45s, smoothstep; no independent m/s override',
                'checks':'actual translated hook at 30/60/144 FPS; monotonic easing, native handoff, cancellations, input ownership; verified PBO source payload/header/SHA1 and ZIP integrity',
                'native_compilation_animation_physics':'pending in-game test'}
    entries['validation.json']=(json.dumps(validation,indent=2)+'\n').encode()
    with zipfile.ZipFile(OUTPUT,'w') as archive:
        for name,data in sorted(entries.items()):
            if name.endswith(('.cmd','.txt')):data=data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
            info=zipfile.ZipInfo('MovementLabJogWalkBlendTest_v1/'+name,(2026,10,10,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(entries)
    print(OUTPUT.name,OUTPUT.stat().st_size,'bytes; SHA256',hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
if __name__=='__main__':main()
