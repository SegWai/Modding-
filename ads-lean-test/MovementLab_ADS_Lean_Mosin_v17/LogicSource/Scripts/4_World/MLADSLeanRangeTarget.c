// Offline designated target only. Reuses the earlier human range ragdoll takeover.
modded class PlayerBase
{
 protected bool m_MLADSLeanRangeTarget;
 protected EntityAI m_MLADSLeanRangeRifle;
 protected bool m_MLADSLeanRangeRagdoll;
 protected bool m_MLADSLeanRangeImpulseApplied;
 protected vector m_MLADSLeanRangeLastPosition;
 protected vector m_MLADSLeanRangeVelocity;
 protected vector m_MLADSLeanRangeDeathVelocity;
 protected int m_MLADSLeanRangeLastSample;
 protected bool m_MLADSLeanRangeMotionValid;

 void MLADSLeanEnableRangeTarget()
 {
  if (GetGame().IsMultiplayer() || GetGame().GetPlayer() == this)
   return;
  m_MLADSLeanRangeTarget = true;
  m_MLADSLeanRangeRifle = GetHumanInventory().GetEntityInHands();
  m_MLADSLeanRangeLastPosition = GetPosition();
  m_MLADSLeanRangeLastSample = GetGame().GetTime();
  PhysicsSetRagdoll(false);
 }
 void MLADSLeanRangeSampleMotion()
 {
  if (!m_MLADSLeanRangeTarget || GetGame().IsMultiplayer() || !IsAlive())
   return;
  int now = GetGame().GetTime();
  int elapsed = now - m_MLADSLeanRangeLastSample;
  if (elapsed < 80)
   return;
  vector velocity = (GetPosition() - m_MLADSLeanRangeLastPosition) / (elapsed * 0.001);
  m_MLADSLeanRangeMotionValid = elapsed <= 200 && velocity.Length() <= 8;
  if (m_MLADSLeanRangeMotionValid)
   m_MLADSLeanRangeVelocity = velocity;
  m_MLADSLeanRangeLastPosition = GetPosition();
  m_MLADSLeanRangeLastSample = now;
 }
 override void EEKilled(Object killer)
 {
  bool rangeDeath = m_MLADSLeanRangeTarget && !GetGame().IsMultiplayer();
  if (rangeDeath)
  {
   // Capture before native death can zero the movement controller.
   m_MLADSLeanRangeDeathVelocity = GetVelocity(this);
   if (m_MLADSLeanRangeMotionValid && GetGame().GetTime() - m_MLADSLeanRangeLastSample <= 200)
    m_MLADSLeanRangeDeathVelocity = m_MLADSLeanRangeVelocity;
   if (m_MLADSLeanRangeDeathVelocity.Length() > 8)
    m_MLADSLeanRangeDeathVelocity = "0 0 0";
  }
  super.EEKilled(killer);
  if (!rangeDeath)
   return;
  MLADSLeanStopDemo();
  DisableSimulation(false);
  PhysicsSetRagdoll(true);
  m_MLADSLeanRangeRagdoll = PhysicsIsRagdoll();
  if (m_MLADSLeanRangeRagdoll)
   MLADSLeanRangeTransferMomentum();
  else
   GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(MLADSLeanRangeRetryRagdoll, 50, false);
  Print("[MLADSLEAN17] target_killed ragdoll=" + m_MLADSLeanRangeRagdoll);
  MLADSLeanSettings.DemoKilled.Invoke(this);
 }
 void MLADSLeanRangeRetryRagdoll()
 {
  if (!m_MLADSLeanRangeTarget || GetGame().IsMultiplayer() || IsAlive())
   return;
  PhysicsSetRagdoll(true);
  m_MLADSLeanRangeRagdoll = PhysicsIsRagdoll();
  if (m_MLADSLeanRangeRagdoll)
   MLADSLeanRangeTransferMomentum();
  Print("[MLADSLEAN17] target_ragdoll_retry active=" + m_MLADSLeanRangeRagdoll);
 }
 protected void MLADSLeanRangeTransferMomentum()
 {
  if (m_MLADSLeanRangeImpulseApplied || !PhysicsIsRagdoll())
   return;
  m_MLADSLeanRangeImpulseApplied = true;
  float mass = dBodyGetMass(this);
  if (mass <= 0)
   return;
  vector delta = m_MLADSLeanRangeDeathVelocity - GetVelocity(this);
  // Preserve gravity/settling: transfer horizontal travel, never an upward kick.
  delta[1] = 0;
  float speed = delta.Length();
  if (speed > 8)
   delta = delta * (8 / speed);
  dBodyActive(this, ActiveState.ACTIVE);
  dBodyApplyImpulse(this, delta * mass);
  Print("[MLADSLEAN17] target_ragdoll_momentum velocity=" + m_MLADSLeanRangeDeathVelocity);
 }
 override bool HandleDeath(int pCurrentCommandID)
 {
  if (m_MLADSLeanRangeTarget && m_MLADSLeanRangeRagdoll && !GetGame().IsMultiplayer() && !IsAlive())
   return true;
  // Fall back to native death if articulated physics fails to activate.
  return super.HandleDeath(pCurrentCommandID);
 }
 void MLADSLeanRangeCleanup()
 {
  GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).Remove(MLADSLeanRangeRetryRagdoll);
  // Native death may drop the rifle outside the corpse hierarchy.
  // Clean up ground drops, but preserve any rifle the player picked up.
  if (m_MLADSLeanRangeRifle && !m_MLADSLeanRangeRifle.GetHierarchyParent())
   GetGame().ObjectDelete(m_MLADSLeanRangeRifle);
  m_MLADSLeanRangeRifle = null;
 }
};

class MLADSLeanRangeAmmo
{
 static void Refresh(PlayerBase player)
 {
  if (!player || GetGame().IsMultiplayer() || GetGame().GetPlayer() != player || !player.IsAlive())
   return;
  Weapon_Base weapon = Weapon_Base.Cast(player.GetHumanInventory().GetEntityInHands());
  if (!weapon || !weapon.IsKindOf("Mosin9130"))
   return;
  weapon.SetHealthMax("", "Health");
  ItemBase suppressor = weapon.GetAttachedSuppressor();
  if (suppressor)
   suppressor.SetHealthMax("", "Health");
  // Preserve the native bolt/FSM and chamber. Refill only the internal reserve.
  if (player.GetWeaponManager() && player.GetWeaponManager().IsRunning())
   return;
  int muzzle = weapon.GetCurrentMuzzle();
  int maximum = weapon.GetInternalMagazineMaxCartridgeCount(muzzle);
  int current = weapon.GetInternalMagazineCartridgeCount(muzzle);
  string ammo = weapon.GetRandomChamberableAmmoTypeName(muzzle);
  if (ammo == "")
   return;
  for (int i = current; i < maximum; i++)
  {
   if (!weapon.PushCartridgeToInternalMagazine(muzzle, 0, ammo))
    break;
  }
 }
};
