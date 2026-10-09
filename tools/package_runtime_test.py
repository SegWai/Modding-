#!/usr/bin/env python3
"""Package the offline test sources; the user's compiled ANM is copied locally."""
from pathlib import Path
import zipfile


def main():
    repo = Path(__file__).resolve().parents[1]
    source = repo / "runtime-test" / "MovementLabOfflineTest"
    output = repo / "artifacts" / "MovementLab_Offline_Test.zip"
    entries = {
        "MovementLabOfflineTest/" + str(path.relative_to(source)).replace("\\", "/"): path.read_bytes()
        for path in sorted(source.rglob("*")) if path.is_file()
    }
    # Preserve notices already shipped with the authored animation, without
    # depending on the untracked Blender export directory.
    with zipfile.ZipFile(repo / "artifacts" / "MovementLab_ArmLift_Test.zip") as authored:
        for name in ("ASSET_NOTICES.txt", "EXPORTER_LICENSE.txt"):
            entries["MovementLabOfflineTest/" + name] = authored.read(name)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            # CRLF for the Windows command files and plain-text guide.
            if name.endswith((".cmd", ".txt")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 9, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)

    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("The runtime test ZIP failed its integrity check")
    print(f"Packaged {len(entries)} files: {output.name} ({output.stat().st_size} bytes)")
    print("ANM and PBO are intentionally supplied by the Windows compile/pack steps.")


if __name__ == "__main__":
    main()
