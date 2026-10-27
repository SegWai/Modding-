"""Package only the files needed to launch and diagnose an ADS lean test."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import argparse
FILES=(
 '@MLADSLeanLogic/Addons/MLADSLeanLogic.pbo',
 '@MLADSLeanWorkspace/Addons/MLADSLeanWorkspace.pbo',
 'Missions/MLADSLeanMosin.ChernarusPlus/init.c',
 'Launch-Mosin-Lean-Test.cmd','Launch-Test.ps1',
 'Collect-Logs.cmd','Collect-Logs.ps1',
 'validation.json','Workspace-Provenance.json','README.txt',
)
REFERENCE_FILES=('Launch-Vanilla-Lean-Reference.cmd','Missions/MLADSLeanNativeReference.ChernarusPlus/init.c')
def runtime_files(kit):
 kit=Path(kit)
 files=FILES
 if (kit/'MLLeanPreset.json').is_file():
  files=files+('MLLeanPreset.json',)
 if any((kit/name).exists() for name in REFERENCE_FILES):
  if not all((kit/name).is_file() for name in REFERENCE_FILES):raise ValueError('Incomplete native reference launcher/mission')
  return files+REFERENCE_FILES
 return files

def package(kit,out):
 kit=Path(kit);out=Path(out);expected={}
 for name in runtime_files(kit):
  data=(kit/name).read_bytes()
  if Path(name).suffix in ('.cmd','.ps1','.txt'):data=data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
  expected[kit.name+'/'+name]=data
 out.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(expected.items()):
   entry=ZipInfo(name,(2026,10,26,0,0,0));entry.compress_type=ZIP_DEFLATED;entry.external_attr=0o100644<<16;z.writestr(entry,data)
 with ZipFile(out) as z:
  assert z.testzip() is None and set(z.namelist())==set(expected)
  for name,data in expected.items():assert z.read(name)==data
 print(f'Runtime essentials verified: {len(expected)} files, {out.stat().st_size} bytes')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('kit',type=Path);p.add_argument('output',type=Path);a=p.parse_args();package(a.kit,a.output)
