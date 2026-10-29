// Data-bank choice is actor gait, not actor identity or camera.
class ML181PoseRouting
{
 static bool WalkingBank(int stance, int movement)
 {
  bool upright = stance == DayZPlayerConstants.STANCEIDX_ERECT || stance == DayZPlayerConstants.STANCEIDX_RAISEDERECT;
  return upright && (movement == 1 || movement == 2);
 }
};
// Both demos read the same clock. Each target lasts exactly one second;
// ordinary lean interpolation runs inside that interval.
class ML181CrouchCycle
{
 static int Epoch;
 static void Begin()
 {
  Epoch = GetGame().GetTime();
 }
 static float Target(int now)
 {
  if (ML193WeaponState.Open)
  {
   if (ML193WeaponState.EditLeft)
    return -1;
   return 1;
  }
  int elapsed = now - Epoch;
  if (elapsed < 0)
   elapsed = 0;
  int phase = elapsed / 1000;
  phase = phase % 4;
  if (phase == 0)
   return -1;
  if (phase == 2)
   return 1;
  return 0;
 }
};
