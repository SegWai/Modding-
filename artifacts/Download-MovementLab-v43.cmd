@echo off
setlocal
set "MOVEMENTLAB_DOWNLOADER=%~f0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$content = [IO.File]::ReadAllText($env:MOVEMENTLAB_DOWNLOADER); $parts = $content -split '(?m)^# POWERSHELL_START\r?$', 2; & ([ScriptBlock]::Create($parts[1]))"
if errorlevel 1 (
    echo Download failed. Check the message above. Run this file again to retry.
    pause
    exit /b 1
)
exit /b 0
# POWERSHELL_START
$ErrorActionPreference = 'Stop'
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $commit = 'b9c9e889df33d0bf3981260940979cc0f7c649a0'
    $prefix = 'hud-icons-test/MovementLabLocomotion_v43/'
    $parentFolder = [IO.Path]::GetDirectoryName($env:MOVEMENTLAB_DOWNLOADER)
    $destination = Join-Path $parentFolder 'MovementLabLocomotion_v43'
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    $headers = @{ 'User-Agent' = 'MovementLab-Downloader'; 'Accept' = 'application/vnd.github+json' }
    Write-Host 'Downloading v43 directly into a folder. No ZIP or Git installation required.'
    $tree = Invoke-RestMethod -Uri "https://api.github.com/repos/SegWai/Modding-/git/trees/${commit}?recursive=1" -Headers $headers
    if ($tree.truncated) { throw 'GitHub returned an incomplete file list. No files were downloaded.' }
    $files = @($tree.tree | Where-Object { $_.type -eq 'blob' -and $_.path.StartsWith($prefix) })
    if ($files.Count -lt 1) { throw 'The v43 file list is empty.' }
    $number = 0
    foreach ($file in $files) {
        $relative = $file.path.Substring($prefix.Length)
        $target = [IO.Path]::GetFullPath((Join-Path $destination $relative))
        if (!$target.StartsWith($destination + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid download path.' }
        New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($target)) | Out-Null
        $number++
        Write-Progress -Activity 'Downloading MovementLab v43' -Status "$number / $($files.Count): $relative" -PercentComplete (100 * $number / $files.Count)
        $urlPath = ($file.path.Split('/') | ForEach-Object { [Uri]::EscapeDataString($_) }) -join '/'
        $temporary = $target + '.downloading'
        $downloaded = $false
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            try {
                Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/SegWai/Modding-/$commit/$urlPath" -OutFile $temporary
                if ((Get-Item -LiteralPath $temporary).Length -ne $file.size) { throw "Incomplete file: $relative" }
                $bytes = [IO.File]::ReadAllBytes($temporary)
                $blobHeader = [Text.Encoding]::ASCII.GetBytes("blob $($bytes.Length)" + [char]0)
                $sha = [Security.Cryptography.SHA1]::Create()
                try {
                    $sha.TransformBlock($blobHeader, 0, $blobHeader.Length, $blobHeader, 0) | Out-Null
                    $sha.TransformFinalBlock($bytes, 0, $bytes.Length) | Out-Null
                    $actualHash = ([BitConverter]::ToString($sha.Hash)).Replace('-', '').ToLowerInvariant()
                } finally { $sha.Dispose() }
                if ($actualHash -ne $file.sha) { throw "File verification failed: $relative" }
                Move-Item -LiteralPath $temporary -Destination $target -Force
                $downloaded = $true
                break
            } catch {
                if ($attempt -eq 3) { throw }
            }
        }
        if (!$downloaded) { throw "Could not download $relative" }
    }
    Write-Progress -Activity 'Downloading MovementLab v43' -Completed
    Write-Host "Ready: $destination" -ForegroundColor Green
    Write-Host 'Open Launch-Movement-Test.cmd in that folder when ready.'
    Start-Process explorer.exe -ArgumentList ('"' + $destination + '"')
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
