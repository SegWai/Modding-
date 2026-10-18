# v107: correct the animation API call context

The uploaded v106 logs contain three deaths. All captured 91 bones and bound 546 controls, but each failed the transform readback check. Maximum position errors were 1.48449, 0.812862 and 0.836397 m; corresponding basis errors were 1.99962, 1.87864 and 1.9997. Each waited approximately 1.5 seconds and returned to native death. There was no physics activation. Weather/config warnings are not evidence of a procedural-graph failure.

The SDK DayZPlayer API explicitly documents AnimSetFloat as usable only from CommandHandler. v106 called it from the scheduled fixture update. v107 queues values on the custom corpse, submits them only inside its CommandHandler after super, and resubmits each command tick. Baseline capture and corrected-pose readback require the submitted revision and a further command tick. Acknowledgement proves the script submission ran in context, not that the native graph evaluated correctly.

Failed handoffs now have a 350 ms deadline instead of 1500 ms. Original simulation/collision/visibility rollback remains. Core joints log target, baseline and actual transforms at the first mismatch; timeout logs queued/submitted revisions, native command-tick count and final errors. This separates lack of command execution from remaining transform or graph semantics errors.

The generated graph, transform math, match limits and root momentum calculation are unchanged. Player movement/camera/pose smoothing, mission and other fixtures are preserved. Tests include an executable C++ adaptation of the actual queue and acknowledgement methods, checking deferred writes, all 547 controls, stable IDs, overwrites and extra-tick waits. This is not native Enforce compilation or gameplay validation.
