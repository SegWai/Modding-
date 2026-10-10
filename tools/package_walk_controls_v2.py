#!/usr/bin/env python3
"""Package walking-first controls without altering the stable v11 build."""
from pathlib import Path
import hashlib, json, zipfile, sys
sys.dont_write_bytecode = True
import package_movement_logic_test as pbo
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'movement-controls-test/MovementLabWalkControlsTest_v2'
OUTPUT=ROOT/'artifacts/MovementLab_Walk_Controls_v2.zip'
PREFIX='MovementLabWalkControlsTest_v2/'

def main():
    script=(SOURCE/'StartGateSource/Scripts/4_World/MovementLabStartGate.c').read_text()
    mission=(SOURCE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_text()
    launcher=(SOURCE/'Launch-Movement-Test.cmd').read_text()
    assert 'MovementLabControls.Update(' in script
    assert 'HumanInputControllerOverrideType.ENABLED' in script
    assert 'HumanInputControllerOverrideType.DISABLED' in script
    assert 'Clock - LastTap <= 0.30' in script
    assert 'KC_F7' in mission and 'OnMissionFinish' in mission
    assert 'MovementLabUpdateBrake(' not in mission
    assert '-mod=%movementlabTestDir%@MovementLabStartGate' in launcher
    assert 'MovementLabMovementLogic.ChernarusPlus' in launcher
    pbo.SOURCE=SOURCE
    pbo.build_start_gate_pbo()
    entries={p.relative_to(SOURCE).as_posix():p.read_bytes() for p in SOURCE.rglob('*') if p.is_file()}
    entries['validation.json']=(json.dumps({
        'variant':'Walking-first controls v2, separate stable v11 derivative',
        'controls':'WASD walk; Shift hold jog; double-tap Shift sprint latch until movement release',
        'tap_window_seconds':0.30,
        'mocked_checks':'actual controller/integration at 30/60/144 FPS, staged startup, v11 stop budgets, smooth coast resume and directional overlap',
        'restored_logic':'v11 walk/jog lead-in, same full-sprint forward/diagonal deadlines, side/backward finishes and native heavy filters',
        'native_compile_and_animation_test':'pending local DayZ test',
        'pbo':'source/header/prefix/payload/SHA1 footer verified',
        'native_assets':'none bundled',
    },indent=2)+'\n').encode()
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(entries.items()):
            if name.endswith(('.cmd','.txt')):data=data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
            info=zipfile.ZipInfo(PREFIX+name,(2026,10,10,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))==len(entries)
    print(OUTPUT.name,OUTPUT.stat().st_size,'bytes; SHA256',hashlib.sha256(OUTPUT.read_bytes()).hexdigest())
if __name__=='__main__':main()
