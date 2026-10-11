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

No new gameplay package is warranted by the current evidence. Working v1 and
stable standing movement remain unchanged.
