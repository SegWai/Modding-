class ML174PresetFile
{
 int PresetVersion = 2;
 ref ML153SidePreset LeftLean;
 ref ML153SidePreset RightLean;
 ref ML153SidePreset LeftArmZero;
 ref ML153SidePreset RightArmZero;
};
class ML174ArmZero
{
 static ref ML153SidePreset LeftBase;
 static ref ML153SidePreset RightBase;
 static bool IsArm(string name)
 {
  return name == "LeftShoulder" || name == "LeftArm" || name == "LeftForeArm" || name == "LeftHand";
 }
 static ML153SidePreset Base(bool left)
 {
  if (left)
   return LeftBase;
  return RightBase;
 }
 static ML144Values BuildArmWeaponValues(ML144Values input, ML153SidePreset basis, float direction)
 {
  ML144Values result = new ML144Values;
  result.X = input.X;
  result.Y = input.Y;
  result.Z = input.Z;
  result.Pitch = input.Pitch;
  result.Yaw = input.Yaw;
  result.Roll = input.Roll;
  result.LeftPitch = input.LeftPitch;
  result.LeftYaw = input.LeftYaw;
  result.LeftRoll = input.LeftRoll;
  result.RightPitch = input.RightPitch;
  result.RightYaw = input.RightYaw;
  result.RightRoll = input.RightRoll;
  result.HeadPitch = input.HeadPitch;
  result.HeadYaw = input.HeadYaw;
  result.HeadRoll = input.HeadRoll;
  result.MuzzleYaw = input.MuzzleYaw;
  result.MuzzlePitch = input.MuzzlePitch;
  result.LeftPitch = result.LeftPitch + basis.WeaponSettings.LeftPitch * direction;
  result.LeftYaw = result.LeftYaw + basis.WeaponSettings.LeftYaw * direction;
  result.LeftRoll = result.LeftRoll + basis.WeaponSettings.LeftRoll * direction;
  return result;
 }
 static ML149Data BuildArmBodyValues(ML149Data input, ML153SidePreset basis, float direction)
 {
  ML149Data result = new ML149Data;
  for (int i = 0; i < input.Parts.Count(); i++)
  {
   ML149Part original = input.Parts[i];
   ML149Part part = new ML149Part;
   part.BoneName = original.BoneName;
   part.X = original.X;
   part.Y = original.Y;
   part.Z = original.Z;
   part.Pitch = original.Pitch;
   part.Yaw = original.Yaw;
   part.Roll = original.Roll;
   if (IsArm(part.BoneName))
   {
    ML149Part armBase = basis.BodySettings.Parts[i];
    part.X = part.X + armBase.X * direction;
    part.Y = part.Y + armBase.Y * direction;
    part.Z = part.Z + armBase.Z * direction;
    part.Pitch = part.Pitch + armBase.Pitch * direction;
    part.Yaw = part.Yaw + armBase.Yaw * direction;
    part.Roll = part.Roll + armBase.Roll * direction;
   }
   result.Parts.Insert(part);
  }
  return result;
 }
 static bool ValidBase(ML153SidePreset basis, bool left)
 {
  if (!basis || !basis.WeaponSettings || !ML149State.ValidData(basis.BodySettings))
   return false;
  array<float> checked = new array<float>;
  return ML144State.Validate(basis.WeaponSettings, left, checked);
 }
 static bool Prepare(ML174PresetFile data)
 {
  if (!data)
   return false;
  if (data.PresetVersion == 2)
   return ValidBase(data.LeftArmZero, true) && ValidBase(data.RightArmZero, false);
  if (data.PresetVersion != 1 || !data.LeftLean || !data.RightLean)
   return false;
  // Old absolute saves migrate against the exact uploaded pose, once.
  if (!ValidBase(data.LeftLean, true) || !ValidBase(data.RightLean, false))
   return false;
  ML153PresetFile uploaded;
  string error;
  if (!JsonFileLoader<ML153PresetFile>.LoadFile("MLADSLeanLogic/Presets/MLWalkingArmBaseline.json", uploaded, error))
   return false;
  if (!uploaded || !ValidBase(uploaded.LeftLean, true) || !ValidBase(uploaded.RightLean, false))
   return false;
  data.LeftArmZero = uploaded.LeftLean;
  data.RightArmZero = uploaded.RightLean;
  data.LeftLean.WeaponSettings = ML174ArmZero.BuildArmWeaponValues(data.LeftLean.WeaponSettings, data.LeftArmZero, -1);
  data.RightLean.WeaponSettings = ML174ArmZero.BuildArmWeaponValues(data.RightLean.WeaponSettings, data.RightArmZero, -1);
  data.LeftLean.BodySettings = ML174ArmZero.BuildArmBodyValues(data.LeftLean.BodySettings, data.LeftArmZero, -1);
  data.RightLean.BodySettings = ML174ArmZero.BuildArmBodyValues(data.RightLean.BodySettings, data.RightArmZero, -1);
  data.PresetVersion = 2;
  return true;
 }
};
