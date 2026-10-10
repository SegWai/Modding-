#!/usr/bin/env python3
"""Build a separate v11-based native pose/physics experiment."""
import sys
sys.dont_write_bytecode = True
import package_movement_logic_test as packer

packer.SOURCE = packer.ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v13"
packer.OUTPUT = packer.ROOT / "artifacts/MovementLab_Movement_Logic_Experiment_v13.zip"
packer.ARCHIVE_ROOT = "MovementLabMovementLogicExperiment_v13"
packer.VALIDATION_EXTRA = {
    "variant": "v13 native reversal pose experiment, copied from stable v11",
    "experiment_v13": {
        "requested_hold_seconds": 0.32,
        "native_pose_command": "CMD_SlidingPose",
        "animation_gait": 2,
        "horizontal_translation": "zeroed through HumanCommandScript.PrePhys_SetTranslation",
        "pose_retention": "repeated native command requests; engine behavior unverified",
        "toggle": "F8 experiment on/off; F7 retains original heavier/vanilla switch",
        "native_compile_and_playtest": "pending local DayZ test",
        "mocked_command_checks": "Actual translated command passed 30/60/144 FPS duration, pose-variable, X/Z suppression, vertical-preservation, cancellation and invalid-binding tests; native graph not modeled",
        "baseline": "stable v11 source and ZIP unchanged; v12 logic not used",
    },
}

if __name__ == "__main__":
    packer.main()
