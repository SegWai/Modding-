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
