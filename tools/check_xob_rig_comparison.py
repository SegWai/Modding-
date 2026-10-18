import math
import struct
import unittest
from compare_xob_rig_transforms import read_xob, world_nodes, qmul


def fixture(names=('Scene_Root','Head'), rows=None, materials=1):
    if rows is None:
        rows=[(1,0,0,0,0,0,0,1,65535,1),(2,0,1,0,0,0,0,1,65535,65535)]
    strings=b'material\0'+b''.join(n.encode()+b'\0' for n in names)
    head=bytearray(60)
    struct.pack_into('<HH',head,44,materials,len(rows))
    struct.pack_into('<I',head,56,len(strings))
    head+=strings+bytes(2*materials)+b''.join(struct.pack('<I7fHH',*r) for r in rows)
    body=b'XOB6HEAD'+struct.pack('>I',len(head))+head+b'LODS'+struct.pack('>I',0)
    return b'FORM'+struct.pack('>I',len(body))+body


class XobTests(unittest.TestCase):
    def test_tree_and_transforms(self):
        rig=read_xob(fixture())
        self.assertEqual(rig['node_count'],2)
        self.assertEqual(rig['nodes'][1]['parent'],'Scene_Root')
        self.assertEqual(world_nodes(rig)['head'][0],(0,1,0))

    def test_multi_material_offset(self):
        self.assertEqual(read_xob(fixture(materials=2))['nodes'][1]['name'],'Head')

    def test_truncated_and_lengths(self):
        data=fixture()
        for end in range(len(data)):
            with self.assertRaises(ValueError):
                read_xob(data[:end])

    def test_bad_node_links(self):
        for child in [0,2]:
            rows=[(1,0,0,0,0,0,0,1,65535,child),(2,0,1,0,0,0,0,1,65535,65535)]
            with self.assertRaises(ValueError):
                read_xob(fixture(rows=rows))

    def test_unreachable_node(self):
        rows=[(1,0,0,0,0,0,0,1,65535,65535),(2,0,1,0,0,0,0,1,65535,65535)]
        with self.assertRaises(ValueError):
            read_xob(fixture(rows=rows))

    def test_nonunit_and_nonfinite(self):
        for value in [0,math.inf,math.nan]:
            rows=[(1,0,0,0,0,0,0,value,65535,65535)]
            with self.assertRaises(ValueError):
                read_xob(fixture(rows=rows))

    def test_duplicate_names(self):
        with self.assertRaises(ValueError):
            read_xob(fixture(names=('Head','Head')))

    def test_rotation_composition(self):
        q=(0,0,math.sqrt(.5),math.sqrt(.5))
        rig={'nodes':[{'name':'root','parent':None,'translation':[1,0,0],'quaternion_xyzw':q},
                      {'name':'head','parent':'root','translation':[1,0,0],'quaternion_xyzw':[0,0,0,1]}]}
        t,r=world_nodes(rig)['head']
        for actual,expected in zip(t,(1,1,0)):
            self.assertAlmostEqual(actual,expected)
        self.assertEqual(r,q)

    def test_negative_quaternion_equivalence(self):
        q=(0,0,math.sqrt(.5),math.sqrt(.5))
        rotated=qmul(qmul(q,(1,0,0,0)),(-q[0],-q[1],-q[2],q[3]))
        self.assertAlmostEqual(rotated[1],1)


if __name__=='__main__':
    unittest.main(verbosity=2)
