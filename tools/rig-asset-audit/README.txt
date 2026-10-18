MovementLab - collect human/infected rig assets for investigation

This is an asset collector, NOT another ragdoll mod. It does not change DayZ, the work-drive files or your installed mod, and does not upload anything automatically. It copies selected extracted assets to a new output folder and makes ZIP parts for you to send.

1. Extract this small tool ZIP to a writable folder.
2. Run Collect-Ragdoll-Assets.cmd.
3. It checks your earlier D:\DayZProjects and P:\ locations. If necessary, enter the folder containing the extracted dz\anims and dz\characters trees.
4. Send the generated Part-XX.zip files back in chat. Each archive is limited to approximately 20MB of collected file data plus its manifest.

A mounted P: drive alone is not enough: the game data must already be extracted through DayZ Tools. This tool deliberately does not guess or invoke extraction commands. For a custom location, you can also run:
Collect-Ragdoll-Assets.cmd -WorkDrive "E:\MyDayZWorkDrive"

Includes: relevant human/infected animation graph/workspace metadata, available rig/physics definitions, character configs/model.cfg, hermit zombie models, human body models and Denis head models when present. Excludes textures/audio and large animation clips at this stage. An inventory of other asset names helps locate references that were missed by the first selection.

Copies include SHA256 hashes and P3D header identification. ODOL means a binarized model; it is not automatically an editable source model. Comparing extracted assets may reveal that a custom/editable mesh or engine support is still required. Collection cannot guarantee that native infected ragdoll can be enabled.

The Windows PowerShell collector uses built-in PowerShell 5.1 commands; no Python installation is needed. It has been reviewed but cannot be executed/verified in this Linux environment. Its shared asset-selection rules and the companion audit parser have automated Python fixture checks. If the collector reports an error, send the error text rather than changing your game setup blindly.
