# v102 confirmed momentum; v103 starting-pose correction

The user confirms the infected-model ragdoll carries running momentum. The uploaded v102 logs independently show running captures near6.45 and5.76m/s and pelvis horizontal travel of approximately1.71 and1.57m within305 and303ms. The one-shot horizontal impulse pipeline is retained.

The remaining observed defects are pose discontinuities: running arms drop immediately, and a dead crawler reappears standing before falling. The current replacement explicitly waits for an upright default skeleton; its native pose is not the infected's last animation frame. Fixing momentum cannot fix that initialization mismatch.

## Implementation

Before super.EEKilled, the tracked infected captures IsCrawling(), its current gait and whether either hand is more than0.12 model units above its pelvis. This uses the inherited skeletal-name lookup which v98 proved readable. Hand height is a heuristic, not a full pose measurement. Source decisions are logged.

During hidden warmup, the replacement uses native HumanCommandMove.ForceStance and input overrides rather than failed generic bone writers. Crawlers request prone and at most native crawling gait1. Upright raised-arm deaths request raised unarmed stance and at most gait2 to avoid the sprint/lowered-arms conflict. Other upright deaths use normal native gait. These requests are limited to the dedicated replacement actor, not the player or other targets.

Activation requires at least100ms and matching observed bone positions. Upright bodies require the existing valid head/pelvis layout; raised-arm bodies additionally require a hand above pelvis+0.12. Crawlers require both head and pelvis to be low (head0.02..0.8, pelvis0.02..0.65); they cannot use the upright condition. If readiness fails by the existing one-second deadline, the normal infected corpse is retained. No standing fallback is spawned for a crawler.

Once ready, input overrides are released, the actor is killed and native ragdoll is enabled using the existing handoff. No script keeps the arms raised after death or continuously drives the ragdoll. The source decisions, seeded hand positions and activation stance/gait are logged for diagnosis. Momentum, one live infected and five-second respawn remain unchanged.

This is approximate native pose seeding. Human raised-unarmed/prone/moving animations are not identical to infected attack/run/crawl poses. Exact skeletal rotations, animation phase and per-limb angular velocity are not cloned. Native death processing might still change the seeded arms before physics; source tests cannot establish continuity and the visible handoff requires the user's run. If a prone/raised pose never becomes ready, retaining the original is preferable to showing a standing ragdoll replacement.

## Verification and test

The actual helper/sample/capture-selection methods pass adapted C++ logic checks including prone initialization, rejection of standing fallback for a crawler, raised-arm readiness, rejection of dropped-arm initialization, existing momentum preservation, warmup/activation failures and cleanup. Native API signatures are checked against the official SDK. These checks do not emulate native stance transitions or compile Enforce. PBO/ZIP packaging verifies source bytes, prefix/offsets/checksum and integrity.

Extract MovementLab_Corpse_Momentum_v103.zip into a fresh folder. Compare an upright running kill with arms up, a stationary kill, and a broken-leg crawling kill. Close DayZ and Collect-Logs.cmd, then send MovementLab-Corpse-v103-Logs.zip and describe any remaining arm snap or upward jump.
