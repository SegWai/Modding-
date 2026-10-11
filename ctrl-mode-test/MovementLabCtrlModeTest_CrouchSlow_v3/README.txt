CROUCH CLIP RETIMING TEST V3

Close DayZ, keep Steam running, extract this entire ZIP to a fresh folder and run Launch-Movement-Test.cmd.

Based on stable v10 Strafe Test v2. Six native crouch walking clips retimed by changing their explicit FPS chunk from 30 to 6. Bone poses, frames, root positions, contact markers and all other bytes remain unchanged. The physical-translation reduction from crouch test v2 is REMOVED so reductions do not stack. Retiming should slow animation and its root motion together, but this must be confirmed in DayZ. Shift fast crouch uses separate run clips.

This asset override applies to all uses of those six slow-crouch clips while the test mod is loaded, including raised crouch if it shares them. F7 only toggles controller logic, not animation assets; compare with stable baseline in a separate launch. Normal standing controller behavior is unchanged.

Checks: exactly six explicit FPS chunks 30->6, one byte per clip changed, all other bytes unchanged, PBO headers/payload/checksum validation, unchanged stable controller regressions. Native asset loading, sync behavior, collision and animation appearance are unverified.
