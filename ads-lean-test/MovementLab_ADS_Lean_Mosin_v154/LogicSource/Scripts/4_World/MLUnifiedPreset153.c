class ML153SidePreset
{
 ref ML144Values WeaponSettings;
 ref ML149Data BodySettings;
};
class ML153PresetFile
{
 int PresetVersion = 1;
 ref ML153SidePreset LeftLean;
 ref ML153SidePreset RightLean;
};
class ML153Preset
{
 static bool Initialized;
 static string FilePath = "$profile:MLLeanPreset.json";
 static string BackupPath = "$profile:MLLeanPreset.json.bak";
 static string BundledPath = "MLADSLeanLogic/Presets/MLLeanPreset.json";
 static void Notice(string message)
 {
  ML144State.Status = message;
  ML149State.Status = message;
  Print("[MLPRESET153] " + message);
 }
 static bool Validate(ML153PresetFile data, array<float> leftSolved, array<float> rightSolved)
 {
  if (!data || data.PresetVersion != 1)
   return false;
  if (!data.LeftLean || !data.RightLean)
   return false;
  if (!data.LeftLean.WeaponSettings || !data.RightLean.WeaponSettings)
   return false;
  if (!ML149State.ValidData(data.LeftLean.BodySettings))
   return false;
  if (!ML149State.ValidData(data.RightLean.BodySettings))
   return false;
  if (!ML144State.Validate(data.LeftLean.WeaponSettings, true, leftSolved))
   return false;
  if (!ML144State.Validate(data.RightLean.WeaponSettings, false, rightSolved))
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
  bool selected = ML144State.EditLeft;
  ML144State.LeftValues = data.LeftLean.WeaponSettings;
  ML144State.RightValues = data.RightLean.WeaponSettings;
  ML144State.LeftCoefficients = leftSolved;
  ML144State.RightCoefficients = rightSolved;
  ML149State.Left = data.LeftLean.BodySettings;
  ML149State.Right = data.RightLean.BodySettings;
  ML149State.GeometryRevision++;
  ML144State.SelectSide(selected);
  return true;
 }
 static ML153PresetFile Capture()
 {
  ML153PresetFile data = new ML153PresetFile;
  data.LeftLean = new ML153SidePreset;
  data.RightLean = new ML153SidePreset;
  data.LeftLean.WeaponSettings = ML144State.LeftValues;
  data.RightLean.WeaponSettings = ML144State.RightValues;
  data.LeftLean.BodySettings = ML149State.Left;
  data.RightLean.BodySettings = ML149State.Right;
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
    if (ML144State.Validate(leftWeapon, true, checked))
     data.LeftLean.WeaponSettings = leftWeapon;
   }
  }
  checked.Clear();
  if (FileExist("$profile:MLPoseEditor_Right.json"))
  {
   if (JsonFileLoader<ML144Values>.LoadFile("$profile:MLPoseEditor_Right.json", rightWeapon, error))
   {
    if (ML144State.Validate(rightWeapon, false, checked))
     data.RightLean.WeaponSettings = rightWeapon;
   }
  }
  if (FileExist("$profile:MLBodyEditor_Left.json"))
  {
   if (JsonFileLoader<ML149Data>.LoadFile("$profile:MLBodyEditor_Left.json", leftBody, error))
   {
    if (ML149State.ValidData(leftBody))
     data.LeftLean.BodySettings = leftBody;
   }
  }
  if (FileExist("$profile:MLBodyEditor_Right.json"))
  {
   if (JsonFileLoader<ML149Data>.LoadFile("$profile:MLBodyEditor_Right.json", rightBody, error))
   {
    if (ML149State.ValidData(rightBody))
     data.RightLean.BodySettings = rightBody;
   }
  }
  // All old files remain untouched as migration backups.
 }
 static void Init()
 {
  if (Initialized)
   return;
  ML144State.Init();
  ML149State.Init();
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
  ImportLegacy(bundled);
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
  Notice("Saved ALL F6/F7 settings and BOTH sides: MLLeanPreset.json");
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
