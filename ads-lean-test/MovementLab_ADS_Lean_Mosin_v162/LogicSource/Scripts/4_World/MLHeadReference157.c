// Model-space orientation only: no position, camera, arm or weapon mutation.
class ML157HeadReference
{
 static ref array<ref ML144Rot> Target = {null, null, null, null};
 static bool Ready[4];
 static int Revision = -1;
 static int BodyRevision = -1;
 static void Sync(int revision, int bodyRevision)
 {
  if (Revision == revision && BodyRevision == bodyRevision)
   return;
  Revision = revision;
  BodyRevision = bodyRevision;
  Ready[0] = false;
  Ready[1] = false;
  Ready[2] = false;
  Ready[3] = false;
 }
 static ML144Rot Read(PlayerBase actor)
 {
  int headBone = actor.GetBoneIndexByName("Head");
  if (headBone == -1)
   return null;
  vector headTM[4];
  actor.GetBoneTransformMS(headBone, headTM);
  vector xAxis = headTM[0];
  vector yAxis = headTM[1];
  vector zAxis = headTM[2];
  if (xAxis.LengthSq() < 0.5 || yAxis.LengthSq() < 0.5 || zAxis.LengthSq() < 0.5)
   return null;
  xAxis.Normalize();
  yAxis.Normalize();
  zAxis.Normalize();
  ML144Rot rotation = new ML144Rot;
  rotation.A = Vector(xAxis[0], yAxis[0], zAxis[0]);
  rotation.B = Vector(xAxis[1], yAxis[1], zAxis[1]);
  rotation.C = Vector(xAxis[2], yAxis[2], zAxis[2]);
  return rotation;
 }
};
