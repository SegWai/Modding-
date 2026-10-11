#!/usr/bin/env python3
"""Package explicit-FPS crouch clip retiming with stable controller unchanged."""
import sys,struct,hashlib,json
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_CrouchSlow_v3'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_Crouch_Slow_Test_v3.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={'variant':'stable v10 strafe v2 controller; six crouch walk clips FPS 30 to 6','physical_scaling':'removed; root-motion timing expected to slow naturally with playback','verified':'explicit FPS chunk and one byte per clip changed; PBO payload SHA1; controller identical to stable','native_compile_and_playtest':'pending; asset override loading and root motion rate require game test'}
def build_clips():
 source=packer.SOURCE/'CrouchClipSource'
 manifest=json.loads((packer.SOURCE/'Retiming_Validation.json').read_text())
 assert len(manifest)==6
 for row in manifest:
  data=(source/row['file']).read_bytes()
  assert data[20:28]==b'FPS\0\0\0\0\4' and struct.unpack_from('<I',data,28)[0]==6
  assert hashlib.sha256(data).hexdigest()==row['retimed_sha256']
  original=bytearray(data);struct.pack_into('<I',original,28,30)
  assert hashlib.sha256(original).hexdigest()==row['original_sha256']
 files={p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
 header=b'\0'+struct.pack('<5I',0x56657273,0,0,0,0)+b'prefix\0DZ\\anims\\anm\\player\\moves\\unarmed\0\0'
 for name,data in sorted(files.items()):header+=name.encode()+b'\0'+struct.pack('<5I',0,0,0,0,len(data))
 body=header+b'\0'+bytes(20)+b''.join(data for name,data in sorted(files.items()))
 result=body+b'\0'+hashlib.sha1(body).digest()
 offset=1+20
 def string():
  nonlocal offset
  end=result.index(b'\0',offset);value=result[offset:end];offset=end+1;return value
 assert string()==b'prefix' and string()==b'DZ\\anims\\anm\\player\\moves\\unarmed' and string()==b''
 records=[]
 while True:
  name=string();fields=struct.unpack_from('<5I',result,offset);offset+=20
  assert fields[:4]==(0,0,0,0)
  if not name:assert fields[4]==0;break
  records.append((name.decode(),fields[4]))
 for name,size in records:assert result[offset:offset+size]==files[name];offset+=size
 assert result[offset:]==b'\0'+hashlib.sha1(result[:offset]).digest()
 target=packer.SOURCE/'@MovementLabSlowCrouchClips/Addons/MovementLabSlowCrouchClips.pbo';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(result)
 stable=packer.ROOT/'ctrl-mode-test/MovementLabCtrlModeTest_v10_Strafe_v2'
 for path in ['StartGateSource/Scripts/4_World/MovementLabStartGate.c','Missions/MovementLabMovementLogic.ChernarusPlus/init.c']:
  assert (stable/path).read_bytes()==(packer.SOURCE/path).read_bytes()
 print('Six FPS chunks validated; all remaining clip bytes and stable controller unchanged; animation PBO independently parsed.')
if __name__=='__main__':build_clips();packer.main()
