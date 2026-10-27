// Shift pelvis/upper body together; re-solve legs to original foot frames.
class ML159TravelMath
{
 static bool Leg(PlayerBase actor, string side, float shift, array<float> output)
 {
  int hipBone = actor.GetBoneIndexByName(side + "UpLeg");
  int kneeBone = actor.GetBoneIndexByName(side + "Leg");
  int footBone = actor.GetBoneIndexByName(side + "Foot");
  if (hipBone == -1 || kneeBone == -1 || footBone == -1)
   return false;
  vector hip = actor.GetBonePositionMS(hipBone);
  vector knee = actor.GetBonePositionMS(kneeBone);
  vector foot = actor.GetBonePositionMS(footBone);
  vector shiftVector = Vector(shift, 0, 0);
  vector targetFoot = foot - shiftVector;
  ML144Rot preserveFoot = new ML144Rot;
  return ML144Math.Limb(hip, knee, foot, targetFoot, preserveFoot, output);
 }
};
