#!/usr/bin/env bash
set -euo pipefail

movementlab_addon_dir=/tmp/dayz-animation-plugin
movementlab_addon_commit=7075310c8aa3ae75f9487168577661809e5caa15
movementlab_support_dir=/tmp/dayz-local-workbench

test "$(blender --version | head -n 1)" = 'Blender 4.3.2' || {
  printf '%s\n' 'This authoring workflow was validated with Blender 4.3.2.' >&2
  exit 1
}

if [ ! -e "$movementlab_addon_dir" ]; then
  git clone --filter=blob:none --no-checkout \
    https://github.com/jdfnc24/DayZAnimationPluginDemo.git "$movementlab_addon_dir"
  git -C "$movementlab_addon_dir" checkout --detach "$movementlab_addon_commit"
fi
test "$(git -C "$movementlab_addon_dir" rev-parse HEAD)" = "$movementlab_addon_commit" || {
  printf '%s\n' 'The dependency checkout has a different revision; preserve it and inspect before proceeding.' >&2
  exit 1
}
test -z "$(git -C "$movementlab_addon_dir" status --porcelain -- . ':!**/__pycache__/**')" || {
  printf '%s\n' 'The dependency checkout has local changes; preserve them before proceeding.' >&2
  exit 1
}
git -C "$movementlab_addon_dir" sparse-checkout set BlenderPlugin _AssetSamples/Poses/Unarmed

mkdir -p "$movementlab_support_dir/blender-config" "$movementlab_support_dir/blender-extensions"
movementlab_rig_temp=$(mktemp "$movementlab_support_dir/rig.XXXXXX")
trap 'rm -f "$movementlab_rig_temp"' EXIT
git -C "$movementlab_addon_dir" show \
  'HEAD:_AssetSamples/JD_Master_Rig (No IK Bones).blend' > "$movementlab_rig_temp"
if [ -e "$movementlab_support_dir/dayz_reference_rig.blend" ]; then
  cmp "$movementlab_rig_temp" "$movementlab_support_dir/dayz_reference_rig.blend"
else
  mv "$movementlab_rig_temp" "$movementlab_support_dir/dayz_reference_rig.blend"
fi
test -s "$movementlab_support_dir/dayz_reference_rig.blend"
test -f "$movementlab_addon_dir/BlenderPlugin/DayzAnimationTools/Export/ExportTxa.py"
printf '%s\n' 'Pinned DayZ authoring dependencies prepared; Windows Workbench validation is separate.'
