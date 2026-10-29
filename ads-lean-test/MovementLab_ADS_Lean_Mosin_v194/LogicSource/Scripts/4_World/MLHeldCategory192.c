// Native item-in-hands behavior, not a gun classname/length allowlist.
class MLHeldCategory192
{
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
