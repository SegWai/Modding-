// Native item-in-hands behavior, not a gun classname/length allowlist.
class MLHeldCategory192
{
 // TWOHANDED alone is too broad: sledgehammers, axes and containers differ.
 static bool UsesBatHolding(PlayerBase actor)
 {
  if (!actor)
   return false;
  EntityAI item = actor.GetHumanInventory().GetEntityInHands();
  if (!item)
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior || behavior.m_iType != ItemBehaviorType.TWOHANDED)
   return false;
  // Native animation-instance query also covers modded items reusing this ASI.
  string animationInstance = actor.DebugGetItemAnimInstance();
  animationInstance.ToLower();
  if (animationInstance.Contains("player_main_2h_bat"))
   return true;
  // Known native registrations/subclasses if debug instance is not populated.
  return item.IsKindOf("BaseballBat") || item.IsKindOf("NailedBaseballBat") || item.IsKindOf("BarbedBaseballBat") || item.IsKindOf("XmasBaseballBat");
 }
 static bool UsesPistolHolding(PlayerBase actor)
 {
  if (!actor || !actor.GetHumanInventory().GetEntityInHands())
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior)
   return false;
  return behavior.m_iType == ItemBehaviorType.PISTOLS;
 }
 static bool UsesRifleHolding(PlayerBase actor)
 {
  if (!actor || !actor.GetHumanInventory().GetEntityInHands())
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior)
   return false;
  return behavior.m_iType == ItemBehaviorType.FIREARMS;
 }
};
