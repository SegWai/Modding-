# v98 runtime result and v99 identifier hypothesis

The uploaded logs contain two completed deaths, with 424 and 393 callback frames. No read-input abort or identity fallback was needed. GetBoneIndexByName("Head") returns 2090324343; GetBoneIndex("Head") returns 41. Using the former, GetBonePositionMS and GetBoneTransformMS provide matching, nonzero head positions and a nonzero orientation basis. This verifies that the skeletal reading correction works in the user's runtime.

SetBoneMatrix and GetBoneMatrix still return false with that same identifier. SetBoneGlobal has no return value. Its later model readback is not the requested head position; native death motion also occurs during that interval, so this cannot be called a successful write or evidence that an accepted write was overwritten. No user-visible movement result for v98 has been supplied.

## What remains untested

The identifiers returned by the animation and model lookups are clearly different. The generic envisual writer's identifier contract is not documented in the inspected source. It is plausible that it expects the compact model index, not the opaque animation-reader identifier. This is a hypothesis, not a proven API contract.

v97 used model index41 but submitted a zero-filled basis. v98 obtained a valid basis but used the animation-reader identifier for the writer. Therefore the valid matrix plus model-index combination has not been tested. v99 isolates that combination: reader calls use GetBoneIndexByName's result; generic writer/readback calls use GetBoneIndex's result. The rest of the marker, bounds, timing, simulation and fixtures are unchanged.

There is still no demonstrated script route for visible infected skeletal writes or articulated physics activation. v99 is not presented as a ragdoll fix. If the model-index writer also rejects the valid matrix, further repetitions of these matrix functions are not justified without new API/asset evidence.

## Run

Extract MovementLab_Bone_Probe_v99.zip into a fresh folder, launch, kill the zombie, watch its head for four seconds and report whether the head visibly moves. Close DayZ, run Collect-Logs.cmd and send MovementLab-Bone-v99-Logs.zip. No Workbench operation or asset recollection is required.

## Checks

Source checks confirm each reader/writer uses its intended identifier, no prior human proxy is introduced, and fixture hooks are byte-identical to v98. Packaging verifies PBO contents, prefix, offsets and SHA1 plus ZIP integrity. Native v99 compilation and rendering remain pending the local test. Raw logs are not republished; derived marker data is recorded in v98-bone-write-results.json.
