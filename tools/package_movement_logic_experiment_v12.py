#!/usr/bin/env python3
"""Build the isolated v12 experiment; default packager/source stays on v11."""
import sys
sys.dont_write_bytecode = True
import package_movement_logic_test as packer

packer.SOURCE = packer.ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v12"
packer.OUTPUT = packer.ROOT / "artifacts/MovementLab_Movement_Logic_Experiment_v12.zip"
packer.ARCHIVE_ROOT = "MovementLabMovementLogicExperiment_v12"
packer.VALIDATION_EXTRA = {
    "variant": "experimental v12; stable source and download remain v11",
    "braking_v11": "v11 retained as the stable baseline; new experiment uses a shorter/smoother envelope",
    "experiment_v12": {
        "full_sprint_stop_max_requested_seconds": 0.92,
        "previous_v11_max_requested_seconds": 1.15,
        "reversal": "pre-base-command A/D opposite-input detection; old-direction brake, achieved-idle wait, 0.12s dwell, then walking restart",
        "idle_wait_timeout_seconds": 0.60,
        "native_compile_and_playtest": "pending user local test",
        "mocked_control_sequences": "mechanically translated actual World logic passed at 30/60/144 FPS; no native animation validation",
    },
}

if __name__ == "__main__":
    packer.main()
