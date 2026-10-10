#!/usr/bin/env python3
"""Reproducibly package the standalone offline native movement experiment."""
from pathlib import Path
import hashlib
import json
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "movement-logic-test" / "MovementLabMovementLogicTest"
OUTPUT = ROOT / "artifacts" / "MovementLab_Movement_Logic_Test_v11.zip"
ARCHIVE_ROOT = "MovementLabMovementLogicTest_v11"
VALIDATION_EXTRA = {}


def build_start_gate_pbo():
    """Store uncompressed config/scripts in a standard PBO with prefix and SHA1."""
    source = SOURCE / "StartGateSource"
    files = {p.relative_to(source).as_posix().replace("/", "\\"): p.read_bytes()
             for p in source.rglob("*") if p.is_file()}
    header = b"\0" + struct.pack("<5I", 0x56657273, 0, 0, 0, 0)
    header += b"prefix\0MovementLabStartGate\0\0"
    payload = b""
    for name, data in sorted(files.items()):
        header += name.encode("ascii") + b"\0" + struct.pack("<5I", 0, 0, 0, 0, len(data))
        payload += data
    body = header + b"\0" + struct.pack("<5I", 0, 0, 0, 0, 0) + payload
    result = body + b"\0" + hashlib.sha1(body).digest()
    # Independently parse headers, metadata and offsets and compare every file.
    offset = 0
    def string():
        nonlocal offset
        end = result.index(b"\0", offset)
        value = result[offset:end].decode("ascii")
        offset = end + 1
        return value
    assert string() == ""
    assert struct.unpack_from("<5I", result, offset)[0] == 0x56657273
    offset += 20
    assert string() == "prefix" and string() == "MovementLabStartGate" and string() == ""
    records = []
    while True:
        name = string()
        method, original, reserved, stamp, size = struct.unpack_from("<5I", result, offset)
        offset += 20
        assert (method, original, reserved, stamp) == (0, 0, 0, 0)
        if not name:
            assert size == 0
            break
        records.append((name, size))
    assert len(records) == len(files)
    for name, size in records:
        assert result[offset:offset+size] == files[name]
        offset += size
    assert result[offset] == 0 and result[offset+1:] == hashlib.sha1(result[:offset]).digest()
    target = SOURCE / "@MovementLabStartGate/Addons/MovementLabStartGate.pbo"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(result)
    return target


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
    assert "-mod=%movementlabTestDir%@MovementLabStartGate" in launcher
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
        "prior_v9_runtime": "user observed one jog frame before walking: mission OnUpdate applied too late",
        "prior_v10_runtime": "user confirmed command-level walking start works; stop deadline approved",
        "starting_v11": "approved v10 command hook/PBO retained",
        "braking_v11": "near/full sprint full-stop envelope redistributed to longer jogging and shorter walk; duration/deadline formulas unchanged; native playback pending",
        "pbo_validation": "uncompressed headers/prefix/file offsets/source bytes and SHA1 footer verified; native loading/compilation pending",
        "ordinary_acceleration": "new short idle walk-to-jog lead-in; native sprint handoff",
    }
    validation.update(VALIDATION_EXTRA)
    build_start_gate_pbo()
    OUTPUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        entries = {p.relative_to(SOURCE).as_posix(): p.read_bytes()
                   for p in SOURCE.rglob("*") if p.is_file()}
        entries["validation.json"] = (json.dumps(validation, indent=2) + "\n").encode()
        for name, data in sorted(entries.items()):
            if name.endswith((".cmd", ".txt")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            info = zipfile.ZipInfo(ARCHIVE_ROOT + "/" + name, (2026, 10, 10, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert len(names) == len(set(names))
        assert all(".." not in Path(name).parts for name in names)
        assert len(names) == len(entries)
    print(f"{OUTPUT.name}: {OUTPUT.stat().st_size} bytes")
    print("SHA256 " + hashlib.sha256(OUTPUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
