// Native item-in-hands behavior, not a gun classname/length allowlist.
class MLHeldCategory192
{
 // User explicitly approves the bat pose for the whole native two-handed category.
 static bool UsesTwoHandedHolding(PlayerBase actor)
 {
  if (!actor || !actor.GetHumanInventory().GetEntityInHands())
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior)
   return false;
  return behavior.m_iType == ItemBehaviorType.TWOHANDED;
 }
 static bool UsesOneHandedHolding(PlayerBase actor)
 {
  if (!actor || !actor.GetHumanInventory().GetEntityInHands())
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior)
   return false;
  return behavior.m_iType == ItemBehaviorType.ONEHANDED;
 }
 static bool UsesHeavyHolding(PlayerBase actor)
 {
  if (!actor || !actor.GetHumanInventory().GetEntityInHands())
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior)
   return false;
  return behavior.m_iType == ItemBehaviorType.HEAVY;
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
