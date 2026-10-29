// One epoch for every preview: references warm while stationary, then walk.
class ML206LineupClock
{
 static int Epoch;
 static void Begin()
 {
  Epoch = GetGame().GetTime();
 }
 static bool Walking(int now)
 {
  return now - Epoch >= 12000;
 }
 static float Target(int now)
 {
  int elapsed = now - Epoch;
  if (elapsed < 3000)
   return 0;
  if (elapsed < 6000)
   return -1;
  if (elapsed < 9000)
   return 1;
  if (elapsed < 12000)
   return 0;
  if (ML214WeaponState.Open)
  {
   if (ML214WeaponState.EditLeft)
    return -1;
   return 1;
  }
  int phase = (elapsed - 12000) / 3000;
  if (phase % 2 == 0)
   return -1;
  return 1;
 }
};
