#!/usr/bin/env python3
"""Package a separate native-inventory appearance addon plus complete offline test."""
from pathlib import Path
import hashlib, struct, sys, zipfile
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'inventory-ui-test/MovementLabTABInventoryTest_v1'

def inventory_pbo():
    folder=SOURCE/'InventoryUISource'
    files={p.relative_to(folder).as_posix().replace('/','\\'):p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    header=b'\0'+struct.pack('<5I',0x56657273,0,0,0,0)+b'prefix\0MovementLabInventoryUI\0\0'
    payload=bytearray()
    for name,data in sorted(files.items()):
        header+=name.encode('ascii')+b'\0'+struct.pack('<5I',0,0,0,0,len(data));payload+=data
    body=header+b'\0'+bytes(20)+payload
    output=body+b'\0'+hashlib.sha1(body).digest()
    # Independently read every header, offset and source entry, then verify footer.
    at=0
    def string():
        nonlocal at
        end=output.index(b'\0',at);s=output[at:end].decode('ascii');at=end+1;return s
    assert string()=='';assert struct.unpack_from('<5I',output,at)[0]==0x56657273;at+=20
    assert string()=='prefix' and string()=='MovementLabInventoryUI' and string()==''
    entries=[]
    while True:
        name=string();method,original,reserved,stamp,size=struct.unpack_from('<5I',output,at);at+=20
        assert (method,original,reserved,stamp)==(0,0,0,0)
        if not name:break
        entries.append((name,size))
    for name,size in entries:assert output[at:at+size]==files[name];at+=size
    assert output[at:]==b'\0'+hashlib.sha1(output[:at]).digest()
    target=SOURCE/'@MovementLabInventoryUI/Addons/MovementLabInventoryUI.pbo'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(output)
    return hashlib.sha256(output).hexdigest()

if __name__=='__main__':
    sha=inventory_pbo()
    packer.SOURCE=SOURCE
    packer.OUTPUT=ROOT/'artifacts/MovementLab_TAB_Inventory_Test_v1.zip'
    packer.ARCHIVE_ROOT=SOURCE.name
    packer.VALIDATION_EXTRA={
      'variant':'separate Mission-only reference-style native TAB inventory skin; existing HUDv2/movement/SNAFU demo preserved',
      'checks':'native signatures/API references; actual skin logic in C++ GUI mocks; drop-grid-origin consistency; readonly gameplay files; two PAA resources; independent inventory-PBO parse/footer',
      'inventory_pbo_sha256':sha,
      'limitations':'Preview is a concept, not a native screenshot. Native Enforce compilation/rendering and drag/drop/collapse/scroll need DayZDiag testing. Original DayZ center/vicinity/quickbar positioning remains; theme focuses on cargo/header panels. Sidebar falls back on narrow or spacer-owned geometry. No original native GUI layouts available in cloud; exact pixel match not established.'}
    packer.main()
    with zipfile.ZipFile(ROOT/'artifacts/MovementLab_TAB_Inventory_Mod_v1.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for folder in ('@MovementLabInventoryUI','InventoryUISource'):
            for p in sorted((SOURCE/folder).rglob('*')):
                if p.is_file():z.write(p,'MovementLabInventoryUI/'+p.relative_to(SOURCE).as_posix())
        z.write(SOURCE/'README-Inventory-Mod.txt','MovementLabInventoryUI/README.txt')
        z.write(SOURCE/'TAB-Inventory-Preview.png','MovementLabInventoryUI/TAB-Inventory-Preview.png')
    print('Standalone inventory mod ZIP also built; native load/playtest pending.')
