@echo off
setlocal
set "DAYZ_FPS_SCRIPT=%~f0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$s=[IO.File]::ReadAllText($env:DAYZ_FPS_SCRIPT); & ([scriptblock]::Create(($s -split '(?m)^# POWERSHELL_START\r?$',2)[1]))"
set "DAYZ_FPS_RESULT=%errorlevel%"
echo.
pause
exit /b %DAYZ_FPS_RESULT%
# POWERSHELL_START
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

function Read-ConfigText([byte[]]$Bytes) {
    $offset = 0
    $bom = [byte[]]@()
    if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 239 -and $Bytes[1] -eq 187 -and $Bytes[2] -eq 191) {
        $encoding = New-Object System.Text.UTF8Encoding($false, $true)
        $offset = 3; $bom = [byte[]]@(239,187,191)
    } elseif ($Bytes.Length -ge 2 -and $Bytes[0] -eq 255 -and $Bytes[1] -eq 254) {
        $encoding = [Text.Encoding]::Unicode
        $offset = 2; $bom = [byte[]]@(255,254)
    } elseif ($Bytes.Length -ge 2 -and $Bytes[0] -eq 254 -and $Bytes[1] -eq 255) {
        $encoding = [Text.Encoding]::BigEndianUnicode
        $offset = 2; $bom = [byte[]]@(254,255)
    } else {
        $encoding = New-Object System.Text.UTF8Encoding($false, $true)
        try { $null = $encoding.GetString($Bytes) }
        catch { $encoding = [Text.Encoding]::Default }
    }
    [pscustomobject]@{ Text = $encoding.GetString($Bytes, $offset, $Bytes.Length - $offset); Encoding = $encoding; Bom = $bom }
}

function Edit-ConfigText([string]$Text) {
    # Only edit settings which already exist. Do not inject obsolete/unsupported keys.
    # A ceiling lowers expensive settings; a floor makes terrain mesh less detailed.
    $rules = @(
        @{ Name='sceneComplexity'; Value=200000; Mode='Ceiling' },
        @{ Name='shadowZDistance'; Value=100; Mode='Ceiling' },
        @{ Name='viewDistance'; Value=1600; Mode='Ceiling' },
        @{ Name='preferredObjectViewDistance'; Value=1000; Mode='Ceiling' },
        @{ Name='terrainGrid'; Value=25; Mode='Floor' },
        @{ Name='FSAA'; Value=0; Mode='Ceiling' },
        @{ Name='AToC'; Value=0; Mode='Ceiling' },
        @{ Name='SSAO'; Value=0; Mode='Ceiling' },
        @{ Name='vsync'; Value=0; Mode='Ceiling' }
    )
    $changes = New-Object 'System.Collections.Generic.List[object]'
    foreach ($rule in $rules) {
        $pattern = '(?im)^(?<prefix>[ \t]*' + [regex]::Escape($rule.Name) + '[ \t]*=[ \t]*)(?<number>[-+]?[0-9]+(?:\.[0-9]+)?)(?<suffix>[ \t]*;[^\r\n]*)$'
        $regex = New-Object System.Text.RegularExpressions.Regex($pattern)
        # Reverse iteration preserves string offsets when several matches exist.
        $matches = $regex.Matches($Text)
        for ($i=$matches.Count-1; $i -ge 0; $i--) {
            $match = $matches[$i]
            $old = [double]::Parse($match.Groups['number'].Value, [Globalization.CultureInfo]::InvariantCulture)
            $change = (($rule.Mode -eq 'Ceiling' -and $old -gt $rule.Value) -or ($rule.Mode -eq 'Floor' -and $old -lt $rule.Value))
            if ($change) {
                $replacement = $match.Groups['prefix'].Value + [string]$rule.Value + $match.Groups['suffix'].Value
                $Text = $Text.Remove($match.Index, $match.Length).Insert($match.Index, $replacement)
                $changes.Add([pscustomobject]@{ Setting=$rule.Name; Before=$old; After=$rule.Value })
            }
        }
    }
    [pscustomobject]@{ Text=$Text; Changes=$changes.ToArray() }
}

function Apply-Preset([string[]]$Roots, [string]$BackupBase) {
    $files = @($Roots | ForEach-Object {
        Get-ChildItem -LiteralPath $_ -File | Where-Object { $_.Extension -in @('.cfg','.DayZProfile') }
    } | Sort-Object -Property FullName -Unique)
    $plans = New-Object 'System.Collections.Generic.List[object]'
    foreach ($file in $files) {
        $bytes = [IO.File]::ReadAllBytes($file.FullName)
        $read = Read-ConfigText $bytes
        $edited = Edit-ConfigText $read.Text
        if ($edited.Changes.Count -eq 0) { continue }
        if ($file.IsReadOnly) { throw "Read-only config: $($file.FullName). Nothing has been changed." }
        $newBytes = [byte[]]($read.Bom + $read.Encoding.GetBytes($edited.Text))
        $plans.Add([pscustomobject]@{ Path=$file.FullName; Original=$bytes; Updated=$newBytes; Changes=$edited.Changes })
    }
    if ($plans.Count -eq 0) {
        Write-Host 'No matching settings need changing. Your version may store them elsewhere, or they are already at this preset.'
        Write-Host 'Use the in-game settings listed in README.txt if no changes were found.'
        return
    }
    $backup = Join-Path $BackupBase ((Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,6))
    $null = New-Item -ItemType Directory -Path $backup -Force
    $manifest = New-Object 'System.Collections.Generic.List[object]'
    # All originals are backed up BEFORE any configuration is changed.
    for ($i=0; $i -lt $plans.Count; $i++) {
        $name = '{0:D3}.original' -f $i
        $destination = Join-Path $backup $name
        [IO.File]::WriteAllBytes($destination, $plans[$i].Original)
        $manifest.Add([pscustomobject]@{ Path=$plans[$i].Path; Backup=$name; SHA256=(Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash })
    }
    $manifest.ToArray() | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backup 'manifest.json') -Encoding UTF8
    try {
        foreach ($plan in $plans) { [IO.File]::WriteAllBytes($plan.Path, $plan.Updated) }
    } catch {
        $failure = $_
        foreach ($plan in $plans) {
            try { [IO.File]::WriteAllBytes($plan.Path, $plan.Original) }
            catch { Write-Warning "Automatic rollback failed for $($plan.Path). Restore from $backup" }
        }
        throw $failure
    }
    foreach ($plan in $plans) {
        Write-Host "`n$($plan.Path)"
        $plan.Changes | Format-Table -AutoSize | Out-Host
    }
    Write-Host "Backup: $backup"
    Write-Host 'Applied. Launch DayZ normally. Settings stay editable in-game.'
    Write-Host 'Visual tradeoffs: more object pop-in, simpler distant terrain/shadows, and jagged foliage. VSync off can cause tearing.'
}

function Restore-Preset([string]$BackupBase) {
    if (-not (Test-Path -LiteralPath $BackupBase -PathType Container)) { Write-Host 'No backups found.'; return }
    $backups = @(Get-ChildItem -LiteralPath $BackupBase -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'manifest.json') } | Sort-Object Name -Descending)
    if ($backups.Count -eq 0) { Write-Host 'No backups found.'; return }
    for ($i=0; $i -lt $backups.Count; $i++) { Write-Host ("{0}. {1}" -f ($i+1),$backups[$i].Name) }
    $selected = 0
    $answer = Read-Host 'Choose backup number to restore (Enter cancels)'
    if ([string]::IsNullOrWhiteSpace($answer)) { return }
    if (-not [int]::TryParse($answer, [ref]$selected) -or $selected -lt 1 -or $selected -gt $backups.Count) { throw 'Invalid backup number.' }
    $folder = $backups[$selected-1].FullName
    $manifest = @(Get-Content -LiteralPath (Join-Path $folder 'manifest.json') -Raw | ConvertFrom-Json)
    foreach ($entry in $manifest) {
        if ($entry.Backup -notmatch '^[0-9]{3}\.original$') { throw 'Invalid backup filename.' }
        if ([IO.Path]::GetExtension($entry.Path) -notin @('.cfg','.DayZProfile')) { throw 'Unexpected restore target.' }
        $source = Join-Path $folder $entry.Backup
        if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $entry.SHA256) { throw "Backup verification failed: $source" }
        if (-not (Test-Path -LiteralPath ([IO.Path]::GetDirectoryName($entry.Path)) -PathType Container)) { throw "Original folder no longer exists: $($entry.Path)" }
    }
    foreach ($entry in $manifest) { [IO.File]::WriteAllBytes($entry.Path, [IO.File]::ReadAllBytes((Join-Path $folder $entry.Backup))) }
    Write-Host 'Original settings restored.'
}

try {
    Write-Host 'DayZ FPS Helper - reversible graphics preset'
    Write-Host 'No administrator access is needed. No registry, services, game assets or anti-cheat changes.'
    if (Get-Process -Name 'DayZ_x64','DayZDiag_x64' -ErrorAction SilentlyContinue) { throw 'Close DayZ before applying or restoring settings.' }
    $backupBase = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'DayZ_FPS_Helper\Backups'
    Write-Host "`n1. Apply preset`n2. Restore a backup`n3. Exit"
    $choice = Read-Host 'Choose 1, 2 or 3'
    switch ($choice) {
        '1' {
            $roots = New-Object 'System.Collections.Generic.List[string]'
            $default = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'DayZ'
            if (Test-Path -LiteralPath $default -PathType Container) { $roots.Add($default); Write-Host "Default settings: $default" }
            Write-Host 'If you use a custom -profiles folder (such as MovementLab), enter that folder too.'
            $custom = (Read-Host 'Additional profile folder, or Enter to skip').Trim().Trim('"')
            if ($custom) {
                if (-not (Test-Path -LiteralPath $custom -PathType Container)) { throw 'That profile folder does not exist.' }
                $roots.Add((Get-Item -LiteralPath $custom).FullName)
            }
            if ($roots.Count -eq 0) { throw 'No profile folder found. Launch DayZ once and save its video settings, then retry.' }
            Apply-Preset -Roots $roots.ToArray() -BackupBase $backupBase
        }
        '2' { Restore-Preset -BackupBase $backupBase }
        '3' { exit 0 }
        default { throw 'Invalid menu choice.' }
    }
    exit 0
} catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
