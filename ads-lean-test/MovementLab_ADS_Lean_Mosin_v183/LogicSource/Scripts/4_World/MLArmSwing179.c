class ML179ArmSwing
{
 static bool BendToGoal(vector root, vector elbow, vector wrist, vector goal, out vector armAngles, out vector foreAngles, out vector handAngles)
 {
  armAngles = vector.Zero;
  foreAngles = vector.Zero;
  handAngles = vector.Zero;
  vector oldUpper = elbow - root;
  vector newUpper = goal - root;
  if (oldUpper.LengthSq() < 0.000001 || newUpper.LengthSq() < 0.000001)
   return false;
  vector oldDirection = oldUpper.Normalized();
  vector newDirection = newUpper.Normalized();
  if (vector.Dot(oldDirection, newDirection) < -0.99999)
   return false;
  ML144Rot armTurn = ML144Math.Turn(oldUpper, newUpper);
  vector oldLower = wrist - elbow;
  vector inheritedLower = armTurn.Apply(oldLower);
  vector desiredLower = wrist - goal;
  if (inheritedLower.LengthSq() < 0.000001 || desiredLower.LengthSq() < 0.000001)
   return false;
  vector lowerDirection = inheritedLower.Normalized();
  vector targetDirection = desiredLower.Normalized();
  if (vector.Dot(lowerDirection, targetDirection) < -0.99999)
   return false;
  ML144Rot foreTurn = ML144Math.Turn(inheritedLower, desiredLower);
  ML144Rot combined = foreTurn.Times(armTurn);
  ML144Rot handTurn = combined.Inverse();
  array<float> solved = new array<float>;
  armTurn.AppendNative(solved);
  foreTurn.AppendNative(solved);
  handTurn.AppendNative(solved);
  if (solved.Count() != 9)
   return false;
  armAngles = Vector(solved[0], solved[1], solved[2]);
  foreAngles = Vector(solved[3], solved[4], solved[5]);
  handAngles = Vector(solved[6], solved[7], solved[8]);
  return true;
 }
 static bool Pole(vector root, vector elbow, vector wrist, vector pole, out vector armAngles, out vector foreAngles, out vector handAngles, out vector goal)
 {
  vector unused;
  if (!MLArmPoleMath104.Solve(root, elbow, wrist, pole, unused, goal))
   return false;
  return BendToGoal(root, elbow, wrist, goal, armAngles, foreAngles, handAngles);
 }
 static bool Editor(vector root, vector elbow, vector wrist, vector angles, out vector armAngles, out vector foreAngles, out vector handAngles)
 {
  armAngles = vector.Zero;
  foreAngles = vector.Zero;
  handAngles = vector.Zero;
  if (angles.LengthSq() < 0.000001)
   return true;
  vector axis = wrist - root;
  if (axis.LengthSq() < 0.0001)
   return false;
  axis.Normalize();
  vector relative = elbow - root;
  float along = vector.Dot(relative, axis);
  vector centre = root + axis * along;
  vector pole = elbow - centre;
  float radius = pole.Length();
  if (radius < 0.001)
   return false;
  ML144Values rotationValue = new ML144Values;
  rotationValue.Pitch = angles[0];
  rotationValue.Yaw = angles[1];
  rotationValue.Roll = angles[2];
  ML144Rot rotation = ML144Math.Euler(rotationValue);
  vector projected = rotation.Apply(pole);
  float projectedAlong = vector.Dot(projected, axis);
  projected = projected - axis * projectedAlong;
  if (projected.LengthSq() < 0.000001)
   return false;
  projected.Normalize();
  vector goal = centre + projected * radius;
  return BendToGoal(root, elbow, wrist, goal, armAngles, foreAngles, handAngles);
 }
};
