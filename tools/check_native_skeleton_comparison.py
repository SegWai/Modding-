import struct
import unittest
from compare_ragdoll_skeletons import skeleton, ragdoll


def fixture(bones):
    return (b'ODOL' + struct.pack('<I', 56) + bytes(56) + b'DayzTemporarySkeleton\0\0'
            + struct.pack('<I', len(bones))
            + b''.join(n.encode() + b'\0' + p.encode() + b'\0' for n, p in bones) + b'\0')


class ComparisonTests(unittest.TestCase):
    def test_names_and_parents(self):
        bones = [('pelvis', ''), ('spine', 'pelvis')]
        self.assertEqual(skeleton(fixture(bones))['bones'], [list(x) for x in bones])

    def test_cycles_and_missing_parents(self):
        for bones in [[('a', 'a')], [('a', 'b')], [('a', 'b'), ('b', 'a')]]:
            with self.assertRaises(ValueError):
                skeleton(fixture(bones))

    def test_duplicates(self):
        with self.assertRaises(ValueError):
            skeleton(fixture([('a', ''), ('a', '')]))

    def test_truncation(self):
        data = fixture([('a', '')])
        for end in range(len(data)):
            with self.assertRaises((ValueError, UnicodeDecodeError)):
                skeleton(data[:end])

    def test_version(self):
        with self.assertRaises(ValueError):
            skeleton(b'ODOL' + struct.pack('<I', 70))

    def test_ragdoll_nesting_and_mass(self):
        bones = ragdoll('RagdollDef { Object "x" { RagdollBone pelvis { Mass 17 Geometries { Shape x { Radius .1 } } { RagdollBone head { Mass 6.1 } } } } }')
        self.assertEqual(bones, [{'name': 'pelvis', 'parent': '', 'mass': 17}, {'name': 'head', 'parent': 'pelvis', 'mass': 6.1}])

    def test_bad_ragdoll(self):
        for text in ['RagdollBone head {', 'RagdollBone head { }', '}', 'RagdollBone head nope']:
            with self.assertRaises(ValueError):
                ragdoll(text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
