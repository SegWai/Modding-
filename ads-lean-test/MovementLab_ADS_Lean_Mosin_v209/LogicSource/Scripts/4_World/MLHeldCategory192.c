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
 // Native SMGs do not share a unique ItemBehaviorType or script base class.
 // Use verified native SMG families; inherited modded subclasses follow them.
 static bool IsSMG(EntityAI item)
 {
  if (!item || !Weapon_Base.Cast(item))
   return false;
  if (item.IsKindOf("MP5K_Base") || item.IsKindOf("UMP45_Base"))
   return true;
  if (item.IsKindOf("CZ61_Base") || item.IsKindOf("PM73Rak_Base"))
   return true;
  return item.IsKindOf("PP19_Base") || item.IsKindOf("MP18_Base");
 }
 static bool UsesPolearmHolding(PlayerBase actor)
 {
  if (!actor || !actor.GetHumanInventory().GetEntityInHands())
   return false;
  HumanItemAccessor accessor = actor.GetItemAccessor();
  if (!accessor)
   return false;
  HumanItemBehaviorCfg behavior = accessor.GetItemInHandsBehaviourCfg();
  if (!behavior)
   return false;
  return behavior.m_iType == ItemBehaviorType.POLEARMS;
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
