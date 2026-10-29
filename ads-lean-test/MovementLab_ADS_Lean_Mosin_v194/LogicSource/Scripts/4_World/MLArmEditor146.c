// Per-actor cached native arm reference. Re-sample only after a weapon/hold change,
// with added editor rotations zeroed and settled; never chase current hand error.
class ML146ArmMath
{
 static ML144Rot AxisTurn(vector axis, float angle)
 {
  axis.Normalize();
  float x = axis[0];
  float y = axis[1];
  float z = axis[2];
  float cosine = Math.Cos(angle);
  float sine = Math.Sin(angle);
  float q = 1.0 - cosine;
  ML144Rot turn = new ML144Rot;
  turn.A = Vector(cosine+x*x*q, x*y*q-z*sine, x*z*q+y*sine);
  turn.B = Vector(y*x*q+z*sine, cosine+y*y*q, y*z*q-x*sine);
  turn.C = Vector(z*x*q-y*sine, z*y*q+x*sine, cosine+z*z*q);
  return turn;
 }
 static bool Swivel(vector root, vector elbow, vector wrist, vector angles, out vector armAngles, out vector handAngles)
 {
  armAngles = vector.Zero;
  handAngles = vector.Zero;
  if (angles.LengthSq() < 0.000001)
   return true;
  vector axis = wrist - root;
  if (axis.LengthSq() < 0.0001)
   return false;
  axis.Normalize();
  vector pole = elbow - root;
  float along = vector.Dot(pole, axis);
  pole = pole - axis * along;
  if (pole.LengthSq() < 0.000001)
   return false;
  ML144Values rotationValues = new ML144Values;
  rotationValues.Pitch = angles[0];
  rotationValues.Yaw = angles[1];
  rotationValues.Roll = angles[2];
  ML144Rot rotation = ML144Math.Euler(rotationValues);
  vector rotatedPole = rotation.Apply(pole);
  float projectedAlong = vector.Dot(rotatedPole, axis);
  rotatedPole = rotatedPole - axis * projectedAlong;
  if (rotatedPole.LengthSq() < 0.000001)
   return false;
  pole.Normalize();
  rotatedPole.Normalize();
  vector cross = ML144Math.Cross(pole, rotatedPole);
  float sine = vector.Dot(axis, cross);
  float cosine = Math.Clamp(vector.Dot(pole, rotatedPole), -1, 1);
  float angle = Math.Atan2(sine, cosine);
  ML144Rot turn = AxisTurn(axis, angle);
  ML144Rot inverse = turn.Inverse();
  array<float> coefficients = new array<float>;
  turn.AppendNative(coefficients);
  inverse.AppendNative(coefficients);
  armAngles = Vector(coefficients[0], coefficients[1], coefficients[2]);
  handAngles = Vector(coefficients[3], coefficients[4], coefficients[5]);
  return true;
 }
};
