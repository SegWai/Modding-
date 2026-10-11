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
