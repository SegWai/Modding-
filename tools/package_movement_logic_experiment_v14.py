#!/usr/bin/env python3
"""Build a separate v11-based native pose/physics experiment."""
import sys
sys.dont_write_bytecode = True
import package_movement_logic_test as packer

packer.SOURCE = packer.ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v14"
packer.OUTPUT = packer.ROOT / "artifacts/MovementLab_Movement_Logic_Experiment_v14.zip"
packer.ARCHIVE_ROOT = "MovementLabMovementLogicExperiment_v14"
packer.VALIDATION_EXTRA = {
    "variant": "v14 native reversal pose experiment, copied from stable v11",
    "experiment_v14": {
        "requested_recovery_seconds": 0.50,
        "native_pose_command": "CMD_SlidingPose",
        "animation_gait": 2,
        "horizontal_translation": "continuous old/new vector momentum and heavy speed recovery through PrePhys_SetTranslation",
        "pose_progression": "single native brace command, changing directional samples and native outgoing blend; no stationary hold or literal animation clock slowdown",
        "toggle": "F8 experiment on/off; F7 retains original heavier/vanilla switch",
        "native_compile_and_playtest": "pending local DayZ test",
        "mocked_command_checks": "Actual translated command passed 30/60/144 FPS continuous directional motion/no-dwell, single brace request, full recovery, vertical preservation, cancellation and override signature tests; native graph not modeled",
        "baseline": "stable v11 source and ZIP unchanged; v12 logic not used",
    },
}

if __name__ == "__main__":
    packer.main()
