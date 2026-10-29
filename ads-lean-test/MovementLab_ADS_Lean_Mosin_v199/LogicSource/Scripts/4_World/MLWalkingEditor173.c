class ML173WeaponState
{
 static ref ML144Values Values;
 static ref array<float> Coefficients;
 static ref ML144Values LeftValues;
 static ref ML144Values RightValues;
 static ref array<float> LeftCoefficients;
 static ref array<float> RightCoefficients;
 static bool EditLeft;
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
 static bool Validate(ML144Values candidate, bool leftLean, array<float> solved)
 {
  if (!candidate)
   return false;
  array<float> numbers = new array<float>;
  numbers.Insert(candidate.X);
  numbers.Insert(candidate.Y);
  numbers.Insert(candidate.Z);
  numbers.Insert(candidate.Pitch);
  numbers.Insert(candidate.Yaw);
  numbers.Insert(candidate.Roll);
  numbers.Insert(candidate.LeftPitch);
  numbers.Insert(candidate.LeftYaw);
  numbers.Insert(candidate.LeftRoll);
  numbers.Insert(candidate.RightPitch);
  numbers.Insert(candidate.RightYaw);
  numbers.Insert(candidate.RightRoll);
  numbers.Insert(candidate.HeadPitch);
  numbers.Insert(candidate.HeadYaw);
  numbers.Insert(candidate.HeadRoll);
  numbers.Insert(candidate.MuzzleYaw);
  numbers.Insert(candidate.MuzzlePitch);
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
  if (Math.AbsFloat(candidate.MuzzleYaw) > 20 || Math.AbsFloat(candidate.MuzzlePitch) > 20)
  {
   Status = "Muzzle angle range is -20 to +20 degrees.";
   return false;
  }
  if (!ML144Math.Solve(candidate, solved, leftLean))
  {
   Status = "Arm cannot reach that target; previous pose retained.";
   return false;
  }
  return true;
 }
 static bool Apply(ML144Values candidate)
 {
  array<float> solved = new array<float>;
  if (!Validate(candidate, EditLeft, solved))
   return false;
  bool holdChanged = !Values;
  if (Values)
  {
   holdChanged = candidate.X != Values.X || candidate.Y != Values.Y || candidate.Z != Values.Z;
   holdChanged = holdChanged || candidate.Pitch != Values.Pitch || candidate.Yaw != Values.Yaw || candidate.Roll != Values.Roll;
   holdChanged = holdChanged || candidate.MuzzleYaw != Values.MuzzleYaw || candidate.MuzzlePitch != Values.MuzzlePitch;
  }
  if (holdChanged)
  {
   HoldRevision++;
   ArmsReady = false;
  }
  ValuesRevision++;
  Values = candidate;
  Coefficients = solved;
  if (EditLeft)
  {
   LeftValues = candidate;
   LeftCoefficients = solved;
  }
  else
  {
   RightValues = candidate;
   RightCoefficients = solved;
  }
  Status = "Applied live. Save to keep these values.";
  return true;
 }
 static ML144Values Defaults(bool left)
 {
  ML144Values defaults = new ML144Values;
  if (left)
  {
   defaults.X = 0;
   defaults.Y = -5;
  }
  return defaults;
 }
 static ML144Values SideValues(bool left)
 {
  if (left)
   return LeftValues;
  return RightValues;
 }
 static void SelectSide(bool left)
 {
  EditLeft = left;
  if (left)
  {
   Values = LeftValues;
   Coefficients = LeftCoefficients;
   Path = "$profile:MLPoseEditor_Left.json";
  }
  else
  {
   Values = RightValues;
   Coefficients = RightCoefficients;
   Path = "$profile:MLPoseEditor_Right.json";
  }
  HoldRevision++;
  ValuesRevision++;
  ArmsReady = false;
  Status = "Side selected; changes apply only to this side.";
 }
 static void Init()
 {
  if (Initialized)
   return;
  Initialized = true;
  EditLeft = false;
  Apply(Defaults(false));
  EditLeft = true;
  Values = null;
  Path = "$profile:MLPoseEditor_Left.json";
  Apply(Defaults(true));
  SelectSide(false);
 }
 static void Reset()
 {
  Apply(Defaults(EditLeft));
 }
 static void Save()
 {
  ML173Preset.Save();
 }
 static void Load()
 {
  ML173Preset.Load();
 }
 static void LoadLegacy()
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

class ML173BodyState
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
  if (ML173WeaponState.EditLeft)
   return Left;
  return Right;
 }
 static string Path()
 {
  if (ML173WeaponState.EditLeft)
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
  if (ML173WeaponState.EditLeft)
   Left = Defaults();
  else
   Right = Defaults();
  GeometryRevision++;
  Status = "Body offsets reset on selected side.";
 }
 static void Save()
 {
  ML173Preset.Save();
 }
 static void Load()
 {
  ML173Preset.Load();
 }
};

class ML173Preset
{
 static bool Initialized;
 static string FilePath = "$profile:MLWalkingLeanPreset.json";
 static string BackupPath = "$profile:MLWalkingLeanPreset.json.bak";
 static string BundledPath = "MLADSLeanLogic/Presets/MLWalkingLeanPreset.json";
 static void Notice(string message)
 {
  ML173WeaponState.Status = message;
  ML173BodyState.Status = message;
  Print("[MLWALKPRESET173] " + message);
 }
 static bool Validate(ML153PresetFile data, array<float> leftSolved, array<float> rightSolved)
 {
  if (!data || data.PresetVersion != 1)
   return false;
  if (!data.LeftLean || !data.RightLean)
   return false;
  if (!data.LeftLean.WeaponSettings || !data.RightLean.WeaponSettings)
   return false;
  if (!ML173BodyState.ValidData(data.LeftLean.BodySettings))
   return false;
  if (!ML173BodyState.ValidData(data.RightLean.BodySettings))
   return false;
  if (!ML173WeaponState.Validate(data.LeftLean.WeaponSettings, true, leftSolved))
   return false;
  if (!ML173WeaponState.Validate(data.RightLean.WeaponSettings, false, rightSolved))
   return false;
  return true;
 }
 static bool Install(ML153PresetFile data)
 {
  array<float> leftSolved = new array<float>;
  array<float> rightSolved = new array<float>;
  // Validate all four sections before changing any active settings.
  if (!Validate(data, leftSolved, rightSolved))
   return false;
  bool selected = ML173WeaponState.EditLeft;
  ML173WeaponState.LeftValues = data.LeftLean.WeaponSettings;
  ML173WeaponState.RightValues = data.RightLean.WeaponSettings;
  ML173WeaponState.LeftCoefficients = leftSolved;
  ML173WeaponState.RightCoefficients = rightSolved;
  ML173BodyState.Left = data.LeftLean.BodySettings;
  ML173BodyState.Right = data.RightLean.BodySettings;
  ML173BodyState.GeometryRevision++;
  ML173WeaponState.SelectSide(selected);
  return true;
 }
 static ML153PresetFile Capture()
 {
  ML153PresetFile data = new ML153PresetFile;
  data.LeftLean = new ML153SidePreset;
  data.RightLean = new ML153SidePreset;
  data.LeftLean.WeaponSettings = ML173WeaponState.LeftValues;
  data.RightLean.WeaponSettings = ML173WeaponState.RightValues;
  data.LeftLean.BodySettings = ML173BodyState.Left;
  data.RightLean.BodySettings = ML173BodyState.Right;
  return data;
 }
 static void ImportLegacy(ML153PresetFile data)
 {
  string error;
  ML144Values leftWeapon;
  ML144Values rightWeapon;
  ML149Data leftBody;
  ML149Data rightBody;
  array<float> checked = new array<float>;
  if (FileExist("$profile:MLPoseEditor_Left.json"))
  {
   if (JsonFileLoader<ML144Values>.LoadFile("$profile:MLPoseEditor_Left.json", leftWeapon, error))
   {
    if (ML173WeaponState.Validate(leftWeapon, true, checked))
     data.LeftLean.WeaponSettings = leftWeapon;
   }
  }
  checked.Clear();
  if (FileExist("$profile:MLPoseEditor_Right.json"))
  {
   if (JsonFileLoader<ML144Values>.LoadFile("$profile:MLPoseEditor_Right.json", rightWeapon, error))
   {
    if (ML173WeaponState.Validate(rightWeapon, false, checked))
     data.RightLean.WeaponSettings = rightWeapon;
   }
  }
  if (FileExist("$profile:MLBodyEditor_Left.json"))
  {
   if (JsonFileLoader<ML149Data>.LoadFile("$profile:MLBodyEditor_Left.json", leftBody, error))
   {
    if (ML173BodyState.ValidData(leftBody))
     data.LeftLean.BodySettings = leftBody;
   }
  }
  if (FileExist("$profile:MLBodyEditor_Right.json"))
  {
   if (JsonFileLoader<ML149Data>.LoadFile("$profile:MLBodyEditor_Right.json", rightBody, error))
   {
    if (ML173BodyState.ValidData(rightBody))
     data.RightLean.BodySettings = rightBody;
   }
  }
  // All old files remain untouched as migration backups.
 }
 static void Init()
 {
  if (Initialized)
   return;
  ML153Preset.Init();
  ML173WeaponState.Init();
  ML173BodyState.Init();
  Initialized = true;
  if (FileExist(FilePath))
  {
   Load();
   return;
  }
  ML153PresetFile bundled;
  string error;
  if (!JsonFileLoader<ML153PresetFile>.LoadFile(BundledPath, bundled, error))
  {
   Notice("Bundled preset unavailable; current settings retained. " + error);
   return;
  }
  // The user-approved bundled preset supersedes old split legacy files.
  // A canonical profile preset, when present, still takes priority.
  if (!Install(bundled))
  {
   Notice("Initial combined preset invalid; current settings retained.");
   return;
  }
  Save();
 }
 static void Save()
 {
  Init();
  ML153PresetFile data = Capture();
  array<float> leftChecked = new array<float>;
  array<float> rightChecked = new array<float>;
  if (!Validate(data, leftChecked, rightChecked))
  {
   Notice("Save cancelled: invalid settings; previous save retained.");
   return;
  }
  string error;
  string temporaryPath = FilePath + ".tmp";
  if (!JsonFileLoader<ML153PresetFile>.SaveFile(temporaryPath, data, error))
  {
   Notice("Save failed; previous save retained. " + error);
   return;
  }
  ML153PresetFile readback;
  if (!JsonFileLoader<ML153PresetFile>.LoadFile(temporaryPath, readback, error))
  {
   DeleteFile(temporaryPath);
   Notice("Save verification failed; previous save retained.");
   return;
  }
  if (!Validate(readback, leftChecked, rightChecked))
  {
   DeleteFile(temporaryPath);
   Notice("Save verification failed; previous save retained.");
   return;
  }
  if (FileExist(FilePath))
  {
   if (FileExist(BackupPath))
   {
    if (!DeleteFile(BackupPath))
    {
     DeleteFile(temporaryPath);
     Notice("Could not rotate previous backup; save cancelled.");
     return;
    }
   }
   if (!CopyFile(FilePath, BackupPath))
   {
    DeleteFile(temporaryPath);
    Notice("Could not back up previous preset; save cancelled.");
    return;
   }
  }
  // FileMode.WRITE inside SaveFile overwrites the canonical file; the old
  // canonical is already backed up and the new payload verified above.
  if (!JsonFileLoader<ML153PresetFile>.SaveFile(FilePath, readback, error))
  {
   Notice("Could not write preset; previous .bak and verified .tmp retained.");
   return;
  }
  DeleteFile(temporaryPath);
  Notice("Saved ALL F6/F7 settings and BOTH sides: MLWalkingLeanPreset.json");
 }
 static void Load()
 {
  Init();
  ML153PresetFile loaded;
  string error;
  if (!JsonFileLoader<ML153PresetFile>.LoadFile(FilePath, loaded, error))
  {
   Notice("Load failed; current settings retained. " + error);
   return;
  }
  if (!Install(loaded))
  {
   Notice("Preset invalid; current settings retained.");
   return;
  }
  Notice("Loaded ALL F6/F7 settings and BOTH sides.");
 }
};
