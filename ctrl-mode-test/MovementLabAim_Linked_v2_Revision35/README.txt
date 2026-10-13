Immediate Scroll Targets v2 — based on user-confirmed all-pose smoothing v1.
Standing upward ladder: walk~85,walk100,walk120,jog80,jog100,sprint100.
Prior downward boundary retained: jog80 -> defaultwalk~85 (notwalk120).
A wheel burst can select any target across mode boundaries in one update.
Crouch ladder remains30/~47/60/~73/~87/nativefast.
Raw signed wheel delta counted; common120-unit deltas normalized, action press fallback.
Animations/acceleration blend toward the stored target after scrolling stops.
No need to wait for animation completion before selecting another speed.
Pending input during temporary native command restrictions is applied when eligible;
menus/pause/stance changes clear pending input. Clamp at ladder endpoints.
Physical held Shift still overrides current gait; target selection is retained.
No graph/clip/brake/pose timer changes from confirmed all-smoothing package.
Close DayZ, extract ZIP, run Launch-Movement-Test.cmd.
Native wheel sign/units/focus and visual pacing require local test; logs record raw steps.
Default confirmed PoseExit v2 and previous all-smoothing package stay preserved.

Revision35: jog100 -> fast aim native100; fast aim100/120 -> jog100 on lowering. Fast aim80 -> jog80. Fast aim level2 now uses original native animation sources. Entry Shift latch initialized from held input.

Sprint -> aim enters exclusive fast aim140% (42FPS), smoothly falls to native100% over1.5s. Wheel events during transition are discarded. Normal wheel levels remain80/100/120. Crouch/slow aim unchanged.

Revision35 captures recently achieved sprint before weapon raise clears it. Exclusive140% entry applies to IsWeapon projectile weapons only. F8 must be custom/OFF to see custom speeds.

Revision35: sprint-entry fast aim140 ->100 slowdown duration1.5s; handoff allowance remains0.25s. Wheel locked until complete.

Revision35: exclusive140% aim requires1 continuous second achieved upright sprint gait>=2.99. Lowered slowdown/stopping/crouch/menu resets qualification. Acceleration/Shift/sprint selection alone never qualifies. Existing1.5s decay and0.25s maximum handoff retained.

Revision35: sprint qualification gait>=2.9 plus active sprint request for1 continuous second. Offline unlimited stamina/load cap; black tactical gear and smaller42-slot black assault backpack, two weapon attachments retained. Every launch spawns atNWAF (4610,10180).1.5s aim decay unchanged.

Revision35: qualified sprint-to-raise grace1s (still resets immediately on lowered slowdown); additional gate logs. Intended NWAF runway spawn4500/10300.5 stationary damageable targets,10m spacing, respawn3s after death forever.140% visible speed remains under investigation; send logs.

Revision35:140->100 decay restored0.5s. Exactly5 targets total (one per slot),10m spacing along airfield pavement; spawn search checks60m paved line. Initialization guarded against repeatedOnInit.3-second recurring respawn retained.

Revision35: pavement vector multiplier nowfloat (native compile fix). Full-sprint qualification uses achieved gait, accepts upright0/3 before raise, does not require heldShift/native cleared input.1s eligibility and0.5s decay retained.

Revision35: workingRevision17 sprintgate preserved; onlyaimdecay changedto1.5s. Offline range removesuntracked extra survivorswithin100m onstartup/every1s, preservingcontrolledplayerandfive assignedtargets; live-slotspawn guarded. This cleanup islimitedtothetestmission.

Revision35: aim140->100 decay1second. ALLrangeNPCspawning/respawn/cleanupremoved. Onlycontrolledplayercreated. Blackgear/unlimitedstamina/pavedairfieldspawnretained.

Revision35:140->100 slowdown1.5seconds. Revision19gate/handoff/loadout/pavedspawn/noNPCsretained.

Revision35: late-sprint entryqualifiesatnativegait>=2.7sustained0.35s; belowthresholdresets. Normaljogging/shortsprinttapdonotqualify.140->100decayremains1.5s. NoNPCs.

Revision35 standingcontrols:Shiftpressselectsjog2/native100; doubleShiftwithin250msselectssprint; Shiftfromsprintselectsjog2; Ctrlalwaysselectswalk1/80%,repeatCtrlneverjogs. Wheellinkingunchanged. Aiming/crouchcontrolsretained.1.5sboostretained.

Revision35 slowaimL1=60%(wheelonly),L2=80%,L3=original100%. Walk1->aim2;Walk2->aim3;Ctrlfromfastaim->slowaim3. Lowergunreturnswalk1/80. LeftAltquicktap<=200ms togglesADS/hipfire. ShiftdoesnotrequestADS; standingShiftbindingsretained; heldAltfreelookretained.

DoubleShift<=250ms whileaim/ADS exitsights,lowersgun,standsupifneeded,andselectsfullsprint. RMBheldblockeduntilreleasedafterlowering.

Revision35:walkingL1~73%(22FPS). SlowaimL1~53%(16FPS),L2~93%(28FPS),L3~113%(34FPS);walk1->aim2,walk2->aim3. Jog/sprint->walk return uses1.5ssmoothstep,withoutstagedplateaus. Fullstoplogicunchanged. AltADS/doubleShiftretained.

Revision35 slowaimrequested55/100/150; wholeFPS17/30/45 produces56.67/100/150. Entrywalk1->aim2,walk2->aim3andallcontrolsunchanged.

Revision35 MomentumFade:jog2->crouch6nativefastpose->crouch5~87over1.5s,smoothstepgait+pose. Wheelignoredduringfade. Ordinarycroentry/jog1/sprintentryunchanged.

Revision35:hiddencro7target95%fastcroplayback(blend28/29FPS),onlyjog2orfullsprintentry;1.5smomentumfadeto5. Notwheelpickable; normalmanual6native100remains. Originalarmedfastcrofootmotionsretimed,gunposeunchanged.

Revision35:fixalphabeticalanimsettemplategrouporder; hiddenmomentumgroupnowbeforeCrouchSpeeds/StandingWalk. NativeRevision30logsidentifiedsixunresolvedhiddenclipIDs. Controllers/ratesunchanged.

Revision35:jog1->hidden8(same95%fastpose)->cro4~73over1.5s. Jog2/sprint->hidden7->cro5unchanged. Hidden8wheelunreachable; reuseexistingvalidsortedtemplate/rateclipgroups.

Revision35:cro4->aimcro4andcro5->aimcro5. Otheraimcroentrydefault60/3unchanged. Allspeedrates/bindings/fadesunchanged.

Revision35:selectablecro30/47/60/87(default4)/nativefast100(level5);aimcro30/47/60/87(default4). Selectable73removed; originalprofileclipsmayappearonlyduringcontinuousblending. Bothhiddenentryfadesnowend4/87. Stationarycrodefaults4,nofade. NativeADSrequestclearedinHandleADS/CameraHandler;LeftAltstilltogglesADS.

Revision35:five-stepHUDindicatorbesidenativesound/stancewidgets; standingwalk1/2,jog3/4,sprint5. Aim/croshowselectedmodelevel; automaticfadesgoldAUTOshowdestination. Pronenative1. FollowHUDvisibility. Allmovementunchanged.
