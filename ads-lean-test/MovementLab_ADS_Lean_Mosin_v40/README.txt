Lean range v40 — first-person raised-view inspection guard

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Stand neutral briefly for existing height calibration.

The video was described as gun raised only/not sure. Raised view normally shows the gun off-centre; looking through the optic requires actual ADS. That video alone did not establish that the native ADS camera was broken.

Source issue corrected: F8 third-person inspection previously applied the custom aimed pose even in raised-only first person. V40 limits that inspection override to the third-person camera. First-person raised-only uses the normal raised pose; actual ADS still activates the approved custom pose in either view. No camera matrices, ADS inputs or shooting origin are modified.

The approved v39 WorkspaceSource and workspace PBO remain byte-identical, including its internal v39 resource filename. Gun/hand/elbow/height animations and native ADS camera are unchanged. The NPC is unchanged.

F9 now shows/logs view and camera before the existing status fields. view=raised_only with DayZPlayerCamera1stPerson means normal gun raised view; ads_camera with DayZPlayerCameraIronsights/Optics means actual sight camera. inspection_requested/applied show whether F8 is active in that view.

Use your actual ADS input to look through the sight. Test standing and walking Q/E in first person, then confirm the third-person pose. If actual ADS still looks wrong, press F9 in that view, close DayZ and run Collect-Logs.cmd; send the v40 ZIP and a short video. All other keys and range behaviour remain. Included authoring PNGs remain historical v32 previews.
