class ML149Part
{
 string BoneName;
 float X;
 float Y;
 float Z;
 float Pitch;
 float Yaw;
 float Roll;
 float ComponentValue(int index)
 {
  switch (index)
  {
   case 0: return X;
   case 1: return Y;
   case 2: return Z;
   case 3: return Pitch;
   case 4: return Yaw;
   case 5: return Roll;
  }
  return 0;
 }
};
class ML149Data
{
 ref array<ref ML149Part> Parts = new array<ref ML149Part>;
};
class ML149State
{
 static ref ML149Data Left;
 static ref ML149Data Right;
 static ref TStringArray Bones;
 static ref TStringArray Labels;
 static int GeometryRevision;
 static bool Initialized;
 static bool Open;
 static bool KeyDown;
 static bool Bound;
 static int SelectedPart;
 static string Status;
 static void Names()
 {
  if (Bones)
   return;
  Bones = new TStringArray;
  Labels = new TStringArray;
  Bones.Insert("Pelvis");
  Labels.Insert("Pelvis");
  Bones.Insert("Spine");
  Labels.Insert("Lower back");
  Bones.Insert("Spine1");
  Labels.Insert("Mid back");
  Bones.Insert("Spine2");
  Labels.Insert("Upper back");
  Bones.Insert("Spine3");
  Labels.Insert("Chest / torso");
  Bones.Insert("Neck");
  Labels.Insert("Lower neck");
  Bones.Insert("Neck1");
  Labels.Insert("Upper neck");
  Bones.Insert("Head");
  Labels.Insert("Head");
  Bones.Insert("LeftShoulder");
  Labels.Insert("Left shoulder");
  Bones.Insert("RightShoulder");
  Labels.Insert("Right shoulder");
  Bones.Insert("LeftArm");
  Labels.Insert("Left upper arm");
  Bones.Insert("RightArm");
  Labels.Insert("Right upper arm");
  Bones.Insert("LeftForeArm");
  Labels.Insert("Left forearm");
  Bones.Insert("RightForeArm");
  Labels.Insert("Right forearm");
  Bones.Insert("LeftHand");
  Labels.Insert("Left hand");
  Bones.Insert("RightHand");
  Labels.Insert("Right hand");
  Bones.Insert("LeftUpLeg");
  Labels.Insert("Left thigh");
  Bones.Insert("RightUpLeg");
  Labels.Insert("Right thigh");
  Bones.Insert("LeftLeg");
  Labels.Insert("Left shin / knee");
  Bones.Insert("RightLeg");
  Labels.Insert("Right shin / knee");
  Bones.Insert("LeftFoot");
  Labels.Insert("Left foot");
  Bones.Insert("RightFoot");
  Labels.Insert("Right foot");
  Bones.Insert("LeftToeBase");
  Labels.Insert("Left toes");
  Bones.Insert("RightToeBase");
  Labels.Insert("Right toes");
 }
 static ML149Data Defaults()
 {
  Names();
  ML149Data data = new ML149Data;
  foreach (string bone : Bones)
  {
   ML149Part part = new ML149Part;
   part.BoneName = bone;
   data.Parts.Insert(part);
  }
  return data;
 }
 static ML149Data Current()
 {
  if (ML144State.EditLeft)
   return Left;
  return Right;
 }
 static string Path()
 {
  if (ML144State.EditLeft)
   return "$profile:MLBodyEditor_Left.json";
  return "$profile:MLBodyEditor_Right.json";
 }
 static bool ValidPart(ML149Part part)
 {
  if (!part)
   return false;
  array<float> values = {part.X, part.Y, part.Z, part.Pitch, part.Yaw, part.Roll};
  for (int i = 0; i < 6; i++)
  {
   float limit = 15;
   if (i >= 3)
    limit = 45;
   float value = values[i];
   if (value != value || Math.AbsFloat(value) > limit)
    return false;
  }
  return true;
 }
 static bool ValidData(ML149Data data)
 {
  Names();
  if (!data || !data.Parts || data.Parts.Count() != Bones.Count())
   return false;
  for (int i = 0; i < Bones.Count(); i++)
  {
   ML149Part part = data.Parts[i];
   if (!ValidPart(part))
    return false;
   if (part.BoneName != Bones[i])
    return false;
  }
  return true;
 }
 static void Init()
 {
  if (Initialized)
   return;
  Initialized = true;
  Left = Defaults();
  Right = Defaults();
  string error;
  ML149Data leftSaved;
  ML149Data rightSaved;
  if (FileExist("$profile:MLBodyEditor_Left.json"))
  {
   if (JsonFileLoader<ML149Data>.LoadFile("$profile:MLBodyEditor_Left.json", leftSaved, error) && ValidData(leftSaved))
    Left = leftSaved;
  }
  if (FileExist("$profile:MLBodyEditor_Right.json"))
  {
   if (JsonFileLoader<ML149Data>.LoadFile("$profile:MLBodyEditor_Right.json", rightSaved, error) && ValidData(rightSaved))
    Right = rightSaved;
  }
  Status = "Select a body part. Position is cm; rotation is degrees.";
 }
 static bool Apply(ML149Part part)
 {
  if (!ValidPart(part))
  {
   Status = "Range: position +/-15 cm; rotation +/-45 degrees.";
   return false;
  }
  ML149Data data = Current();
  if (!data || part.BoneName != Bones[SelectedPart])
   return false;
  data.Parts[SelectedPart] = part;
  GeometryRevision++;
  Status = "Applied live. Child bones move with their parent.";
  return true;
 }
 static void ResetPart()
 {
  ML149Part part = new ML149Part;
  part.BoneName = Bones[SelectedPart];
  Apply(part);
 }
 static void ResetSide()
 {
  if (ML144State.EditLeft)
   Left = Defaults();
  else
   Right = Defaults();
  GeometryRevision++;
  Status = "Body offsets reset on selected side.";
 }
 static void Save()
 {
  ML153Preset.Save();
 }
 static void Load()
 {
  ML153Preset.Load();
 }
};
