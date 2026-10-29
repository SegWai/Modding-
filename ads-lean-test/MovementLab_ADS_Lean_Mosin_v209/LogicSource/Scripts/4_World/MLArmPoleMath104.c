// One-shot elbow pole solve from native pose positions. No bone/input writes.
class MLArmPoleMath104
{
 static bool Solve(vector root, vector elbow, vector wrist, vector pole, out vector nativeAngles, out vector elbowGoal)
 {
  nativeAngles = vector.Zero;
  elbowGoal = elbow;
  vector upper = elbow - root;
  vector lower = wrist - elbow;
  vector reach = wrist - root;
  float l1 = upper.Length();
  float l2 = lower.Length();
  float distance = reach.Length();
  if (l1 < 0.001 || l2 < 0.001 || distance < 0.001)
   return false;
  vector direction = reach * (1.0 / distance);
  float along = l1 * l1 - l2 * l2;
  along = (along + distance * distance) / (2.0 * distance);
  float radiusSquared = Math.Max(0.0, l1 * l1 - along * along);
  float radius = Math.Sqrt(radiusSquared);
  vector projected = pole - direction * vector.Dot(pole, direction);
  if (projected.LengthSq() < 0.000001)
   return false;
  projected.Normalize();
  elbowGoal = root + direction * along + projected * radius;
  vector from = upper.Normalized();
  vector to = (elbowGoal - root).Normalized();
  vector cross;
  cross[0] = from[1] * to[2] - from[2] * to[1];
  cross[1] = from[2] * to[0] - from[0] * to[2];
  cross[2] = from[0] * to[1] - from[1] * to[0];
  float sine = cross.Length();
  float cosine = Math.Clamp(vector.Dot(from, to), -1.0, 1.0);
  if (sine < 0.000001)
   return cosine > 0;
  vector turn = cross * (1.0 / sine);
  float x = turn[0];
  float y = turn[1];
  float z = turn[2];
  float q = 1.0 - cosine;
  float d20 = z * x * q - y * sine;
  float d21 = z * y * q + x * sine;
  float d22 = cosine + z * z * q;
  float d10 = y * x * q + z * sine;
  float d00 = cosine + x * x * q;
  float angleY = Math.Asin(Math.Clamp(-d20, -1.0, 1.0));
  float angleX;
  float angleZ;
  if (Math.AbsFloat(Math.Cos(angleY)) > 0.000001)
  {
   angleX = Math.Atan2(d21, d22);
   angleZ = Math.Atan2(d10, d00);
  }
  else
  {
   float d12 = y * z * q - x * sine;
   float d11 = cosine + y * y * q;
   angleX = Math.Atan2(-d12, d11);
   angleZ = 0;
  }
  // Native model-axis ProcTransform rotation sign is opposite RH math.
  nativeAngles = Vector(-angleX, -angleY, -angleZ);
  return true;
 }
 static bool Swivel(vector root, vector elbow, vector wrist, vector pole, out vector nativeAngles, out vector elbowGoal, out vector handAngles)
 {
  nativeAngles = vector.Zero;
  handAngles = vector.Zero;
  elbowGoal = elbow;
  vector upper = elbow - root;
  vector lower = wrist - elbow;
  vector reach = wrist - root;
  float l1 = upper.Length();
  float l2 = lower.Length();
  float distance = reach.Length();
  if (l1 < 0.001 || l2 < 0.001 || distance < 0.001)
   return false;
  vector direction = reach * (1.0 / distance);
  float along = l1 * l1 - l2 * l2;
  along = (along + distance * distance) / (2.0 * distance);
  float radiusSquared = Math.Max(0.0, l1 * l1 - along * along);
  float radius = Math.Sqrt(radiusSquared);
  vector projected = pole - direction * vector.Dot(pole, direction);
  if (projected.LengthSq() < 0.000001)
   return false;
  projected.Normalize();
  elbowGoal = root + direction * along + projected * radius;
  vector centre = root + direction * along;
  vector from = (elbow - centre).Normalized();
  vector to = projected;
  vector cross;
  cross[0] = from[1] * to[2] - from[2] * to[1];
  cross[1] = from[2] * to[0] - from[0] * to[2];
  cross[2] = from[0] * to[1] - from[1] * to[0];
  float sine = cross.Length();
  float cosine = Math.Clamp(vector.Dot(from, to), -1.0, 1.0);
  if (sine < 0.000001)
   return cosine > 0;
  vector turn = cross * (1.0 / sine);
  float x = turn[0];
  float y = turn[1];
  float z = turn[2];
  float q = 1.0 - cosine;
  float d20 = z * x * q - y * sine;
  float d21 = z * y * q + x * sine;
  float d22 = cosine + z * z * q;
  float d10 = y * x * q + z * sine;
  float d00 = cosine + x * x * q;
  float angleY = Math.Asin(Math.Clamp(-d20, -1.0, 1.0));
  float angleX;
  float angleZ;
  if (Math.AbsFloat(Math.Cos(angleY)) > 0.000001)
  {
   angleX = Math.Atan2(d21, d22);
   angleZ = Math.Atan2(d10, d00);
  }
  else
  {
   float d12 = y * z * q - x * sine;
   float d11 = cosine + y * y * q;
   angleX = Math.Atan2(-d12, d11);
   angleZ = 0;
  }
  // Inverse model rotation at the wrist restores its original orientation.
  float d02 = x * z * q + y * sine;
  float d01 = x * y * q - z * sine;
  float inverseY = Math.Asin(Math.Clamp(-d02, -1.0, 1.0));
  float inverseX = Math.Atan2(y * z * q - x * sine, d22);
  float inverseZ = Math.Atan2(d01, d00);
  handAngles = Vector(-inverseX, -inverseY, -inverseZ);
  // Native model-axis ProcTransform rotation sign is opposite RH math.
  nativeAngles = Vector(-angleX, -angleY, -angleZ);
  return true;
 }
};
