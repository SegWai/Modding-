#!/usr/bin/env python3
"""Package native-only v17a without changing any stable artifacts."""
import sys
sys.dont_write_bytecode = True
import package_movement_logic_test as packer
packer.SOURCE = packer.ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v17a"
packer.OUTPUT = packer.ROOT / "artifacts/MovementLab_Movement_Logic_Experiment_v17a.zip"
packer.ARCHIVE_ROOT = "MovementLabMovementLogicExperiment_v17a"
packer.VALIDATION_EXTRA = {
    "variant": "v17a native-only moving reversal; no script-command handoff",
    "recovery_seconds": 0.62,
    "incoming_slowdown_seconds": 0.12,
    "minimum_requested_gait": 1.60,
    "release_gap_seconds": 0.10,
    "animation_control": "native engine only; no manually requested brace or graph/physics writes",
    "native_compile_and_playtest": "pending local DayZ test",
    "mocked_checks": "actual controller/integration at 30/60/144 FPS with spam, overlap, gaps and exclusions; v11 ordinary startup/braking equality excluding explicit ownership guard",
}
if __name__ == "__main__":
    packer.main()
