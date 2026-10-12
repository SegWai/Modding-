# Crouch wheel timing investigation

Working version: `ctrl-mode-test/MovementLabCrouchWheel_v1/` and
`artifacts/MovementLab_Crouch_Wheel_Test_v1.zip`.
User confirmed v1 works. Preserve it unchanged. SHA256:
`673289da814f1f89495b6d0f98b893c0799aa4031e9f0cca635144dc37e10f1e`.
V2 and v3 slowdown experiments were rejected for visibly jumping motion.

## Verified findings

- Six supplied ANM clips contain an explicit integer FPS chunk (30 originally).
  Retimed variants use 6, 14, 18 and 24 FPS, plus native fast crouch at level5.
  This changes file timing before launch; it is not live animation rate control.
- The supplied AST defines animation groups/slots. The ASY defines contact
  phases. Neither exposes a live playback-rate parameter in the supplied text.
- Supplied locomotion graph uses AnimNodeSourceSync and a Walk sync line.
  Our wheel implementation selects group mappings through AnimNodeBlendN.
  Changing the selector changes which retimed source is used.
- The inspected Human/HumanCommandMove/DayZPlayer scripting interfaces expose
  gait override, animation graph variable writes and script-command translation
  hooks, but no documented direct player-clip playback-rate setter.
  HumanCommandScript.PreAnimUpdate is a script-command callback, not evidence
  of a native movement command's playback-rate control. Passing a smaller
  CommandHandler timestep does not prove that the engine animation clock changes.
- User screenshots show clip events/contact markers in Animation Editor.
  That panel is not the graph-node property interface. Asking for those clip
  properties did not establish a timing control.
- V3 crouch slow test RPT showed 258 missing original unarmed resources.
  User subsequently confirmed the complete-folder local repack resolved this.
  This asset-loading fix is distinct from phase continuity during wheel changes.

## Unresolved

The precise cause of motion discontinuity is unmeasured. Source changes,
normalized phase synchronization, native fast/slow gait transitions and reuse
of a common subtree under multiple group contexts are candidates; none is a
confirmed diagnosis from a native graph trace.

A smooth selector, ordered integer stages, source cross-fades and script mock
passes are not proof that native clip phase or physical root motion is smooth.
The user rejected both tested smoothing approaches. Do not reissue them as fixes.

No supported time-warp node or native API has yet been established. Absence in
these supplied files does not prove the engine lacks one. Official DayZ-specific
node documentation or graph-editor node controls are needed before implementing
an assumed node type/property. A Bohemia wiki request returned proxy/tunnel
403 Forbidden in this environment; no page content was retrieved.

## Next justified experiment, if timing controls become available

Keep a continuous source cycle, ease its phase advancement/playback rate while
preserving foot-contact phase, and ensure root-motion translation follows the
same clock. Native fast-to-slow crouch also needs a gait blend. Test phase,
foot placement and measured horizontal travel at each transition in DayZ.
Do not invent a graph-node type, scale the whole game clock, repeatedly reload
clips, freeze poses, or claim native verification from C++ translation tests.

The initial inspection did not justify another rate-selector-only package.
The subsequent native timed-blend investigation below supports a separate
experiment; working v1 and stable standing movement remain unchanged.


## Follow-up: timed pose transition experiment (v4)

Official DayZ-Samples and DayZ-Misc repositories were inspected. They provide
sample assets/rigs but no located runtime player playback-rate example. The
StarDZ-Team/DayZ-Modding-Wiki animation chapter describes graph-variable
bindings, not a verified live player clip-rate setter. These searches do not
establish that such an engine capability is impossible.

The supplied native graph provides a concrete alternative to a playback-rate
setter. `WalkRunBlendT` uses `AnimNodeBlendT`, conditions around gait 2, a 0.3
transition value and `"S" 7` fields. This is the standing/ADS path, not the low
crouch path: `CroVar` reaches `CroRunSprintBlend`, a plain `AnimNodeBlend`
between `WalkBlendSTM` and `SprintCyclic`. Walk sources use the `Walk` sync
line while run/sprint sources use `RunSprint`. It is therefore incorrect to
assume the standing timed transition already smooths every wheel change.

V4 replaces only the added wheel `AnimNodeBlendN` selector with four nested
`AnimNodeBlendT` nodes using the native example's condition/field structure,
0.18-second transition values and tier thresholds 1.5, 2.5, 3.5 and 4.5.
Moving downward effective pace crosses each threshold at five levels/second.
Upward selected pace changes immediately as in v1; the new graph transitions
can nevertheless alter upward visual behavior, which needs comparison.
Original downstream graph, AST, ASI, root graph, local preparer and mission
are identical to the previous working assets. Standing script methods remain
unchanged; crouch downward pacing derives from v2. This differs materially
from rejected fractional BlendN blending and staged instant source selection.

The meanings of native numeric flags are not independently documented here;
the existing supported serialization was reused rather than inventing fields.
Shared-subtree caching, source activation and phase preservation remain
unverified. Timed pose blending is a testable alternative, not a confirmed fix
or a guarantee of continuous animation-clock scaling.

Validation: translated actual controller tests passed at 30/60/144 FPS and both
callback orders, including downward intermediate traversal, rapid retargeting,
Shift and stable standing/strafe regressions. Structural checks ensure the
only graph change is the new timed selector and retained native resources are
byte-identical. PBO records/source bytes/checksum and ZIP integrity pass.
Native Enforce compilation, graph interpretation and foot-contact continuity
cannot be verified in this Linux environment and require the supplied DayZ
launcher test.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Test_v4.zip`.
SHA256: `00b73f7cb53753ee4ff648a3d89b246091d5b4e697dff5a0dfaf3f566f061954`.
Rollback: close DayZ and run the existing original v1 launcher folder. Neither
preparer writes the original DZ assets.


## V5: user-requested hidden 90% A/B bridge

Separate package, F8 defaults OFF. The v4 four-tier timed selector is retained
under `CroWheelNormalG`; a new outer timed blend uses a transient float variable
`MovementLabHidden90` to select `CroHidden90G`. Its added Locomotion group copies
all CroWheel4 mappings, changing only six walk paths to H90 variants retimed to
27FPS (90% of original slow-crouch 30FPS). This does not establish 90% of measured
native fast-crouch velocity; level5 is a different native gait. Existing native
gait interpolation is retained during bridge entry/exit.

Only a moving, eligible crouch scroll-down from selected level5 with effective
pace at least4.95 starts the bridge. .10s entry, .10s hidden stage, .10s exit;
lower queued targets resume existing v4 deceleration afterward. Further downward
scroll never resets or skips the stage. Upward scroll, Shift, no directional
input, ineligible stance, or F8 OFF cancels it. The hidden stage never changes the
selected integer wheel level, is never directly selectable and cannot persist.
OFF adds an inactive graph wrapper but retains the original v4 controller path;
initial activation/transition interpretation of the wrapper remains native-test
pending. F8 toggles only this experiment; existing F7 remains separate.

Validation: actual translated default-OFF controller regressions and new bridge
cases passed at30/60/144FPS, both callback orders. Complete added group mappings,
15-group AST count, quote-aware graph/table brace balance, six supplied ANM
27FPS-only retiming checks, PBO contents/footer and ZIP integrity passed.
Windows preparation, native Enforce compilation, measured travel and visual
foot-contact continuity remain unexecuted here. Original v1 and v4 unchanged.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Test_v5.zip`.
SHA256: `e0b24bb92428ed6429dad7419c7b64a0f85f2b93435e83791e477702304b5a41`.


## V6: regression after v5 native-speed test

User reported a frozen pose at level5 in both F8 OFF and ON, narrowing this
beyond activation of the hidden stage. Both states still use v4's nested timed
selectors and v5's outer timed wrapper. The actual engine failure mechanism is
not established by a still screenshot or script mock.

Checked Cro and CroWheel5 mappings: same28 slots, including original native
SprintF/FL/FR and Aim resources. All downstream locomotion nodes after the new
header are byte-identical to user-confirmed v1. This rules out a changed run
clip mapping in those checked slots; it does not prove all runtime assets loaded.

V6 removes the experimental nested timed selector chain and outer timed wrapper.
It restores v1's wheel BlendN selector under CroWheelNormalG. A short continuously
weighted BlendN wrapper adds the hidden27FPS stage with0.10s ramp in,0.10s hold,
0.10s ramp out. Five selectable tiers, downward-only trigger, cancellation,
standing controller and original asset preservation remain unchanged. F8 OFF
now compares this restored selector with the existing downward controller pace,
not v4's rejected timed graph. Original v1/v4/v5 packages remain unchanged.

Translated actual controller and hidden-stage tests passed at30/60/144FPS,
both callback orders. Structural tests verify no new timed selector remains
in the header and all original downstream graph nodes remain byte-identical.
Package PBO/source/footer and ZIP integrity pass. User must first verify native
level5 animates with F8 OFF; correction is not yet native-confirmed. If it still
freezes, use original v1 and inspect v6 RPT/script asset/binding output next.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Test_v6.zip`.
SHA256: `1547fd3894016d96f0b67654facf74677e97ee5aded55043776de0cc6f73f2f4`.


## V7: v6 also reported frozen, isolate against exact original

User confirmed v6 still freezes with both F8 states. No native runtime trace
has been supplied, so neither the timed-selector hypothesis nor the v6 change
is a confirmed fix. V6 still added a nested selector wrapper; v5/v6 inserted
CroHidden90 between existing CroWheel5 and CroRas group names. Those are two
remaining differences from v1, not established engine failure causes.

V7 removes every extra selector wrapper, restoring the exact v1 locomotion
text except one additional input4.5 and its GroupSelect. Original group names
retain their order, and CroHidden90 is appended. F8 OFF now feeds original
integer levels and snaps the gait pace to match v1, so an OFF test no longer
silently retains rejected fractional slowdown behavior. ON retains downward
bridge entry/hold/exit and lower-target pacing. The added unused graph slot and
group still mean OFF assets are not byte-identical to v1, hence the control.

The package includes KnownWorkingV1, a byte-identical copy of every file in
original v1, with its own launcher, script PBO, workspace patches, preparer and
profile folder. Top-level Launch-Known-Working-v1.cmd launches it separately;
DayZ must be closed before switching. A same-package control separates native
runtime/local-source regressions from the hidden experiment. If v1 works but
v7 fails, collect the latter's logs. If both fail, inspect runtime assets/input
state/logs before more graph experimentation.

Translated v1 OFF regressions and hidden controls pass30/60/144FPS in both
callback orders. Structural checks reconstruct exact original locomotion after
removing only added slot/node and reconstruct exact AST after removing appended
group/count increment. Control files are all byte-verified against original v1.
PBO/ZIP packaging checks pass. Native compilation and visual result pending.
Collect-Logs.cmd/ps1 packages this test folder's RPT/log files for next diagnosis.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Test_v7.zip`.
SHA256: `1042c4724648bc18be131248b61bd5ca2190c5b23985d1cb0f262b2f698df674`.


## V8: first current runtime evidence and schema repair

Uploaded `DayZDiag_x64_2026-10-11_11-52-48.RPT` is explicitly a v7 launch, not
KnownWorkingV1. It contains1206 missing-source-ID messages (323unique IDs),
including native CroRas/Erc/Pne/Water groups and added CroWheel2..5 mappings.
Graph initialization reports `CroWheel5G:Invalid columnLocomotion` and invalid
Locomotion columns for numerous original graph nodes. The wheel variable binds
and script log reaches levels2,3,4,5. These logs establish invalid runtime
animation-table resolution; they do not show a measured clip-time discontinuity
or identify a single verified native parser rule causing all failures.

The v5-v7 hidden ASI rows are outside `$animations`, before the outer instance
closing brace. This was our concrete generation error, missed by brace balance
and raw string-presence checks. V8 adds structural block-scope validation.

V8 restores the native Locomotion template to exactly its original ten group
names and58slots. A sorted, separately appended column
`ZZMovementLabCrouchSpeeds` defines H90/L2/L3/L4/L5 groups with those58slots.
28 native Cro assignments are duplicated into each group (140 mappings), all
inside the ASI `$animations` block. The root ASI and AGR use an explicit patched
template path. No native source-ID assignments are removed or redirected.

33 crouch dependency nodes are cloned; their healthy Locomotion source IDs use
the new column, while native injury column references remain intact. Levels2..4
and the hidden stage select this subtree with their new column groups. Level5
now selects original `CroMoveLowInjG`, native Locomotion/Cro directly; its native
run playback does not depend on added column resolution. The added L5 mapping
is currently unused. Existing native graph nodes remain intact. Standing and
wheel controller methods are unchanged from v7; F8 behavior remains.

Validation now parses group/slot counts, sorted group names, every ASI source-ID
against declared table schema, every custom mapping's block placement, cloned
node uniqueness/references and custom-source slot coverage. Native original
mappings remain present. Actual translated OFF/ON controllers and regressions
pass30/60/144FPS both orders. PBO/footer/ZIP checks pass. No DayZ engine or native
Enforce compiler is available here; engine acceptance and visual repair need
user playtest. This is a log-driven repair test, not a confirmed runtime fix.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Test_v8.zip`.
SHA256: `58c59ee63bcbd356c7cbef6f5021a197a54a3e1699a2dfb3bfd5974d069755f6`.
Uploaded logs remain outside the Git repository; earlier working archives unchanged.


## User-requested six-level speed revision

Separate `MovementLabCrouchWheel_SixLevels` test changes selectable levels to
30%,46.67%,60%,73.33%,86.67% of normal slow crouch, followed by original native
fast crouch as level6.9/14/18/22/26FPS timing realizes the first five values.
Level2 remains the previous rounded47%;22 and26FPS approximate requested73/87.
The native fast gait is a separate gait, not100% of normal slow crouch.

Controller/mission derive directly from v1: clamp maximum6, status /6, Shift
requests6, selected6 owns native fast gait and fast-crouch exit logic. No momentum,
hidden-stage or F8 code is included. Existing standing/strafe behavior retained.
Asset routing uses the v8 separate-column repair: original native Locomotion
unchanged; new four groups L2..L5 and matching cloned sources; level1 and level6
use native Cro sources (walk retimed9FPS, native fast clips unchanged). This
includes unconfirmed native asset-repair behavior and is explicitly a test,
not a newly approved stable version. Original v1 package/source untouched.

Translated actual six-level selection/clamps/Shift/persistence and stable
controller regressions passed30/60/144FPS both orders. Structural schema checks
verify112 extra mappings inside animations, four declared extra groups, original
native mappings retained and33 cloned source nodes. Package checks pass; native
Enforce/DayZ/Windows preparation remain user-side verification.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Six_Levels.zip`.
SHA256: `ec112e729f5b3b604a297f0f6736fc4ab087c4c45834b8fa2a3d5e745487a027`.


## Six-level v2: source retention during87%-to-native handoff

Uploaded `DayZ 2026-10-11 18-44-43 (online-video-cutter.com).mp4` is a3.237-second
excerpt. Entire excerpt inspected with sampled frames; crouched leg pose lingers
before movement resumes. It does not contain an absolute1:50 timestamp or
telemetry demonstrating a specific native gait/filter value. No new runtime
RPT was provided with this recording.

Source inspection identifies a plausible fallback: previous selector switches
from L5 custom walk26FPS directly to native Cro, whose walk clip has been retimed
to9FPS for level1. `CroRunSprintBlend` uses walk while filtered MovementSpeed is
at/below2 and blends native crouch run above2. If the engine gait is still
building after the override request3, selecting native Cro exposes9FPS walk
before fast gait completes. This is a code-path hypothesis, not a measured
native trace of the recording. Deactivating/restarting the alternate subtree
can also affect continuity.

V2 changes exactly one graph input: selector6 now references CroWheel5G, as
selector5 does. L5 walk remains26FPS until native gait3 activates the unchanged
original native SprintF/FL/FR mappings. Script still clamps1..6 and requests
native3 at6/Shift; all script, mission and clip-preparer bytes are unchanged.
No speed percentage, controller timing or standing rule changes. Old Group6
remains unused. The shared node avoids both immediate9FPS fallback and a
selector-induced activation of a different native subtree at5->6.

Actual translated six-level controllers/regressions and schema checks pass;
structural differential proves a single graph-line change and verifies L5 fast
clips exactly match native Cro run references. Native animation/filter behavior
and measured travel remain user playtest pending. Previous packages unchanged.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Six_Levels_v2.zip`.
SHA256: `ce0f372dbe365ca41d075003fd577c12a069f8250a0b14b308dc32f5cf28f4ef`.


## Six-level v3: reset entry to60%, except standing full sprint

User requests every new crouch session default60%, independent of prior crouch
speed; walking/jogging/idle entry all select3. Full standing sprint entry selects
native6 (chosen from user's90% or100% option). A separate stance edge records
last upright native gait>=2.90 on COMMANDID_MOVE. It preserves evidence through
upright transition commands and avoids counting the first upright sample after
fast crouch as a standing sprint. Initial saved level and graph default are3.
On first crouch frame saved choice resets3/6, then wheel inputs apply normally.
Holding Shift still temporarily overrides to native under existing crouch rules;
a Shift tap before achieved standing sprint does not change saved entry default.

Changes confined to wheel-entry tracking/default, entry status message and root
variable initial default. All other original world methods are verified identical
to six-level v2, mission/preparer identical, locomotion handoff unchanged. Crouch
exit behavior (fast exits jog, slow preserves standing mode) remains unchanged.

Translated actual controller tests at30/60/144FPS both orders exercise all prior
wheel choices1..6 against upright gait0/1/2/2.5/2.89/3, session persistence, repeated
entries, first-upright fast-crouch contamination and short Shift taps. Stable
standing/strafe and wheel/schema/package checks pass. Native compile/visual tests
remain user-side confirmation; no new stable approval claimed.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Six_Levels_v3.zip`.
SHA256: `21038e24fba7c0fe03bb591a57c4bcb3890a9f6ccbd378dae079bf5ac4b0ae09`.


## Six-level v4: consistent held-Shift request

User confirms v3 works but crouching while holding Shift+direction sometimes
remains normal60%. Source inspection shows saved wheel-native6 explicitly owns
gait3, while held Shift at another saved level merely disables our slow override
and relies on native input behavior. No current native runtime input trace
establishes whether Turbo filtering, standing walk intent or another mechanism
caused the report.

V4 replaces the explicit-fast condition with `moving && shift`, where local
`shift` already includes physical Turbo action or saved wheel6. This explicitly
requests gait3 for both sources. Idle/blocked eligibility remain unchanged,
releasing Shift returns to saved tier unless saved6, and crouch-exit standing
rules remain intact. Standing/mission/source profiles/graph/FPS/preparer bytes
are identical to v3. It does not latch fast crouch after input release.

Translated actual-code checks pass30/60/144FPS both callback orders. Added mock
cases suppress native Turbo interpretation while leaving input held: fast gait
remains3 for default60% entry, both standing modes, eight directional key masks,
Ctrl-held cases and wheel retargeting. Shift release restores saved tier; saved6
still fast without Shift; no movement releases override. Existing tests updated
to expect owned fast override, rather than native-bypass ownership. Controller
entry/standing/strafe/schema/PBO/ZIP checks pass. Native runtime still pending.

Artifact: `artifacts/MovementLab_Crouch_Wheel_Six_Levels_v4.zip`.
SHA256: `bfee1d3ff3f45fdb38baee99eb6f33379d7ccaf582147265150b0eae3bb0544d`.

## User approval: preserved best version (2026-10-11)

User requested: “save this as the best version till now. dont delete this one from logs”.
Six Levels v4 is now the approved baseline for subsequent work. Preserve its
source, artifact, and this investigation history; make future tests separately.
The preserved package is pinned to commit `1eb9e67`, with the SHA256 above.
This records user approval; cloud validation remains the local checks described
above, rather than a native runtime test performed in this environment.

## Standing walking half-pace F8 experiment

Separate from preserved best Six Levels v4. Six healthy standing Walk source
nodes now select between original source and a custom-column GroupSelect wrapper.
The wrapper uses `ZZMovementLabStandingWalk.Half` with six direction slots and
separate 15 FPS clips prepared from original 30 FPS standing walk files. Native
mapping rows and every pre-existing table column remain unchanged; the new
column is appended in sorted order. Selection is masked to erect stance in the
graph, so shared native crouch sources retain their original pace. Script binds
an independent float and F8 toggles a static test flag, OFF by default. F7 vanilla
comparison disables the flag's graph effect. Movement gait requests remain
unchanged: root-motion displacement per frame is preserved, while playback
frequency is halved, targeting matched animation and travel speed. Existing
walk portions during acceleration/braking also use half pace. Jog/sprint clips
and crouch variants are unchanged. Raised/injured alternatives are outside the
healthy standing walk comparison; mid-step toggling may reset phase once.

Validation: every baseline movement method except the added graph binding in
CommandHandler is byte-preserved, as are mission methods except OnKeyPress.
Actual variant controller translated to C++ passed baseline regressions plus
separate-binding/F8 selection checks at30/60/144FPS, both callback orders. New
column counts/order, six mapping scopes, six selectors, baseline node preservation
and FPS-only byte mutation on an actual supplied ANM pass. Windows preparation,
native DayZ compilation, actual root-motion speed and foot contact are pending.
The approved v4 ZIP checksum remains unchanged.

Artifact: `artifacts/MovementLab_Standing_Walk_Half_Speed_Test_v1.zip`.
SHA256: `5923d1ba5fc750cbc83df733d5ce04348451fe7132ea06de20f0681aa09ae5d3`.

## Standing walk three levels v1 (separate version)

User requested removing F8 and walking levels70/85/100, default70 and crouch-exit70.
Created separate source/package; previous F8 test and approved Six Levels v4
remain unchanged. No F8 flag, input handler or animation variable remains.
Walking selection defaults1 and clamps1..3, scrollable only when standing in
walking mode without Shift and under the existing local-player/menu/command
eligibility checks. Crouch retains its independent wheel handler. On a crouch
to upright edge, standing walk selection resets1 before graph update; same-frame
standing wheel input is ignored so the exit remains70%. Existing crouch-exit gait
mode rules are retained; this resets walk pace rather than forcing jog to walk.

Custom standing column has L1/L2, six directions each. L1 clips retime30->21FPS
(exact70%). L2 retimes30->26FPS (86.67%, nearest integer FPS to85%). Level3 selects
untouched native walking. Graph selector encoding3/2/1 corresponds to walking
levels1/2/3; non-erect stance masks to native1. Existing crouch and all other graph
nodes/mappings are preserved, and all native clips retain original data. The
script always applies selected walking graph level when mod enabled; no toggle
is needed. F7 vanilla comparison still selects native clips. Walking portions
of start/braking transitions inherit chosen pace; jog/sprint remain original.

Tests: translated actual controller at30/60/144FPS, both callback orders, verifies
all level changes and limits, default/reset after slow and fast crouch, independent
crouch scrolling, standing Shift/jog/menu input exclusion, separate float bindings
and vanilla bypass. Full inherited standing/crouch/strafe regression harness passes.
Schema counts/sorted columns/mapping scope, all selectors, baseline node/method
preservation, FPS-only mutation and approved ZIP integrity checked. PBO/ZIP checks
pass. Native DayZ compile/playback/root motion and Windows preparer remain local
test requirements; this is a separate test, not a newly approved stable baseline.

Artifact: `artifacts/MovementLab_Standing_Walk_Three_Levels_v1.zip`.
SHA256: `ee657ba430f8d98212aec3f38ef014b6e7e1c02dea06a65b87594c2caff5b8f3`.

## Standing walk three levels v2: ~85/100/120 test

User requested level1/default85%, level2 100%, level3 120%. Separate source/package
created from standing walk three-level v1; no earlier files or approved v4 changed.
Standing L1 retimes original30FPS clips to26FPS (86.67%, closest integer to85%).
L2 custom resources now retime to36FPS (120%). Selector inputs changed to1=custom
L2 (120%),2=native (100%),3=custom L1 (~85%). Saved walking level1/2/3 retains
reversed encoding3/2/1. Non-erect masking and vanilla bypass now select2 (native),
so crouch remains native on the shared Walk source nodes. Default walking saved
level1 and reset on crouch exit retained. Crouch wheel, gait mode rules, jogging,
sprint, braking, acceleration, direction fix and strafe logic unchanged.

Actual translated controller regression and walk-wheel defaults/clamps/reset/input
isolation tests pass30/60/144FPS with both callback orders. Table/mapping scopes,
six graph selectors, native source preservation and FPS-only byte changes verified;
36/30=1.2 and26/30 approximates0.85. PBO/header/source/footer and ZIP checks pass.
Windows preparation and native animation/root-motion travel speed, including any
native speed cap at120%, remain user-side test requirements.

Artifact: `artifacts/MovementLab_Standing_Walk_Three_Levels_v2.zip`.
SHA256: `291f352a19bbbceda4cd397dc23bb224a73502ddf28e5d6ebd80bf474652bb9a`.

## User v2 logs and standing branch experiment v3

Uploaded script_2026-10-11_19-55-58.log and DayZDiag_x64_2026-10-11_19-55-56.RPT
show v2's correct launcher/mod paths, generated clip/workspace PBOs added, script
module loaded and graph load Success. Script logs contain repeated Walk Wheel
Level1/2/3 changes and Ctrl Base gait1/2. Earlier inference that missing on-screen
messages meant the standing wheel handler did not run was incorrect. Inputs
and saved walking level updates worked. RPT contains no standing custom column,
source-ID or selector error. Mod-relative skeleton XML probes fail before native
load as in earlier tests; they do not establish the walking failure. Standing
variable binding was not logged in v2, so these logs do not prove its success or
which FPS resource actually played. Actual unchanged speed is the user's report.
Uploaded personal-path logs remain attachments, not committed.

V3 is an experiment, not a confirmed cause/fix. Returns native Walk source nodes
to their original form; ErcMoveLowG now selects native original group or custom
L1/L2 groups over a fully cloned ErcMoveLowInjG dependency branch. Correct quoted
string tokenization includes empty and multiline strings:59 dependency nodes
cloned. Two-component Locomotion.slot IDs change to custom standing column;
explicit Locomotion.Cro.MoveLookHead and injured column stay original. Custom
column copies the full native58-slot schema; all39 Erc mappings copied for each
of2groups,78 rows. Only six Walk direction rows use26/36FPS variants; all other
idle/look/jog/sprint/etc mappings are identical native rows. Whole branch group
selection parallels the working crouch approach instead of per-leaf wrappers.
Walking UI messages removed; first graph binding and changed selection logged.
Clip preparer prints generated FPS per standing variant. Collect-Logs tools added.

Tests validate every original graph node unchanged except ErcMoveLowG, all59 clone
references and custom slots resolve, full schema counts/order/scoped mapping,
non-walk custom rows identical native Erc rows, controller default/reset/clamps,
separate crouch wheel and all inherited movement regressions. Translated controller
passes30/60/144FPS both callback orders. Native compile/playback/velocity and
Windows preparer unexecuted here; package header/source/footer and ZIP verified.
All earlier packages and approved Six Levels v4 remain unchanged.

Artifact: `artifacts/MovementLab_Standing_Walk_Three_Levels_v3.zip`.
SHA256: `5708c33fef03dd6c62968b6a199a266a5cd2805d7fa4fab7c16e2a0a32bac394`.

## Standing jogging two-level wheel v1

User requested jogging level1 100%, level2 130%. Separate source/artifact built
from walking v3, whose native speed effect remained unconfirmed. Six RunB/BL/BR/F/
FL/FR healthy standing resources get39FPS variants from original30FPS, retaining
all bytes except FPS. Jog selection defaults1 and clamps1..2 with wheel input
only in eligible standing jog mode without held Shift. Ctrl, crouch and walking
retain prior mode/input logic. Jog selection persists across mode and stance
changes; no additional screen message or F8 comparison added.

Full upright cloned branch now uses five custom groups: L1,L1J2,L2,L2J2,NJ2,
combined with original native Erc group. Saved walking encoding3/2/1 plus3 when
jogging130 selected resolves graph inputs6/5/4. Each J2 group copies matching
walk profile and original native Erc non-jog rows, retargeting only six Run slots
to39FPS variants. 195 custom mappings (39x5) in original58-slot schema. Native
full sprint resources are unchanged; jogging parts of acceleration/braking/sprint
blends inherit chosen jogging pace. Existing gait and timer logic preserved.
Jog wheel processing runs before walking graph update for immediate selection.

Validation: actual translated controller baseline plus jogging defaults/clamps,
walk/jog/crouch wheel isolation, Shift/menu/prone/vanilla exclusions, persistence,
all six combinations,30/60/144FPS both callback orders passed. Schema/order and
mapping scopes, all combined groups' non-jog row equality, native graph node
preservation and39/30=1.3 FPS-only mutation checked. PBO/ZIP verification passed.
Windows preparer, native compilation, phase continuity and actual physical travel
speed remain local test requirements. Original approved v4 and prior packages
remain unchanged.

Artifact: `artifacts/MovementLab_Standing_Jog_Two_Levels_v1.zip`.
SHA256: `817d231f3aa0d214ac9a9a72c5b80dd696abdfb2672a47d2c0a0947a792212cd`.

## Linked standing wheel boundaries v1

User requested walking level4 at121% to toggle jogging; jogging level1 at99% to
return to highest actual walking level120%, with native jogging100 atlevel2.
Existing130% jogging retained aslevel3 (user said add levels, not remove130).
Separate source/package from Jogging Two Levels v1. Actual animation/profile/
preparer/mission bytes unchanged;121/99 are transient mode triggers.

Single standing wheel reader replaces separate walk/jog readers. It increments
walking1..4 or jogging1..3 based on the mode at the start of processing. Walking4
normalizes to savedwalking3, savedjogging2, walkMode=false. Jogging1 normalizes to
savedjogging2, savedwalking3, walkMode=true. Normalization called every eligible
standing frame (including without scroll), so trigger levels never persist.
No second wheel reader runs in the destination mode. Native mode transition
WantedGait/command startup and mission braking paths handle1->2 and2->1; timer
constants unchanged. Savedjog default2 selects original100%;130% graph selection
now requires savedjog3. Walking selection, crouch defaults/reset and Ctrl/Shift
rules unchanged. Existing input eligibility/menu/prone/crouch/Shift exclusions
preserved; boundary rules active during standing walk/jog including at rest.

Validation: actual translated controller passed30/60/144FPS both callback orders,
full ascending/descending sequence, limits, native/jog130 preservation,100 rapid
boundary alternations with no double-notch destination processing, parked boundary
normalization without new input, idle switches, stable post-switch state, retained
timed deceleration, crouch wheel/reset and Shift/menu/vanilla exclusions. Existing
standing/crouch/strafe regressions and combined-profile schema tests pass. Animation,
preparer and mission byte preservation checked. PBO/source/footer/ZIP verified.
Native DayZ compilation, animation continuity and velocity still require local
confirmation. No new screen messages; diagnostics recorded in logs only.

Artifact: `artifacts/MovementLab_Standing_Scroll_Mode_Links_v1.zip`.
SHA256: `8d3dd6fbc554c51828db3f92112aea2569253dd2ba0ec0f4f25d2b445013cb77`.

## Top jogging110/130 F8 comparison v1

Separate version from linked wheel v1. F8 OFF default uses33FPS jogging (110%).
F8 ON uses previous39FPS (130%). Native jogging level2 stays100%, boundaries
walking121->nativejog and jog99->walking120 unchanged. Three new custom groups
combine each existing walking pace with jogging110; all non-Run rows copied
unchanged from respective130 groups. Eight custom groups/312 rows, graph inputs
7/8/9 for110 versus4/5/6 for130. Float maximum expanded9. F8 toggles static
comparison flag in offline mission, logged only. Existing saved jogging top
level3 now selects110 unless flagON. No additional movement gait/time changes.

Actual translated controller tests pass30/60/144FPS both callback orders for all
walking-profile comparisons, native jogging independence, inherited mode boundary/
rapid-scroll/crouch/standing regressions. Schema and non-jog mapping preservation,
33/30=1.1 FPS-only mutation, PBO and ZIP verified. Native compilation/Windows
preparation/physical speed and animation continuity pending local confirmation.
Mid-step clip switch may reset phase once. Earlier packages and approved v4
preserved.

Artifact: artifacts/MovementLab_Jog_110_130_F8_Test_v1.zip.
SHA256:29cd7cb7087094f2d421b7b737678c6ccaf2b9743c48bc5ce1ebe49da17f3237.

## Jog80/native100 to scroll-selected sprint v1

Separate test from linked wheel v1; previous F8 comparison preserved unchanged.
User replaces jogging levels with80/100/101 boundary and sprint99/100. Jogging80
is a real24FPS pace, replacing the prior99->walking boundary; walking121 still
enters nativejog100. Jog101 normalizes savedjog2 and enables scroll sprint with
savedsprint2. Sprint99 normalizes sprint2 and disables scroll sprint, selecting
nativejog2. No retimed101/99 clips needed; existing native sprint clips retained.
Single standing wheel reader prevents double-processing destination mode. Scroll
sprint requests gait3 without Shift; selected mode persists when movement keys
are released. Ctrl or crouch clears scroll sprint. Shift native sprint retained.
Standing actual jog resources change39FPS/J2 variants to24FPS/J80; native jogging
unchanged. Custom group layout reused, now selects80 when savedjog1.

Mission turbo classification includes player scroll sprint status, preserving
achieved-sprint exposure and release-to-stop envelope when no Shift is held.
Existing mode acceleration, timed brake formulas, directions, crouch defaults
and walking resets retained. Tests with actual translated controller/mission pass
30/60/144FPS both callback orders: jog80/native100 limits, native sprint without
Shift, capped sprint wheel, returntojog100,100 reversal cycles, achieved sprint
exposure/full-stop, parked sprint mode, crouch ownership and Ctrl clearing.
Inherited regressions, mapping/schema/FPS-only24/30=.8 and package checks pass.
A post-harness assertion first referred to an overwritten Python loop variable;
corrected to reread the actual mission file, rerun passed. Native compiler,
Windows preparer, animation playback/physical velocity remain local requirements.

Artifact: artifacts/MovementLab_Scroll_Jog_Sprint_v1.zip.
SHA256:12073dc4c1c8beccaa29c30f56ad4ac0737c826105d468a5fab39f5c9790773e.

## Jog/sprint v2 corrected default crossings

Walking fourth121% trigger selects jog80 level2. Jogging:1 transient79% -> walking
defaultlevel1~85%;2 real80% default;3 native100%;4 transient101% -> native sprint.
Sprint99 downward trigger returns native jog100 atlevel3. Custom80 profiles now
select when joglevel2. Walking121 normalizes savedwalk3/savedjog2, jogging79
normalizes savedwalk1/savedjog2. Single-notch processing retained. Existing
scroll-sprint brake exposure, native Shift, Ctrl and crouch ownership retained;
no new animation/FPS changes. Actual translated controller tests pass30/60/144FPS
both callback orders, ascending/descending crossings,100 walk/jog reversal cycles,
idle crosses, sprint exposure/full stop and crouch clearing; inherited regressions/
schema pass. Native compilation/playback/velocity pending local test.
Earlier packages and approved Six Levels v4 remain preserved.

Artifact: artifacts/MovementLab_Scroll_Jog_Sprint_v2.zip.
SHA256:3aead464c12aad6e5b3df29c980a5795ff822a4bd3b307cd4fcc18eb9309d87e.

## Seven crouch levels v1

Separate test from current jog/sprint v2. Added slow-crouch level6 target95% using
29FPS (96.67% nominal pace); nativefast endpoint renumbered7. Default3 remains60.
Crouch wheel clamp/max7, Shift graph selection7, savednative7 gait3, sprint-entry7,
existing messages updated /7. New L6 group duplicates28 L5 native/custom mappings,
six walk paths point to L6 retimed29FPS variants. Other rows unchanged. CroMoveLowG
levels6/7 share new CroWheel95G, selecting L6 over existing cloned crouch branch,
avoiding branch switch at native transition. Native sprint/run rows preserved.
Standing scroll/walk/jog/sprint rules unchanged.

Tests: actual translated controller seven-tier clamps/defaults/Shift/sprint-entry/
release/ownership and all inherited standing/strafe/jog-sprint regressions pass
30/60/144FPS both callback orders. Table count/sorted group IDs/mapping scopes,
L6 row equality apart from walk path, graph endpoint selectors and script native7
requests validated. PBO and ZIP checks pass. Native DayZ compiler, Windows clip
preparation, animation pace and physical speed pending local confirmation.
95% nominal rounds to96.67%; native fast level7 is a separate gait, not100% slow
walking pace. Original approved v4 and all earlier packages preserved.

Artifact: artifacts/MovementLab_Crouch_Seven_Levels_v1.zip.
SHA256:694050d1d43d3100370e05760cd67340bb391e5bf4caba37fe64633024e7c53d.

## Six-level restore, fast crouch90% v1

User reverted the seven-tier slow95 experiment and requested fast crouch velocity
10% below native. Separate test starts from jog/sprint v2 six-tier crouch baseline,
level6 nativefast request. Three custom L5 SprintF/FL/FR mappings now use separate
p_cro_runF/FL/FR variants at27FPS instead original30. Native rows/resources remain
unchanged, as do World controller, mission, root/template/locomotion graph bytes.
Level6/heldShift/full-sprint entry retains gait3, custom clip playback/root-motion
targets90% fast-crouch velocity and animation cadence together. Level1..5 and60%
entry default preserved. This90% refers to nativefast, not native slow-crouch.
Seven-level experiment preserved separately.

Translated standing/crouch/strafe/jog-sprint regressions pass30/60/144FPS both
callback orders. Schema/mapping scope and original native row preservation checked,
only three custom fast slots differ;27/30=.9 FPS-only byte mutation verified.
PBO/ZIP checks pass. Native compilation/actual velocity/playback and Windows
preparation require local confirmation. All earlier packages remain preserved.

Artifact: artifacts/MovementLab_Crouch_Fast90_v1.zip.
SHA256:2ba814042d70b91a3d895ca65772c3d0b788e78f4c98c54d57221078ede9ae4b.

## Sprint120 v1 from explicitly requested corrected scroll v2

Separate source from MovementLabScroll_JogSprint_v2, excluding later crouch tests.
Sprint clamp expands1..3; entering from jog101 still selectsnativelevel2. Up selects
level3 120%, down first selectsnativelevel2 then99 trigger returnsnativejog100level3.
Three sprint variants F/FL/FR retime original30FPS to36FPS; native originals kept.
Three full upright custom groups combine each walking profile with120 sprint;
all non-Sprint rows retain respective base profiles. Custom standing groups8/
rows312 and graph inputs7/8/9. Root float max9. 120% profile selected only while
scroll-sprint mode and sprintlevel3. NativeShift/manualmode and crouch handling
retained. Mission bytes, timer formulas and original six-level crouch preserved.

Actual translated controller and mission tests pass30/60/144FPS both callback
orders, nativeentry/highestlimit/downwardsequence,all3 walking profile selections,
100 repeated sprint crossings, exposure/stop handling and inherited regressions.
Mapping preservation/36FPS mutation/schema/PBO/ZIP checked. Native compiler,
Windows preparer, animation continuity and physical120% velocity remain local
test requirements. Approved v4 and earlier packages preserved.

Artifact: artifacts/MovementLab_Sprint120_Test_v1.zip.
SHA256:af465ae04d9e0cc55efdad60cdc04692734b0236c45142d7b9c29152764c8c11.

## Sprint travel120 physical diagnostic

User reported earlier sprint120 clip test very slow, then requested actual faster
travel. Exact earlier failure not established; no new native logs provided.
New separate test starts from corrected scroll v2, preserves all animation/
preparer/mission bytes, adds sprintlevel3 and physical callback intervention.
Official Human SDK documents OnPhysMove(dt,transform[4]) before final transform/
alignment, plus CollisionMoveTest(dir,offset,scale,ignore,out hit...) collision
fraction. Native override gait3 is an animation/gait state, not m/s and cannot
establish120% physical speed. New callback calculates horizontal delta between
current GetPosition and proposed transform translation, tests120% proposal with
CollisionMoveTest, applies max(1,1.2*fraction) to x/z preserving height and validated
native base movement. Only eligible grounded unattached local fully achieved
standing scroll-sprintlevel3, directional input, no braking and sane timestep.
No SetPosition teleport or physics velocity override. Native replay/network
semantics are not validated; experiment is offline only.

Added logs record proposed base/adjusted m/s and independently sample actual
GetPosition x/z travel over0.5s intervals for native sprintlevel2 versuslevel3.
Proposal logs are not proof of final speed; actual speed logs/native test needed.
Native animation stays100% to isolate travel, so foot sliding may occur. Correction
against cached heading/native movement may still reject transform adjustment;
documented callback availability does not prove practical result.

Actual callback translated to C++ against mock checks120% arithmetic at30/60/144FPS,
height preservation, obstacle fraction/no extra travel, eligibility/falling/parent/
gait/brake/level gates. Existing actual controller regression harness passes after
excluding separate physics/measurement callbacks from controller-only SDK. Ground
measurement callback not native-tested. Animation/preparer/mission byte preservation
and PBO/ZIP verified. Native Windows compile/playback/final displacement unexecuted.
Earlier tests and approved v4 preserved.

Artifact: artifacts/MovementLab_Sprint_Travel120_Test_v1.zip.
SHA256:69a88634540842e5d8849e19dadd3cd329e62de57b07da3e74f5be951785c8e6.

## Sprint travel90/110 v1

User requested level2 sprint10% slower and finallevel110%. Separate source from
travel120 experiment. Grounded eligible achieved scroll-sprintlevel2 now scales
native horizontal proposed displacement0.90. Level3 uses1.10, collision fraction
can block added travel while preserving native validated step. Heights unchanged.
Braking retains native envelopes as previous diagnostic. Scroll99->nativejog100,
walking/jogging/crouch rules unchanged. Native sprint clips deliberately retained,
foot pace mismatch possible. Actual ground speed measurement callbacks retained.

Actual callback arithmetic tests pass30/60/144FPS: native8m/s proposals become7.2
atlevel2 and8.8 atlevel3, height unchanged, collision restriction, falling/parent/
gait/brake/mode/level guards. Inherited actual translated controller regressions,
native animation/preparer/mission byte preservation and PBO/ZIP checks pass.
Native DayZ compile/OnPhysMove alignment outcome/actual final speed and animation
remain user-side requirements. Earlier packages and approved v4 preserved.

Artifact: artifacts/MovementLab_Sprint_Travel90_110_Test_v1.zip.
SHA256:5ec4510327fb2124e420829c0281c4bd82e04a08a3a235ee53ffda43b297ce9d.

## Default reset: corrected scroll test v2 (2026-10-12)

User selected corrected scroll test v2 as default for all future work.
Start from ctrl-mode-test/MovementLabScroll_JogSprint_v2; preserve its source/ZIP
unchanged and package new tests separately. Later crouch/sprint experiments are
outside this baseline. Previously approved v4 and all histories stay preserved.

Artifact: artifacts/MovementLab_Scroll_Jog_Sprint_v2.zip.
Pinned commit:6c4d275.
SHA256:3aead464c12aad6e5b3df29c980a5795ff822a4bd3b307cd4fcc18eb9309d87e.

## Corrected scroll v2: directional crouch transition investigation (2026-10-12)

User observes87->nativefast smooth, nativefast->87 looks like walking loop restarts.
Readonly checks confirm levels5 and6 both select CroWheel5G/custom L5 subtree;
there is no top-level source-column/group change at this exact endpoint. L5WalkF
is p_cro_walkF variant26FPS; L5SprintF/FL/FR use original p_cro_runF/FL/FR. Script
moving slow crouch requests normalizedgait1, fast crouch gait3; these are native
gait values, not physical percentages. CroRunSprintBlendMLWheel is AnimNodeBlend
with clamp((MovementSpeed-2)*(1-Injured),0,1). Healthy blend fast weights0 at<=2,
.25 at2.25,.5 at2.5,.75 at2.75,1 at3. Transition therefore depends on achieved
MovementSpeed trajectory through2..3, not selected wheel percent.

WalkFSrcMLWheel SourceSync uses Walk sync line; SprintFAnimMLWheel SourceSync
uses RunSprint. Supplied player_synctable.asy has separate normalized marker maps:
Walk RDown.25/LUp.31/LDown.85/RUp.90; RunSprint LUp.15/RDown.40/RUp.60/LDown.90.
Both use named foot events but different phase definitions. No explicit
cross-group current-foot-phase transfer appears in this blend's serialized
parameters; native SourceSync cross-group behavior remains undocumented here.
WalkBlendSTMMLWheel manages forward/back branch states and directional
transitions, not a dedicated fast-to-slow crouch exit state.

Mission exits standing brake handling when crouched, cancels brake and delegates
to UpdateCrouchRules. Thus standing mode slowdowns/timer envelopes do not manage
this nativefast->slow crouch handoff. RunSprint native filter modifier remains
heavy4 when standing mission brakeinactive; native directional timing asymmetry
not established. Direct requested3->1 could cross blend range rapidly. Both a
rapid blend-weight fall and loss/mismatch of walking foot phase are candidates.
Cannot claim frame0 restart from source alone: need native phase/achieved-speed
telemetry or slowed video. Exact smooth ascent vs rough descent cause unconfirmed.

Checked actual supplied crouchWalkF ANM event block: first RFootDown/LFootUp/
LFootDown/RFootUp store frame indices8/11/26/31 before marker strings. FPS-only
retiming does not itself introduce fixed original-seconds event timestamps; no
evidence for a timestamp-corruption cause in this inspected format.

Baseline source/package unchanged; SHA256 remains
3aead464c12aad6e5b3df29c980a5795ff822a4bd3b307cd4fcc18eb9309d87e.
Desired behavior: forward-progressing foot cycle with reverse blend weights and
deceleration, not reversed clip playback. Useful next native diagnostic would
compare achievedgait3..2 descent duration vs ascent and check active foot phase/
walk-source activation at the handoff before editing a separate test.

## Crouch descent v1 timing experiment

User authorized a separate test after the graph investigation. Source based on
corrected scroll v2, unchanged default baseline. Controller targets only fast
(savedlevel6 or heldShift) ->savedlevel5 ~87 while moving, with actual achieved
gait>2.05. Request starts from achieved gait clamped2.05..3, smoothstep fades to2
over.28s, then linear2->1 over.10s. Graph blend weight thus has an explicit
descending target trajectory rather than direct request1. No hold/freeze/clip
rewind. Downward controller advanced only from CommandHandler after wheel input,
while mission rule callbacks read the same request without incrementing time.
Fast return, no input, lower wheel tier, invalid eligibility or stance exit cancel.
Original fast request3/ascent behavior retained. All graph/preparer/mission bytes
unchanged; no claimed phase-preserving native source synchronization fix.

Actual translated controller tests pass30/60/144FPS both callback orders: smooth
nonincreasing requests bounded>=1, completed duration, repeated mission reads do
not change timer, Shift reverse/new descent, lower-tier cancellation, input stop,
stance exit and full inherited standing/crouch/strafe/jog-sprint regressions.
An inherited immediate saved87 Shift-release expectation updated for deliberate
new descent behavior. Package PBO/ZIP and byte-preservation checks passed.
Native compiler, achieved native gait trajectory, actual foot-phase/visual
continuity require local test. Corrected v2 default/source/artifact unchanged.

Artifact: artifacts/MovementLab_Crouch_Descent_Test_v1.zip.
SHA256:f02fd604a6f7df70ddc303af39a91588fd32ccff777618ec43f567385524c166.

## Uploaded transition video and direct pose-weight experiment v2

User rejected descentv1 and provided4.14s854x48030FPS recording. Contact-sheet and
full30FPS2.2–3.0s frames inspected: right forearm drops and upper-body pose changes
rapidly around2.4–2.5s. Feet are not fully visible; cannot establish loop frame0
reset from this recording. Upward transition spans pose changes more gradually.
Generated whole clip reverse (124frames4.133s, no audio) and side-by-side reversed
upward source0.2–1.4s vs actual downward2.2–3.4s, both half-speed. Cropped comparison
800x480,71frames2.367s. First preview inspected and both videos fully decode.
Reversed clip is user-requested visual reference, not desired backward foot motion.

New pose-exit v2 built separately from corrected scroll v2, excludes rejected
gait-descent controller. On fast->saved87 edge (achievedgait>2.05), new controller
captures native healthy fast weight clamp(gait-2,0,1), smoothstep fades it to0 over
.55s. Two independent root floats indicate active override and fast-pose weight.
Only CroRunSprintBlendMLWheel expression changes: inactive retains original
native factor; active uses explicit decaying weight times(1-Injured). Native
velocity requests1/3 untouched, source clips continue forward. No frame freeze,
clip rewind or synchronization-table rewrite. Same eligibility/stop/stance/
lower-tier/Shift reversal cancellation. Controller timer only advances once per
command callback. This tests body-pose continuity; exact walking foot phase
transfer is still unproven, not solved merely by numeric blend weights.

Actual translated controller/independent variable bindings tests pass30/60/144FPS
both callback orders: fast->87 startsweight1 while requestgait remains1, monotonic
decay/complete, mission reads don't advance timer, Shift reverse, lower tier/input
stop cancellation and inherited standing/crouch/strafe/jog-sprint regressions.
Schema/mappings, preparer/mission/template/instance byte preservation checked;
PBO/ZIP verified. Native graph expression/compiler/playback/phase need local test.
Corrected scroll v2 remains default and untouched.

Artifact: artifacts/MovementLab_Crouch_PoseExit_Test_v2.zip.
SHA256:e1a6e4999c45abb0553f2e1dc187e9de091bdb49939effd49eecdc3614e024e3.

## Confirmed default: crouch pose-exit v2 (2026-10-12)

User confirmed the direct pose blend works, then explicitly selected the package
from044fd7b as default and authorized extending smoothing across movement speed,
stance and direction transitions. Future work starts from
ctrl-mode-test/MovementLabCrouch_PoseExit_v2; preserve its source/artifact unchanged.
New broad smoothing tests remain separate until user confirms them.
Default ZIP SHA256:e1a6e4999c45abb0553f2e1dc187e9de091bdb49939effd49eecdc3614e024e3.

## Broad locomotion pose smoothing v1

User authorized applying the confirmed direct-pose approach to movement speed/
stance changes and keeping PoseExit v2 as default. Default preserved and marked
before new work. Separate source derives from confirmed PoseExit v2. Graph:
21 original nodes modified,22 new wrapper/matrix/side nodes,99 manifest entries
covering node rewrites and transition-duration edits. Adds8 independently bound
floats: active, walk/jog pose, jog/sprint pose, walking profile, jog rate profile,
crouch profile, lateral side weight and lateral active weight.

WalkRunSprintBlendT native and standing clone plus raised WalkRunBlendT now wrap
their unchanged original T nodes and a direct variable-driven walk/run pose blend.
Standing RunSprintBlendF native/clone combine original native factor when inactive
with filtered fast-pose factor when active. Variables follow achieved native gait,
bounded0..1 with.16s feedback span. Separate two-axis walking-profile/jog-rate
matrix avoids scalar profile changes crossing unrelated speed rows. Walking level
floats1..3 and jog80/native100 mixture use.20s feedback; target values unchanged.
Slow crouch profile floats1..5 smoothly blend existing branches. Confirmed .55s
fast-exit pose controller extends to any lower selected crouch tier; while active
holds highest slow profile5, then blends toward selected lower tier.

Five forward cyclic nodes (native walk/run, cloned walk/run and crouch clone)
wrap original direction cycles and a direct left/right pose blend. Lateral side
weight follows current movement angle, active within65..115deg side range and
fades with.16s span. Blends left/right source poses without intermediate forward
source, retaining original native directional branches for other angles. Native
forward/back state machine crossfade durations extended to at least.42s. Existing
transition conditions/normalized-foot-time gates/phase offsets untouched. Erect/
crouch moving posture crossfades .50s, native stance-change edges at least.38s,
start/stop/sliding-pose handoffs in StanceMaster at least.40s. Original stance clips/
tags retained, including stand/crouch/prone route via StanceChangeSTM.
Unrelated actions/combat/vehicle/gestures are outside this locomotion experiment.

Source adds pose-variable helper only, original input/wanted gait/start/brake/
crouch/strafe rules and mission byte-preserved; broadens confirmed exit target
condition <=5 and adds helper to command orchestration. Root/template/instance
clip mappings and FPS preparer unchanged. No freezes/rewinds or velocity API
intervention. Actual root-motion trajectory may nevertheless change from graph
pose weights; mocks do not prove physical speeds retained. Native F7 graph fallback
wrappers retain original speed nodes, but native graph transition duration edits
remain active; exact comparison requires loading preserved default.

Validation: actual translated controller and independent animation bindings pass
30/60/144FPS both callback orders, full inherited input/standing/crouch/strafe/
scroll-boundary regressions, known fast->87, fast exit to other tiers, monotonic
wheel-profile changes, bounded pose weights and lateral reversal/eligibility cases.
Method comparison verifies every default movement helper unchanged except command
orchestration and intended exit broadening. State machine conditions, clips/tags
and phase offset tokens identical apart from blend-duration values. Original
speedT nodes retained exactly under aliases. Graph schema/count/mapping/binding
and preserved default checksum validated. An inherited test expected cancelling
exit atlevel4; updated for intentional broader exit. A new scenario initially set
fast level before crouch entry default reset; corrected setup enters crouch first.
Reruns pass. PBO/ZIP checks pass. Native DayZ compiler/graph animation/foot phase/
root motion remain user-side tests; broad test is not newly approved default.

Artifact: artifacts/MovementLab_All_Pose_Smoothing_Test_v1.zip.
SHA256:4e5ba33842d8b9a3d033a2b54eb5b05cbe56d77babe97da17004a41648ed071c.
Default artifact remains e1a6e4999c45abb0553f2e1dc187e9de091bdb49939effd49eecdc3614e024e3.

## Confirmed broad smoothing and immediate scroll target v2

User confirmed broad locomotion smoothing v1 works perfectly. Default remains
explicitly preserved PoseExitv2. User now requests immediate target selection
from rapid wheel bursts across walk/jog/sprint and crouch tiers, with animations
continuing toward selected target after scrolling stops. Existing code reads
LocalPress boolean, which cannot convey several notches in one update; native
raw wheel behavior not captured yet, so input collapse diagnosis is provisional.

Separate source from confirmed AllPoseSmoothingv1. Adds documented native
GetMouseState(MouseState.WHEEL) polling once per GetGame.GetTime sample. Signed
counts accepted; magnitude>=120 interpreted as120-unit deltas, anomalous counts
bounded16. Action LocalPress fallback used only if raw0, avoids double-counting.
Accumulated pending count bounded32, cleared across physical stance change/
menu/pause/unfocused game. Input.HasGameFocus checked per official SDK. Native
wheel sign/units and timing require real hardware validation; diagnostics log
raw count/normalized steps.

Standing consumes full count by stepping selected-mode fields and normalizing
existing mode boundary after each notch, without consulting achieved speed or
waiting for pose completion. Preserves asymmetric corrected v2 jog80->walk85 rule,
rather than replacing it with a linear down-to-walk120 ladder. Crouch applies
whole count and clamps1..6 after original entry reset. No further scroll required
once target selected. Existing acceleration, braking, pose profile timers then
approach retained target. Pending count retained across temporary command
ineligibility, applied when eligible; physicalShift can still override current
gait, while stored target selection changes underneath. No new UI messages.
All graph/clip/preparer/mission and Smoothing-Coverage bytes unchanged.

Tests: actual translated source at30/60/144FPS both callback orders passes5-notch
lowestwalk->maxsprint selection before animation catches up, no-more-input settle,
rapid descent to walk,600-unit burst normalization, endpointclamps, same-frame
dedup, asymmetric jog return, crouch endpoint bursts/settling, temporary command
queue, menu and game-focus drops. Inherited full input/brake/crouch/pose/direction
regressions pass. SDK harness extended with actual signatures and raw wheel/time/
focus mock; namespaces converted for C++ only. A single-line guarded log changed
to braces because harness removes logs. Default artifact checksum and confirmed
broad graph/timer methods verified unchanged. PBO/ZIP checks pass. Native compile,
raw-input semantics, target capture and visual continuity pending in-game test.

Artifact: artifacts/MovementLab_Immediate_Scroll_Targets_v2.zip.
SHA256:52eb7aff06bd3de8feb4ff87e0bb7336e35134b90960918769449b3cbec5c3a0.


### Immediate scroll targets v3 — frame capture experiment

User v2 logs (2026-10-12 12:40) contain standing target 5 repeatedly, no proof of an animation-dependent target reset, and raw wheel values only -1/0/1. Raw-zero action fallback also contributes events. Logs cannot establish the number of physical notches lost. Earlier claim that the higher target was not retained was too strong.

V3 calls the existing wheel capture from Mission OnUpdate before super, retaining time-deduplicated simulation fallback and existing pending queue. This tests transient input sampling between character updates; native frame timing and wheel retention are not proven locally. No graphs, pose timing, gait, brake, or crouch rules changed. Local translated tests cover five separate capture calls before one command, persistent target settlement, focus/menu guards, and inherited regressions. Default PoseExit v2 preserved. Collect-Logs produces MovementLab-Wheel-Targets-v3-Logs.zip.


### Immediate scroll targets v4 — active brake destination repair
V3 native logs show many target0/walking selections after a sprint-to-jog target2 brake, with no subsequent target1 brake. Input selection therefore worked in these sequences. Mission did not lower an active brake destination; world pending-decrease held achieved gait after the mission had consumed the wanted transition edge. V4 retargets active moving brakes to lower wanted gait using current brake request and remaining duration (minimum .12s); permits pending walking slowdown after prior brake instead of requiring a fresh edge. Graphs, smoothing timers, frame wheel capture, clip preparation unchanged. Actual-controller regression sprint -> jog -> queued walk fails against v3 and passes v4 at30/60/144FPS both orders. Native visuals/compilation still need user test. Default remains preserved.


### Immediate scroll targets v5 — preserve momentum during retarget
User confirmed v4 selection works but rapid downward retarget compresses sprint-to-walk. V5 replaces remaining-brake duration with established current-gait budget: ordinary jog-to-walk .42s (back .18s), sprint remainder proportional to existing full-stop budget and current request/start. Minimum .12s. Targets still apply immediately; native upward controller and all pose/profile graphs/timers unchanged. Regression asserts a sustained sprint retarget to walk retains >.70s brake budget at30/60/144FPS both orders; original controller and selection tests pass. This verifies request timing, not native physical velocity or visual continuity. Local native test pending; preserved default unchanged.


### Immediate scroll targets v6 — slow-jog/walk endpoint pose test
User reports a subtle bump from lowest jog80 to any walking pace. Cause not proven from video/native graph phase; test applies smoothstep to achieved-gait walk/jog pose target only when walk mode selected with jogLevel2. Endpoints remain0/1, derivative tends to0 at endpoints. Existing low-pass remains; same shared pose variable feeds wrapped walking/jogging graphs. V5 World source byte-identical after removing the four-line addition; mission, all graphs and preparation identical. Full local controller regressions pass, native visual confirmation pending. No claim that phase or root motion is verified by mock tests. V5 and default PoseExitv2 preserved.


### Immediate scroll targets v7 — walking level revision
Walking1 now24FPS/80%, walking2 native100%, walking3 boundary directly to jog80. Removed sustained120 selection; compatibility StandingWalkVariants/L2 is30FPS to ensure no120 fallback. Crouch variants unchanged. Boundary saves walkLevel2 for outgoing pose; downward jog boundary still returns default walk1 now80. Local schema/controller/boundary and pose tests pass30/60/144FPS bothorders. Mission and pose helper unchanged fromv6. Native playback requires local freshly prepared test.


### Immediate scroll targets v8 — single action-event owner
User reports intermittent double steps on v7. Raw wheel state can be observed by frame and simulation callers at different game times and supplemented by action fallback; actual per-notch count not known from prior logs. V8 eliminates both duplication paths: frame Mission reader alone uses Prev/Next LocalPress action events; removes raw polling and CommandHandler capture fallback. Frame-time dedup retained, queue persists. Local regression asserts persistent raw value never changes selection, one action event moves walk80->native100 only, subsequent frames remain there, and multiple explicit action events accumulate across frames before simulation. Momentum/pose/levels preserved. Native rapid event delivery remains unverified and requires user test.


### Immediate scroll targets v9 — walking pose handoff rate test
User confirmed v8 wheel behaviour. Uploaded1.033s/30FPS rear-view clip shows brief torso/arm change around walking handoff; feet cropped, phase reset not established. V9 caps decreasing WalkJogPose at dt/.45 when walking selected, after existing filter, to prevent abrupt native achieved-gait drops from causing a fast outgoing-pose collapse. Animation clips still play normally; graph and speed/brake methods unchanged. Added achieved-gait1/pose1 regression passes30/60/144FPS bothorders; native visual improvement unverified. V8 preserved.


### Camera/loadout v10
User requests fast-crouch viewpoint for slow crouch and military shooting-test inventory. Native third-person crouch camera uses distance1.4, model offset0/.7/.1, local offset0/.3/0 and movement-dependent height SmoothCD((clamp(m_iMovement,1,3)-1)*.5*.4). Camera test adds smoothed difference to fast target .4 for moving crouch; idle remains native, first-person/sights unchanged. Custom FieldBackpack90-slot cargo with Shoulder/Melee attachments; BDU/plate carrier/helmet/gloves/boots/balaclava vanilla gear; M4A1 andSVD backpack attachments, MP5K player shoulder, FNX holster. Each gets full mag+chamber, one spare and cargo ammo fills round robin. Native slots/config availability not verified here; failures print loadout logs. Existing World, graphs/preparer and mission movement/brake methods unchanged. No MMG dependency. Prior v8/v9 preserved.


### Camera/loadout v11 — missing inventory and camera rise repair
V10 erroneously inherited FieldBackpack (display name), not native AliceBag_Green (verified SDK alicebag_colorbase.c); pack creation failure returned before weapons/ammo. V11 config+script inherits AliceBag_Green, equips via attachment, falls back to nativepack and player inventory without earlyexit, weapon attachment failures fallback into player inventory or ground placement via helper. Camera now smooths desired movingheight .4 independently of gait and subtracts native m_fCameraHeight directly: total .7+desired, so fast/slow switches do not lift camera. Idle target0 preserves stationary base view. Existing movement source, graphs and preparer unchanged. Native capacity/attachment acceptance and inventory/compilation still need local validation.


### Armed speeds v12 — instance-aware custom groups
User archive contains130 ASIs,129 player template instances plus1 menu. Eleven direct override providers include rifle/pistol/1h/2h/heavy/bow/restrained/props; weapon descendants inherit these. V12 plan duplicates only original local Locomotion.Cro/Erc rows into corresponding custom namespaces, respecting per-item inheritance rather than hardcoded unarmed source mappings.294 source-specific clip/FPS variants generated locally without modifying originals. Native armed Cro.Walk six directions point to9FPS copies matching level1, eliminating native-speed fallback before custom levels2+. Custom cro14/18/22/26FPS and standingwalk24/jog24 retained; nonwalk/run mappings retain original armed source refs. All129 inheritance checks pass, World/mission unchanged. Raised-aim branches still native; no claim of raised aiming speed support. Original armed clips read from D:\DayZProjects; missing assets fail launcher explicitly. Native preparation/header validity and visual grip require user test. Uploaded original ASIs not committed; only derived mapping plan and paths.


### Armed speeds v13 — ANIMSET5 compatibility
User surrender walkB upload is FORM/ANIMSET5, FPS\0 at20, BEchunk length4 at24, LEuint32 FPS30 at28: same retiming layout as verified ANIMSET6. V12 rejected solely because it required ANIMSET6. V13 armed preparation accepts both verified versions with FORM/FPS chunk-size/FPS range validation, writes onlybytes28..31. Actual uploaded5/6 binaries retiming invariant tests pass;129 inheritance plan checks remain unchanged. Levels/pose/World/mission/camera and mapping plan unchanged. Native full Windows preparation still requires user test.


### Camera toggle v14
V toggles static wider-view flag via guarded/latching mission KeyPress/KeyRelease. Third-person base camera adds smoothed .15m distance/.05m height erect or .30m distance/no extraheight crouch. Current view default, reset on mission init/finish. Crouch correction unchanged and executes after base adjustment. First-person/iron sights separate classes untouched. Native V action bindings unchanged; native collision solver can shorten requested distances. Core movement, graph, armed instance plan and clip preparation byte-identical tov13. SDK keyrelease/camera APIs inspected, PBO/ZIP validated; local Windows/native visuals pending.


### Camera cycle v15 — three perspectives
User confirms native V switches third/first and interferes with v14 two-view flag. SDK DayZPlayerImplement.SetIsInThirdPerson verified; UAPersonView action ForceDisable during offline mission, restored on finish. V key handler now cycles mode0 default3rd,1 wider3rd,2 first; sets wider flag only1 and native perspective mode!=2. Existing key hold latch/menu guard preserved; third-disabled world guard. Initial spawn defaults3rd. Actual helper translated to C++ passed30 cycle presses; native input lifecycle/camera test pending. Existing wider camera geometry/crouch correction, World movement, graphs, armed mappings and prepare unchanged.


### Camera cycle v16 — wider offsets revision
Only wider-view targets changed from erect+.15m/+ .05m height to+.45m/default height and crouch+.30m to+.60m distance. Current/default and first-person cycle retained; existing crouch correction unchanged. Mission/World/graphs/armed plan/preparer byte-identical tov15. Package verified; native camera collision/viewpoint pending local test.


### Aimed speeds v17 — v13 base, no wider camera
User requests aiming movement wheel tiers and no fast aimed crouch. Native graph ErcRas WalkAimBlend/RunAimBlend and rifle *_walk*_ras/*_run*_ras mappings prove distinct raised walk/run pose branches; actual native ADS gait caps/Shift classification still require gameplay confirmation. New template groups ZZMovementLabCrouchAim L1..5 and ZZMovementLabStandingAim5profile combos (same58slots), root+item-specific native CroRas/ErcRas mappings,492 totalvariant plans across16providers. Existing129-instance inherited armed lowergroups preserved. Two raised movement groupselectors wrapped with smoothed profile matrices;16addednodes, every other original node unchanged inclADS/recoil/IK/fire graphlayers. Raised eligibility enabled for wheel/controller/braking, wantedgait capped towalk/jog base (no Shift/sprint), crouchaim clamped1..5 and ignoresShiftfastoverride. Lowered behaviour unchanged in inherited actual-controller regressions. New raised controller tests30/60/144FPS bothorders verifystanding80/native100/jog80/native100 topclamp, Shiftnoaimsprint, aimedcrofivelevels andnativegait1 request. Camera file identical tov13; noVcycle. Native preparation/aimhold/shooting/ADS speed cap test pending.


### Aimed speeds v18 — native crash evidence repairs
Both v17 logs show graph load Error: ErcMoveRasG/CroMoveRasG unresolved. New16 nodes had been appended outside graph/sheet (local regex counted them globally); v18 inserts them before enclosing sheet/root closes. New structural check rejects v17 trailing declarations and proves every v18 node inside sheet/root. Same logs fatal VM NULL DayZPlayerInventory.HandleHandEvent at2698, GetPlugin(PluginInventoryDebug) notregistered. SDK diagnostic branch dereferences that plugin under DIAG_DEVELOPER, but PluginManager registers it through RegisterPluginDebug, skipped when IsDebug false. Offline diagnostic override changes only that registration to release-allowed in DIAG build, delegating all other plugins unchanged. Original exception not swallowed. Core aiming/tiers/controller and native pose mapping plans unchanged. Local raised regressions30/60/144FPS bothorders and scope tests pass; native plugin startup, hand transfers and aim/fire require user reproduction.


### Aimed walking v19 — isolated walking leaves, v13 baseline
User rejected v17/v18 and requests only aimed walking tiers standing65/75/85/native100, crouch30/47/60default/73/87 with correct gun orientation. V19 starts fromv13; does not reuse whole raised-group wrappers. Only six shared synchronized walking source leaves are wrapped; new nine-group/six-slot ZZMovementLabAimWalk scope is local to those leaves, preserving native outer Locomotion.ErcRas/CroRas groups and every upper-body/ADS/IK/recoil graph node exactly. FPS targets20/23/26/30 standing (66.7/76.7/86.7/native100actual),9/14/18/22/26cro. Added120leaf nodes all inside sheet/root. Native Walk synchronization tags and source metadata retained. Runtime plan includes item-specific raised WALK slots only; no copied Aim/AimingDownSight/Idle/Look sources in aim namespace. New independent aim controller keeps gait1 while directional input,0idle; ignoresShiftspeed and Ctrlmode during raised ownership, consumes same wheel queue into4standing/5crotiers, defaultsstandingnative100/cro60onentry. Disables broad smooth controller whileaimed so cached lowered gait poses do not selectRunAimBlend; profile blending .20s within walking clips. Mission cancels prior brake on raising then reapplies aim walking speed to prevent callback-order interference; lowering releases own override and originalcontroller continues. Existing v13 camera/loadout unchanged; targeted diagnostic inventory plugin registration repair from fatal logs retained, noexception suppression. Actual controller tests30/60/144FPS bothorders, tierclamps, Shift, defaultcro60, wheel, idle/lowerownership and inherited lowered movement tests pass. Native upper-body preservation and allscope/mapping checks pass. Native gun orientation/ADS/fire/velocity must be tested.


### Aimed walking v20 — diagnostic after v19 has no effect
User reports native speed standing/crouched. Uploaded v19 logs from two runs show graph load Success and wheel action edges; no native VM exception. v19 emitted no aim-tier/binding/ownership/physical-velocity data, so logs cannot distinguish controller ineligibility, failed bindings or native playback/root-motion ignoring retiming. v20 changes only log reporting: ineligible raised command/stance, eligible tier/profile and native binding IDs, achieved gait and GetVelocity.Length every.5s or targetchange. No on-screen messages; no movement/animation workaround yet. Graphs, armed variant plan, prepare and mission byte-preserved. v19/controller regressions pass including30/60/144FPS callbackorders. Native diagnostic run needed before further functional edits; hypothesis of source synchronization not established.


### Aimed walking v21 — native raised stance indices
Uploaded v20 logs show repeated Ineligible command20/stance3 while standingaim and20/stance4 whilecroaim; isolated eligible stance1 onlyafterlowering. SDK confirms STANCEIDX_RAISEDERECT3 and STANCEIDX_RAISEDCROUCH4. Controller erroneously accepted onlylowered0/1, so didnotconsume aimedtiers orapplyprofile. V21 accepts bothnative raised and existinglowered representations while requiringIsRaised; classifiesstance4ascrouch. Local tests now use actualraised3/4 (earliermock usedlowered0/1 evenwithraisedbooltrue); nativeeffectstillpending. Graphs, clips, plan, prepare andmission identical tov20; loggingretained. Raised4/5 tierbounds andshiftwalkownership regressionstests30/60/144FPS bothorders pass withcorrectnative stanceIDs. No native playback/root-motion claimuntiluser test.


### Separate aiming linked v2
User requests separate branch, removes v21 standing65/75/85 tiers, preserves native slow/fast aimed modes with Ctrl toggle. Clarified90%slower=10%native slow and70%slower=30%native fast. User selected sequence: fastnative100 down->fast30 thennextdown->slownative100. V2 wheel ladder slow10->slownative100->fast30->fastnative100;101/99 are transient mode-edge markers, not held velocities. Ctrl selects opposite mode at itsnative100 tier. Standing fast maps native raised Run branch/gait2, slowmapsraisedWalk/gait1, native upper-body scope unchanged. Only six synchronized Walk andsixRun sourceswrapped withlocal groupselection; noAim/ADS/IK/recoil nodes changed. Walkprofiles S10/S100 + existing5croprofiles, fastprofilesF30/F100. ExactFPS3/30slow and9/30fast implement literal10/30 targets. Croaim tiers/default60 retained; correct raisedstance3/4 gates and diagnostic logging retained. V21 source/artifact unchanged, no camera toggle. Local actual-controller Ctrl latch/clamp/asymmetricmarker/burst/lowerownership/crotests30/60/144FPS bothorders and inheritedlowered checks pass;132extrafoot-sourcenodes allinsidegraph/sheet, nativeclip mappings preserved. Native gait/velocity/ADS/fire check pending; modepercentages relative to eachmode native speed.


### Separate v2 Revision2 — revised slow/fast tiers
User changes fast30 to80, retainsnative100 and adds120; replaces slow10 with30 and adds47/60/73, requesting60default. Clarification explicitly chooses ascending30/47/60/73/100 ordering, so60default nowlevel3 (notoriginallyrequested4). New slowFPS9/14/18/22/30 andfastFPS24/30/36; originalv2 andv21 artifacts/source untouched. Ctrl defaultslowlevel3/fastlevel2; slowupper101 edge afterlevel5 tofast80; fastlower99 edge afterfast80 toslowdefault60, so downward mode boundary returns default instead of uppermostslownative100. Existingcroaim5levels/default60 retained. Twelve foot-source wrappers only,180added nodes, uppernativeAim/ADS/IK/recoil graphnodes unchanged. New actual-controller5/3tier/CTRL/clamp/boundary/raisedstance3/4/cro tests30/60/144FPS bothorders pass, inheritedlowered checks and source/scope mappingchecks pass. Native faster120velocity/fire must be verifiedlocally.


### Separate v2 Revision3 — slowaim trimmed/native comparison
User removes slowaimlevels1/2/3 (30/47/60), leaves73/native100; renumbered1=73default,2=native100. Boundaryabove2 transitionsfast80; fastlower99 returnsdefaultslow73. Standing profiles mapselected1/2 toexistinggraphindices4/5, so lowerstandtiers areunreachable; unusedassetsretained. Fast80/100/120 andcroaimtiers/default60 unchanged. F8 guarded/latching toggles NativeAimComparison bool defaultfalse; onlystandingaim bypassescustomwalking/run source branches viaactive0 andnativeprofiles, samegait1/2/Ctrlmode. Wheelstandingignoredincmp andsavedcustomtiersretained; returningcustomrestoresselection/profile. Crouchaimnotaffectedbytoggle. Logs only, no onscreenmessages. Graphs, mappings/clipplan/preparer unchangedrev2. Actual-controller2slow/3fast/default/persistence/nativebranches/crotests30/60/144FPS bothorders plusloweredregressions passed. Nativecamera/aimvelocity/fire/comparison stillrequireslocaluser test. Previousrev2 andoriginalv2 preserved.


### Separate v2 Revision4 — original native slow source at highest tier
User perceives customhighest100 differently from F8original. V4 keeps custom73defaultlevel1, butlevel2 nowdisablesbothcustomwalking/running source branches exactlyasF8 nativecomparison (standingSlowMode only), selecting originalnativeSyncWalk sources. Samegait1/Ctrl logicandallF8 flags preserved; noFPS/camera/fast/cro edits. Actual-controller assertionlevel2WalkActive0/FastActive0 andallrev3comparison/tier/cro/lowerregressions passed. Graph/mapping/clipplans unchanged. Native parity stillrequireslocaltest; no claim of measuredvelocity equivalencefrommock. Earlierrevisions preserved.


### Separate v2 Revision5 — aim wheel never changes modes
Removed101/99 boundary logic in aimed standingwheel. Slow clamps1..2;fastclamps1..3. Aim defaultSlow, physicalShift heldselectsFast/releaseSlow;CtrlwhileShift forcesSlow andsuppressescurrentShift untilrelease/repress. Wheelremembersmodelevels andnevercrosses. F8nativecomparison andcroaim unchanged; nativetopSlow source preserved. Actual-controllerclamp/spam/Shift/CTRLatheldShift/release/repress/comparison/crochecks30/60/144FPS bothorders passed. Graphs/clipplans untouched. Native validationpending.


### Separate v2 Revision6 — derive aim entry from lowered mode
Standing aim entry fromwalkflagtrue atanywalktier selects slowhighest(original100);fromjogflagfalse atanyjogtier selects fasthighest120. Ctrl toggleseffectiveaimmode andresetsbothselectedtiershighest. Storedbaseaimmode persistswithoutShift: holdingShift.10s onlytemporarily overridesSlowbase toFast; release restoresSlowbase. Fastbase cannotbechangedtoSlowbyShift. Ctrl duringShifttempFast selectsSlow/suppressescurrenthold untilrelease/repress. Wheelclamps currentmode, aimingpose/clipplans/F8/crounchanged. Actual-controller entry/CTRL/Shiftrelease/raised3/4/defaults/cro tests30/60/144FPS bothorders and inheritedchecks passed;nativevalidationpending.


### Separate v2 Revision7 — Shift latches fast aiming
User requestspressShiftfromslowaim tofastwithoutrequiringhold, releasecannotreturnslow;Ctrlonlyslowreturn. V7 detectsShift risingedge; setsbaseFast/highest120. Ctrlprioritytoggleseffectivebase/highest levels; holdingShiftwhileCtrlslow doesnotoverrideuntilfreshrelease/press. WalkingentrySloworiginal100/jogentryFast120 unchanged. Slow73/native100 andfast80/native100/120 wheeltiers, upperpose/F8/crouchpreserved. Actual-controllerpress/release/heldCtrl/freshpress/entrytests30/60/144FPS bothorders passed;nativevalidationpending.


### Separate v2 Revision8 — tier-aware aim entry/default exit
Entry walking1/2 ->slowaim1/2; joggingdisplaylevel1/internal2(80) ->fastaim1; joggingdisplaylevel2/internal3(native100)->fastaim2; scrollsprint orunconsumedphysicalShift->fastaim3. Exitstandingaim maps effectiveSlow/Fast towalking/jogging default80, clears scrollsprint andconsumesanycurrentheldShiftuntilrelease toavoidreturningsprint. New aiming session flags distinguishloweringfrommenu/action interruptions; selectedtiers retainedacrossineligibletemporarycontexts. Wheelup increases/downdecreases (userline3 down-tohigher interpretedtypo). ExistingShiftlatch/Ctrltoggle/fast80/native100/120/slows73/original100/cro/F8/upperposes preserved. Controller testsfiveentrycases/temporarymenu/reentry/defaultreturn/changedmodeexit30/60/144FPS bothorders passed;nativevalidationpending.

### Separate aimed movement v2 Revision9

User reported jog level2 did not feel like native fast aim level2 and lowering fast aim level2 returned to jog level1. Revision8 explicitly reset every aim exit to jog80; Revision9 maps fast aim80 to jog80 and fast aim100/120 to jog100. Slow aim exits still select default walk80. Entry jog100 mapping remains internal jog3 -> fast aim2, now with a log identifying source and selected tier. Fast aim level2 bypasses retimed foot-source groups and uses the original native source branches, like the previously corrected native slow aim level2. The Shift edge latch initializes from actual held input on aim entry. All earlier builds retained.

Actual-controller translated C++ checks passed at30/60/144 FPS in both callback orders, including five entry mappings, native source binding outputs, exit/reentry mappings, menu persistence, and existing movement regressions. Graph/clip mappings unchanged. Windows native compilation, animation and velocity remain user-test dependent.

### Separate aimed movement v2 Revision10 — sprint-entry momentum

Sprint -> standing aim enters exclusive fast aim level4/140% (42FPS native run-foot source variants). A smoothstep profile traverses4 ->3 ->2 in0.5 seconds, retaining native gun aim layers. During this transition wheel events are discarded, Ctrl/Shift mode changes are deferred until completion (new presses required). Normal selectable fast aim remains80/100/120%, clamped1..3. Level4 can only be entered from a new sprint-to-aim session. Lowering gun cancels the timer; crouch entry cancels it and preserves normal crouch aiming levels. Original native fast aim branch is restored after reaching profile2, rather than snapping into it mid-transition. F8 native comparison continues to bypass custom source playback.

Actual-controller checks passed30/60/144 FPS both callback orders:0.5s traversal, monotonic profile, scroll spam discard and maximum selectable3, entry/exit mappings, inherited controller regressions. Structural graph validation confirms12 extra synchronized fast-foot nodes, native aim/ADS/IK/recoil nodes unchanged; F140 mappings use original correct armed run sources at42FPS. PBO/ZIP packaged. Native DayZ compilation, perceived momentum and achieved velocity require local test. Revision9 preserved.

### Revision11 — projectile weapon sprint entry and handoff test

Revision10 native logs show three successful fast aim level4 entries followed by level2; no evidence the selector failed. Native reported gait remains2.8+ at timer completion, despite requested aim gait2. This suggests the half-second retimed run-foot profile decays during the native sprint-to-raise handoff; logs do not prove the visible source contribution or exact cause. New test caches achieved upright lowered sprint for250ms to survive cleared sprint inputs, restricts exclusive140 entry to held IsWeapon items, and allows a bounded250ms handoff before counting the0.5s decay (or starts sooner when achieved gait<=2.1). Total duration may now reach0.75s; scroll remains discarded throughout. Added log for fast profile, remaining timer and native comparison. No claims of native success until tested.

Translated actual-controller checks pass30/60/144FPS both callback orders plus recent sprint with released Shift/cleared scroll sprint, weapon exclusion, held handoff, capped selectable tiers and prior regressions. Graph and plans identical toRevision10. Original native runtime unavailable here. Prior builds preserved.

### Revision12 — longer sprint-entry aim decay

User requested140 ->100 over1.5 seconds. Changed only the aim sprint timer duration and corresponding normalized progress divisor from0.5 to1.5. Existing bounded0.25s handoff and wheel lock retained; maximum total1.75s. Graph/clip plans unchanged. Updated actual-controller duration tests passed30/60/144FPS and both callback orders, including wheel lock, native endpoint and weapon scope. Native visible effect still requires user test. Revision11 preserved.

### Revision13 — sustained full-sprint qualification

User requested140% only after1 continuous second fully sprinting, excluding jogging/acceleration. Added achieved gait>=2.99 duration accumulator while local upright lowered movement is eligible. Requested Shift/scroll sprint alone can no longer trigger140. Anything below threshold, crouch, stop or UI pause resets qualification. A qualified raise retains existing250ms entry grace for native sprint input clearing and consumes qualification once. Existing1.5s decay and maximum250ms handoff unchanged. Native gait is a movement-state proxy rather than direct visual animation frame inspection.

Actual-controller checks passed30/60/144FPS both callback orders; added checks for long accelerating gait2.9, half-second full sprint, interrupted sprint, successful full-second qualification and reset on stop/crouch/menu. Graph and clips unchanged. Native runtime test pending. Revision12 preserved.

### Revision14 — attainable sprint qualification and offline test loadout

User reportedRevision13 never triggers. Strict achieved gait2.99 may not be reached: earlier native logs showed sprint around2.97. Revised condition>=2.9 plus active sprint request and1 continuous second (still resets below threshold/ineligible). This is a test hypothesis, not proven fromRevision13 logs. Added regression sustained2.97 qualifies, early2.8 does not. Decay1.5s retained.

Offline-only StaminaHandler overrides preserve native processing while removing load-based cap and depletion; PlayerBase.IsOverloaded returnsfalse only in enabled offline test. No multiplayer changes. All tactical clothing/vest/holster/pouches black; custom backpack now smaller AssaultBag_Black model with42 cargo slots and two weapon slots. Existing four weapons/loaded and spare magazines retained; spare loose ammo fills smaller pack. Spawn moved fromcoast toNWAF4610/10180 surface height every launch.

Actual controller and inherited graph checks passed30/60/144FPS both callback orders. Translated stamina methods checked600 updates/full cap/no depletion and multiplayer fallbacks. Loadout class references and spawn checked statically. Native compile/spawn and felt momentum remain user-test dependent. Earlier versions preserved.

### Revision15 — sprint-entry diagnostics and paved target range

User reports140 still invisible. Revision14 native logs requested, not received at packaging. No proven root cause; do not claim fixed. Test extends qualified raise grace250ms ->1s while retaining immediate reset on lowered slowdown; logs achieved sprint gait, sustained timer, qualified expiry, profile and decay timer to distinguish eligibility from playback. Duration1.5s unchanged. NWAF spawn moved to intended paved runway4500/10300; exact surface requires native check.

Five unselected PlayerBase targets spawn20m ahead on a line10m spacing. Per-target mission scheduler detects death, waits3000ms, deletes corpse, replaces same class/position, repeats indefinitely and cleans up on mission finish. Native command idle override applied only to flagged live targets, normal death processing preserved. Black/unlimited-stamina loadout retained.

Existing actual-controller regressions pass. Actual target update method translated and tested20 death cycles/five targets, no respawn2999ms, replacement3000ms and corpse cleanup. Native animation speed/compilation/spawn surface/NPC stationary behavior remain unverified. User logs/in-game test required to finish140 diagnosis.
