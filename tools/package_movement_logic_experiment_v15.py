#!/usr/bin/env python3
"""Build a separate v11-based native pose/physics experiment."""
import sys
sys.dont_write_bytecode = True
import package_movement_logic_test as packer

packer.SOURCE = packer.ROOT / "movement-logic-experiments/MovementLabMovementLogicTest_v15"
packer.OUTPUT = packer.ROOT / "artifacts/MovementLab_Movement_Logic_Experiment_v15.zip"
packer.ARCHIVE_ROOT = "MovementLabMovementLogicExperiment_v15"
packer.VALIDATION_EXTRA = {
    "variant": "v15 clean stable v11 baseline plus only the v14 moving reversal",
    "experiment_v15": {
        "requested_recovery_seconds": 0.50,
        "native_pose_command": "CMD_SlidingPose",
        "animation_gait": 2,
        "horizontal_translation": "continuous old/new vector momentum and heavy speed recovery through PrePhys_SetTranslation",
        "pose_progression": "single native brace command, no directional atlas sweep, native outgoing blend and seeded native handoff; no stationary hold or animation clock slowdown",
        "toggle": "F8 experiment on/off; F7 retains original heavier/vanilla switch",
        "native_compile_and_playtest": "pending local DayZ test",
        "mocked_command_checks": "Actual translated command/handoff passed 30/60/144 FPS; ordinary v11 startup/braking methods verified equal; native graph not modeled",
        "baseline": "fresh copy of stable v11; ordinary braking/startup methods identical; only moving reversal added; no v12 stop sequence or v13 stationary hold",
    },
}

if __name__ == "__main__":
    packer.main()
