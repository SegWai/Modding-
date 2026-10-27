// Live tuning uses fixed reference geometry, never a per-frame pose feedback loop.
class ML144Values
{
 float X = 5;
 float Y = -10;
 float Z;
 float Pitch;
 float Yaw;
 float Roll;
 float LeftPitch;
 float LeftYaw;
 float LeftRoll;
 float RightPitch;
 float RightYaw;
 float RightRoll;
 float HeadPitch;
 float HeadYaw;
 float HeadRoll;

};
class ML144Rot
{
 vector A = "1 0 0";
 vector B = "0 1 0";
 vector C = "0 0 1";
 vector Apply(vector v)
 {
  return Vector(vector.Dot(A, v), vector.Dot(B, v), vector.Dot(C, v));
 }
 ML144Rot Inverse()
 {
  ML144Rot t = new ML144Rot;
  t.A = Vector(A[0], B[0], C[0]);
  t.B = Vector(A[1], B[1], C[1]);
  t.C = Vector(A[2], B[2], C[2]);
  return t;
 }
 ML144Rot Times(ML144Rot other)
 {
  ML144Rot columns = other.Inverse();
  ML144Rot t = new ML144Rot;
  t.A = Vector(vector.Dot(A, columns.A), vector.Dot(A, columns.B), vector.Dot(A, columns.C));
  t.B = Vector(vector.Dot(B, columns.A), vector.Dot(B, columns.B), vector.Dot(B, columns.C));
  t.C = Vector(vector.Dot(C, columns.A), vector.Dot(C, columns.B), vector.Dot(C, columns.C));
  return t;
 }
 void AppendNative(array<float> output)
 {
  float ay = Math.Asin(Math.Clamp(-C[0], -1, 1));
  float ax;
  float az;
  if (Math.AbsFloat(Math.Cos(ay)) > 0.000001)
  {
   ax = Math.Atan2(C[1], C[2]);
   az = Math.Atan2(B[0], A[0]);
  }
  else
  {
   ax = Math.Atan2(-B[2], B[1]);
   az = 0;
  }
  output.Insert(-ax);
  output.Insert(-ay);
  output.Insert(-az);
 }
};
class ML144Math
{
 static vector Cross(vector a, vector b)
 {
  return Vector(a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]);
 }
 static ML144Rot Turn(vector from, vector to)
 {
  from.Normalize();
  to.Normalize();
  vector cross = Cross(from, to);
  float sine = cross.Length();
  float cosine = Math.Clamp(vector.Dot(from, to), -1, 1);
  ML144Rot t = new ML144Rot;
  if (sine < 0.000001)
   return t;
  vector axis = cross * (1.0 / sine);
  float x = axis[0];
  float y = axis[1];
  float z = axis[2];
  float q = 1.0 - cosine;
  t.A = Vector(cosine+x*x*q, x*y*q-z*sine, x*z*q+y*sine);
  t.B = Vector(y*x*q+z*sine, cosine+y*y*q, y*z*q-x*sine);
  t.C = Vector(z*x*q-y*sine, z*y*q+x*sine, cosine+z*z*q);
  return t;
 }
 static ML144Rot Euler(ML144Values value)
 {
  float x = value.Pitch * Math.DEG2RAD;
  float y = value.Yaw * Math.DEG2RAD;
  float z = value.Roll * Math.DEG2RAD;
  float cx = Math.Cos(x);
  float sx = Math.Sin(x);
  float cy = Math.Cos(y);
  float sy = Math.Sin(y);
  float cz = Math.Cos(z);
  float sz = Math.Sin(z);
  ML144Rot t = new ML144Rot;
  t.A = Vector(cz*cy, cz*sy*sx-sz*cx, cz*sy*cx+sz*sx);
  t.B = Vector(sz*cy, sz*sy*sx+cz*cx, sz*sy*cx-cz*sx);
  t.C = Vector(-sy, cy*sx, cy*cx);
  return t;
 }
 static bool Limb(vector root, vector elbow, vector wrist, vector target, ML144Rot orientation, array<float> output)
 {
  float upper = vector.Distance(root, elbow);
  float lower = vector.Distance(elbow, wrist);
  vector reach = target - root;
  float distance = reach.Length();
  // Keep each bound separate: the native Enforce parser rejects the previous
  // mixed function/arithmetic expression in this compound condition.
  float lengthDifference = upper - lower;
  float minimumReach = Math.AbsFloat(lengthDifference);
  minimumReach = minimumReach + 0.002;
  float maximumReach = upper + lower;
  maximumReach = maximumReach - 0.002;
  if (distance <= minimumReach)
   return false;
  if (distance >= maximumReach)
   return false;
  vector axis = reach * (1.0 / distance);
  float upperSquared = upper * upper;
  float lowerSquared = lower * lower;
  float reachSquared = distance * distance;
  float along = upperSquared - lowerSquared;
  along = along + reachSquared;
  float denominator = 2.0 * distance;
  along = along / denominator;
  float radiusSquared = upperSquared - along * along;
  radiusSquared = Math.Max(0, radiusSquared);
  float radius = Math.Sqrt(radiusSquared);
  vector pole = elbow-root;
  pole = pole-axis*vector.Dot(pole, axis);
  if (pole.LengthSq() < 0.000001)
   return false;
  pole.Normalize();
  vector goal = root+axis*along+pole*radius;
  ML144Rot armTurn = Turn(elbow-root, goal-root);
  vector rotatedLower = armTurn.Apply(wrist-elbow);
  ML144Rot foreTurn = Turn(rotatedLower, target-goal);
  ML144Rot combined = foreTurn.Times(armTurn);
  ML144Rot inverse = combined.Inverse();
  ML144Rot handTurn = orientation.Times(inverse);
  armTurn.AppendNative(output);
  foreTurn.AppendNative(output);
  handTurn.AppendNative(output);
  return true;
 }
 static void Seed(bool right, out vector root, out vector elbow, out vector wrist)
 {
  if (right)
  {
   root = Vector(0.128964327733, 1.3646036463, -0.0685806371047);
   elbow = Vector(0.232675324806, 1.12230392152, 0.0523943415775);
   wrist = Vector(0.156801082436, 1.36270056994, 0.167258305319);
  }
  else
  {
   root = Vector(-0.146458324454, 1.42127137609, -0.0315709986774);
   elbow = Vector(-0.178184477963, 1.26412542564, 0.210067332299);
   wrist = Vector(-0.070968283906, 1.47529961832, 0.34983818603);
  }
 }
 static bool Solve(ML144Values value, array<float> output)
 {
  output.Clear();
  vector leftRoot;
  vector leftElbow;
  vector leftWrist;
  vector rightRoot;
  vector rightElbow;
  vector rightWrist;
  Seed(false, leftRoot, leftElbow, leftWrist);
  Seed(true, rightRoot, rightElbow, rightWrist);
  ML144Rot orientation = Euler(value);
  vector offset = Vector(value.X*0.01, (value.Y+5.0)*0.01, value.Z*0.01);
  vector rightTarget = rightWrist+offset;
  vector leftTarget = rightTarget+orientation.Apply(leftWrist-rightWrist);
  if (!Limb(leftRoot, leftElbow, leftWrist, leftTarget, orientation, output))
   return false;
  if (!Limb(rightRoot, rightElbow, rightWrist, rightTarget, orientation, output))
   return false;
  return output.Count() == 18;
 }
};
class ML144State
{
 static ref ML144Values Values;
 static ref array<float> Coefficients;
 static bool Initialized;
 static bool Open;
 static bool HoldRight = true;
 static bool KeyDown;
 static bool Bound;
 static bool ArmsReady;
 static int HoldRevision;
 static int ValuesRevision;
 static string Status;
 static string Path = "$profile:MLPoseEditor_Right.json";
 static bool Apply(ML144Values candidate)
 {
  if (!candidate)
   return false;
  array<float> numbers = {candidate.X, candidate.Y, candidate.Z, candidate.Pitch, candidate.Yaw, candidate.Roll, candidate.LeftPitch, candidate.LeftYaw, candidate.LeftRoll, candidate.RightPitch, candidate.RightYaw, candidate.RightRoll, candidate.HeadPitch, candidate.HeadYaw, candidate.HeadRoll};
  foreach (float number : numbers)
  {
   if (number != number || Math.AbsFloat(number) > 1000)
   {
    Status = "Invalid value; previous pose retained.";
    return false;
   }
  }
  if (candidate.X < -20 || candidate.X > 20 || candidate.Y < -25 || candidate.Y > 15 || candidate.Z < -20 || candidate.Z > 25)
  {
   Status = "Position outside editor range; previous pose retained.";
   return false;
  }
  if (Math.AbsFloat(candidate.Pitch)>20 || Math.AbsFloat(candidate.Yaw)>20 || Math.AbsFloat(candidate.Roll)>20)
  {
   Status = "Rotation range is -20 to +20 degrees.";
   return false;
  }
  array<float> armValues = {candidate.LeftPitch, candidate.LeftYaw, candidate.LeftRoll, candidate.RightPitch, candidate.RightYaw, candidate.RightRoll};
  foreach (float armValue : armValues)
  {
   if (Math.AbsFloat(armValue) > 90)
   {
    Status = "Arm bend-direction range is -90 to +90 degrees.";
    return false;
   }
  }
  if (Math.AbsFloat(candidate.HeadPitch) > 45 || Math.AbsFloat(candidate.HeadYaw) > 45 || Math.AbsFloat(candidate.HeadRoll) > 45)
  {
   Status = "Head range is -45 to +45 degrees.";
   return false;
  }
  array<float> solved = new array<float>;
  if (!ML144Math.Solve(candidate, solved))
  {
   Status = "Arm cannot reach that target; previous pose retained.";
   return false;
  }
  bool holdChanged = !Values;
  if (Values)
  {
   holdChanged = candidate.X != Values.X || candidate.Y != Values.Y || candidate.Z != Values.Z;
   holdChanged = holdChanged || candidate.Pitch != Values.Pitch || candidate.Yaw != Values.Yaw || candidate.Roll != Values.Roll;
  }
  if (holdChanged)
  {
   HoldRevision++;
   ArmsReady = false;
  }
  ValuesRevision++;
  Values = candidate;
  Coefficients = solved;
  Status = "Applied live. Save to keep these values.";
  return true;
 }
 static void Init()
 {
  if (Initialized)
   return;
  Initialized = true;
  Apply(new ML144Values);
  if (FileExist(Path))
   Load();
 }
 static void Reset()
 {
  Apply(new ML144Values);
 }
 static void Save()
 {
  string error;
  if (JsonFileLoader<ML144Values>.SaveFile(Path, Values, error))
   Status = "Saved: Profiles/LeanMosin/MLPoseEditor_Right.json";
  else
   Status = "Save failed: " + error;
 }
 static void Load()
 {
  ML144Values loaded;
  string error;
  if (!JsonFileLoader<ML144Values>.LoadFile(Path, loaded, error))
  {
   Status = "No saved values loaded: " + error;
   return;
  }
  if (Apply(loaded))
   Status = "Saved values loaded and applied live.";
 }
};
