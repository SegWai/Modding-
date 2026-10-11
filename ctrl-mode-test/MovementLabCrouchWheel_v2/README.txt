CROUCH WHEEL MOMENTUM TEST V2

Extract entire ZIP to fresh folder, close DayZ, keep Steam running, run Launch-Movement-Test.cmd. Same local preparation as v1, originals unchanged.

Wheel sets target level; effective graph pace changes continuously while crouch movement is held. Downward rate 5 levels/sec: full level 5->1 about .80s; level 3->1 about .40s. Upward rate 10 levels/sec: 1->5 about .40s. Retargeting/spam never resets the current pace. Between level4 and5, native gait smoothly blends from1 to3 rather than switching abruptly. Existing graph blends adjacent clip groups continuously.

Selection and original Shift override retained; Shift still immediately requests fast crouch and returns to wheel pace on release. Idle/standing snaps the effective selection to its target because no moving momentum needs preserving. Standing/strafe rules retained. Wheel action-input conflict remains from v1; test away from interactable items.

Translated actual code tests passed at30/60/144FPS both callback orders, comparing .8s vs .4s deceleration, intermediate traversal and spam continuity. Native animation/root-motion blending remains for in-game confirmation. V1 remains available unchanged.
