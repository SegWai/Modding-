#!/usr/bin/env python3
"""Reproducibly package the standalone offline native movement experiment."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "movement-logic-test" / "MovementLabMovementLogicTest"
OUTPUT = ROOT / "artifacts" / "MovementLab_Movement_Logic_Test_v9.zip"


def main():
    mission = (SOURCE / "Missions/MovementLabMovementLogic.ChernarusPlus/init.c").read_text()
    launcher = (SOURCE / "Launch-Movement-Test.cmd").read_text()
    setters = ["SetRunSprintFilterModifier", "SetDirectionFilterModifier",
               "SetDirectionSprintFilterModifier", "SetTurnSpanModifier",
               "SetTurnSpanSprintModifier"]
    for setter in setters:
        assert setter in mission
    assert "KC_F7" in mission and "OnMissionFinish" in mission
    assert "HumanInputControllerOverrideType.ONE_FRAME" in mission
    assert "HumanInputControllerOverrideType.DISABLED" in mission
    assert "MovementLabCancelBrake();" in mission
    assert "SetPosition(" not in mission and "SetVelocity(" not in mission
    assert "-mod=" not in launcher
    assert "MovementLabMovementLogic.ChernarusPlus" in launcher
    validation = {
        "checks": "Package structure and static API/source inspection only",
        "native_compile_and_playtest": "pending user local DayZ 1.29 test",
        "official_script_revision": "86974a0f5bd16b1ee3e334ad828133c93dca80a1",
        "native_setters": setters,
        "prior_v1_runtime": "user confirmed heavier movement, unchanged animations and near-instant sprint release stopping",
        "prior_v2_runtime": "user liked startup but full sprint stop was still too fast",
        "prior_v3_runtime": "too much near-sprint time; brief Shift taps could receive full-sprint stop",
        "prior_v4_runtime": "user confirmed forward braking is perfect; diagonal stops faster",
        "prior_v5_runtime": "user approved forward and diagonal sprint braking",
        "prior_v6_runtime": "user approved jogging stop; pure A/D stop finished with forward walking animation",
        "prior_v7_runtime": "user approved sideways walking finish; requested a shorter backward walk finish",
        "prior_v8_runtime": "user approved quick backward walking finish",
        "starting_v9": "from idle: 0.10s walk, 0.18s smooth walk-to-jog, 0.07s jog lead-in; handoff to native sprint if held/allowed; native playback pending",
        "braking_v9": "v8 stopping formulas/directions retained; actual startup speed caps release sampling",
        "ordinary_acceleration": "new short idle walk-to-jog lead-in; native sprint handoff",
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        entries = {p.relative_to(SOURCE).as_posix(): p.read_bytes()
                   for p in SOURCE.rglob("*") if p.is_file()}
        entries["validation.json"] = (json.dumps(validation, indent=2) + "\n").encode()
        for name, data in sorted(entries.items()):
            if name.endswith((".cmd", ".txt")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            info = zipfile.ZipInfo("MovementLabMovementLogicTest_v9/" + name, (2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert all(".." not in Path(name).parts for name in names)
        assert len(names) == 5
    print(f"{OUTPUT.name}: {OUTPUT.stat().st_size} bytes")
    print("SHA256 " + hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
