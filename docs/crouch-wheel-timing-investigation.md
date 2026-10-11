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
