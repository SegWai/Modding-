import math,random,unittest
from captured_pose_bridge import solve,reconstruct,rotation,identity,fragment

class PoseTests(unittest.TestCase):
    def assert_pose(self,reference,target,parents):
        got=reconstruct(reference,parents,solve(reference,target,parents))
        self.assertLess(max(abs(got[n][i][j]-target[n][i][j]) for n in target for i in range(4) for j in range(4)),1e-7)

    def test_parent_correction_not_double_applied(self):
        reference={'pelvis':identity(),'arm':identity(),'hand':identity()}
        reference['arm'][0][3]=.2;reference['hand'][0][3]=.6
        desired={k:rotation(.4,.9,-.7) for k in reference}
        desired['pelvis'][1][3]=.3;desired['arm'][0][3]=.4;desired['hand'][2][3]=.9
        self.assert_pose(reference,desired,{'pelvis':None,'arm':'pelvis','hand':'arm'})

    def test_arbitrary_frames_and_branched_hierarchy(self):
        rng=random.Random(91)
        for _ in range(50):
            parents={'pelvis':None,'spine':'pelvis','leftarm':'spine','rightarm':'spine','head':'spine','leftleg':'pelvis'}
            poses=[]
            for _ in range(2):
                pose={}
                for name in parents:
                    m=rotation(*(rng.uniform(-math.pi,math.pi) for _ in range(3)))
                    for i in range(3):m[i][3]=rng.uniform(-2,2)
                    pose[name]=m
                poses.append(pose)
            self.assert_pose(*poses,parents)

    def test_prone_and_gimbal_limits(self):
        for y in [-math.pi/2,math.pi/2]:
            desired=rotation(.35,y,-.7);desired[1][3]=-.8
            self.assert_pose({'pelvis':identity()},{'pelvis':desired},{'pelvis':None})

    def test_identity_frame(self):
        pose={'head':rotation(.4,.3,.2)}
        self.assert_pose(pose,pose,{'head':None})

    def test_invalid_hierarchy_and_matrices(self):
        for parents in [{'head':'head'},{'head':'missing'}]:
            with self.assertRaises(ValueError):solve({'head':identity()},{'head':identity()},parents)
        for value in [math.nan,0,2,-1]:
            m=identity();m[0][0]=value
            with self.assertRaises(ValueError):solve({'head':m},{'head':identity()},{'head':None})

    def test_graph_only_not_claimed_runtime(self):
        f=fragment({'pelvis':None,'head':'pelvis'})
        self.assertEqual(len(f['binding_names']),2)
        self.assertEqual(f['nodes'].count('AnimSrcNodeProcTransform'),12)
        self.assertIn('UNVERIFIED',f['native_status'])
        self.assertIn('Child "APoseSrc"',f['nodes'])
        self.assertEqual(f['output_node'],'MLCapturedPose_1_Translate_Z_Node')

if __name__=='__main__':unittest.main(verbosity=2)
