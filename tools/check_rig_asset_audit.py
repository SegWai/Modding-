from pathlib import Path
import hashlib, json, struct, tempfile, unittest, zipfile
from unittest.mock import patch
import audit_ragdoll_assets as audit

ROOT=Path(__file__).resolve().parent
RULES=json.loads((ROOT/'rig-asset-audit/AssetRules.json').read_text())

def record(path,data):
    return {'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'part':1}

def archive(path, entries, all_records=None, extras=None):
    manifest={'format':'MovementLab-Rig-Assets-1','files':all_records if all_records is not None else [record(p,d) for p,d in entries.items()]}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json', b'\xef\xbb\xbf'+json.dumps(manifest).encode())
        for p,d in entries.items(): z.writestr(p,d)
        for p,d in (extras or {}).items(): z.writestr(p,d)
    return path

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def test_selection_rules(self):
        import re
        def chosen(p):return any(re.search(pattern,p.replace('\\','/'),re.I) for pattern in RULES['include'])
        for path in [r'dz\anims\workspaces\infected_main\infected.asi','dz/anims/workspaces/player_main/locomotion.agf','dz/characters/zombies/hermit_skinny/body.p3d','dz/characters/bodies/male/body.p3d','dz/characters/zombies/model.cfg','dz/anims/data/ragdoll.phys','dz/anims/workspaces/player/models/player_m_editorpreview.xob','dz/anims/workspaces/infected/models/z_hermit_m_editorpreview.xob','dz/anims/workspaces/infected/synctable.asy','dz/characters/zombies/z_hermit_m.xob','dz/characters/bodies/player_testing.xob']:
            self.assertTrue(chosen(path),path)
        for path in ['dz/anims/workspaces/player_main/walk.anm','dz/characters/zombies/hermit_skinny/texture.paa','Profiles/script.log','dz/characters/zombies/soldier/body.p3d']:
            self.assertFalse(chosen(path),path)
        self.assertLess(RULES['max_file_bytes'],RULES['part_budget_bytes'])
    def test_models_and_source_bones(self):
        entries={'dz/characters/zombies/hermit/body.p3d':b'ODOL'+struct.pack('<I',75), 'dz/characters/bodies/body.p3d':b'MLOD'+struct.pack('<I',257),'dz/characters/zombies/model.cfg':b'class CfgSkeletons { skeletonBones[]={"Pelvis","","Spine","Pelvis"}; };'}
        result=audit.inspect([archive(self.root/'a.zip',entries)])
        self.assertEqual(result['model_summary'],{'total':2,'binarized_ODOL':1,'source_MLOD':1})
        skeleton=next(x for x in result['files'] if x['path'].endswith('model.cfg'))
        self.assertEqual(skeleton['source_skeleton_arrays'][0]['pairs'],[('Pelvis',''),('Spine','Pelvis')])
    def test_missing_part_and_combined_parts(self):
        a={'dz/anims/workspaces/player_main/main.asi':b'Skeleton "human.skeleton"'}
        b={'dz/anims/workspaces/infected_main/main.asi':b'Physics "infected.phys"'}
        records=[record(p,d) for p,d in {**a,**b}.items()]
        first=archive(self.root/'one.zip',a,records);second=archive(self.root/'two.zip',b,records)
        self.assertEqual(audit.inspect([first])['missing_from_uploaded_parts'],list(b))
        result=audit.inspect([first,second]);self.assertEqual(result['missing_from_uploaded_parts'],[])
        self.assertEqual(result['summary'],{'human':1,'infected':1,'shared':0})
    def test_hash_tamper(self):
        path='dz/characters/zombies/model.cfg'
        z=archive(self.root/'a.zip',{path:b'changed'},[record(path,b'original')])
        with self.assertRaisesRegex(ValueError,'hash/size mismatch'):audit.inspect([z])
    def test_traversal(self):
        for index,path in enumerate(['../model.cfg','C:\\outside.cfg','/absolute.cfg']):
            z=archive(self.root/f'{index}.zip',{path:b'x'})
            with self.assertRaisesRegex(ValueError,'Unsafe archive'):audit.inspect([z])
    def test_case_duplicate(self):
        z=archive(self.root/'a.zip',{'dz/a.cfg':b'x','DZ/A.cfg':b'x'})
        with self.assertRaisesRegex(ValueError,'Duplicate archive'):audit.inspect([z])
    def test_unlisted_asset(self):
        z=archive(self.root/'a.zip',{},extras={'unlisted.cfg':b'x'})
        with self.assertRaisesRegex(ValueError,'Unlisted asset'):audit.inspect([z])
    def test_opaque_files_not_text_proof(self):
        z=archive(self.root/'a.zip',{'dz/anims/infected.phys':b'\x00ragdoll','dz/characters/config.bin':b'\x00raP\x04'})
        result=audit.inspect([z]);self.assertTrue(all(x['opaque_binary'] for x in result['files']))
        self.assertFalse(any('rig_mentions' in x for x in result['files']))
    def test_oversized_entry(self):
        z=archive(self.root/'a.zip',{'dz/a.cfg':b'x'*33})
        with patch.object(audit,'MAX_ASSET',32):
            with self.assertRaisesRegex(ValueError,'Oversized archive'):audit.inspect([z])
    def test_total_budget(self):
        z=archive(self.root/'a.zip',{'dz/a.cfg':b'x'})
        with patch.object(audit,'MAX_TOTAL',1):
            with self.assertRaisesRegex(ValueError,'size budget'):audit.inspect([z])
    def test_no_rig_inference_from_binarized_model(self):
        z=archive(self.root/'a.zip',{'dz/characters/zombies/hermit.p3d':b'ODOL'+struct.pack('<I',75)})
        result=audit.inspect([z])
        self.assertIn('Not established',result['files'][0]['rig_compatibility'])
        self.assertTrue(any('not editable' in message for message in result['next_steps']))
    def test_shared_material_config_not_infected_rig(self):
        self.assertEqual(audit.group('dz/characters/config.cpp'),'shared')

if __name__=='__main__':unittest.main(verbosity=2)
