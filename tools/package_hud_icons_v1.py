#!/usr/bin/env python3
import sys
sys.dont_write_bytecode=True
import package_movement_logic_test as packer
packer.SOURCE=packer.ROOT/'hud-icons-test/MovementLabHUDIcons_v1'
packer.OUTPUT=packer.ROOT/'artifacts/MovementLab_HUD_Icons_v1.zip'
packer.ARCHIVE_ROOT=packer.SOURCE.name
packer.VALIDATION_EXTRA={
 'variant':'image HUD:23 reference-chart tiles plus added third slow-aim tile; latest SNAFU/optional arms test retained',
 'checks':'actual read-only icon accessor and actual HUD executed in C++ mocks; stable world/mission code comparison; native PAA mip/header verification and independent armake decode; PBO package integrity',
 'limitations':'Native Enforce compilation and DayZ renderer not executed. Confirm image UV orientation, dimensions and placement locally. SNAFU loadout and optional arms renderer retain prior test limitations. Only HUD artwork/selection presentation changed; no speed values or timers changed.'
}
if __name__=='__main__':packer.main()
