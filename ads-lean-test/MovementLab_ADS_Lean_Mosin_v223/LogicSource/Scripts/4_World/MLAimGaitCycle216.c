// Shared initial moving-reference calibration, then exact one-second targets.
class ML216AimGaitCycle
{
 static int Epoch;
 static void Begin()
 {
  Epoch = GetGame().GetTime();
 }
 static bool Moving(int now)
 {
  return now - Epoch >= 3000;
 }
 static float Target(int now)
 {
  int elapsed = now - Epoch;
  if (elapsed < 3000)
   return 0;
  if (elapsed < 6000)
   return -1;
  if (elapsed < 7000)
   return 0;
  if (elapsed < 10000)
   return 1;
  if (elapsed < 12000)
   return 0;
  if (ML216WeaponState.Open)
  {
   if (ML216WeaponState.EditLeft)
    return -1;
   return 1;
  }
  int phase = (elapsed - 12000) / 1000;
  if (phase % 2 == 0)
   return -1;
  return 1;
 }
};
