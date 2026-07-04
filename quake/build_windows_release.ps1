$ErrorActionPreference = "Stop"
$Version = if ($env:PT_VERSION) { $env:PT_VERSION } else { Get-Date -Format "yyyy.MM.dd" }
$ZipName = "PeakTogether-Quake-Windows-$Version.zip"

if (!(Test-Path ".\app.py")) { throw "Run from the quake\ folder (.\app.py not found)." }

Write-Host "Cleaning..."
# NOTE: do NOT delete .\build -- that folder holds Quake's SOURCE build scripts
# (room_from_spec.py, build_all.py, ...). PyInstaller work goes to .\.pyi-build instead.
Remove-Item -Recurse -Force ".\.pyi-build", ".\dist", ".\release" -ErrorAction SilentlyContinue

Write-Host "Creating build venv..."
if (!(Test-Path ".\.venv-build")) {
    if (Get-Command py -ErrorAction SilentlyContinue) { py -3.12 -m venv .venv-build }
    else { python -m venv .venv-build }
}
$Python = ".\.venv-build\Scripts\python.exe"

& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install -r requirements-runtime.txt -r requirements-build.txt

Write-Host "Building..."
& $Python -m PyInstaller ".\packaging\quake_windows.spec" --noconfirm --clean --workpath ".\.pyi-build" --distpath ".\dist"

if (!(Test-Path ".\dist\Quake\Quake.exe")) { throw "Build failed: exe missing." }

New-Item -ItemType Directory -Force ".\release" | Out-Null

@"
Quake  -  Peak Together

A first-person walk through Newton's Principia as a 3D dungeon.

How to play:
1. If you're reading this inside the zip, extract the zip first.
2. Open the extracted folder.
3. Double-click "Quake.exe".

No Python. No terminal. No installer. No admin needed.
To uninstall: delete this folder.

CONTROLS (co-op: one player moves, one player aims -- or one person does both):
  Keyboard + Mouse
    W A S D .......... move / strafe
    Mouse ............ look around + aim the reticle
    Left-click ....... shoot a panel (colors it) / shoot the demon
    R ................ read a panel up close (toggle)
    Esc .............. quit
  Optional controllers (work at the same time as keyboard + mouse):
    Joystick (Thrustmaster T.16000M) -> the MOVER
       stick = walk/strafe, twist = turn, throttle slider = run forward/back
    Xbox controller -> the AIMER
       right stick = look + aim, right trigger or A = shoot

If it crashes, a log is written to:
%LOCALAPPDATA%\PeakTogether\Quake\crash-log.txt

Website: https://peaktogether.me
Source:  https://github.com/strulovitz/peaktogether-website
"@ | Set-Content -Path ".\dist\Quake\README - How to Play.txt" -Encoding UTF8

Write-Host "Zipping..."
Compress-Archive -Path ".\dist\Quake\*" -DestinationPath ".\release\$ZipName" -Force

$Hash = Get-FileHash ".\release\$ZipName" -Algorithm SHA256
"$($Hash.Hash)  $ZipName" | Set-Content -Path ".\release\$ZipName.sha256.txt" -Encoding ASCII

Write-Host "`nDONE."
Write-Host "  .\release\$ZipName"
Write-Host "  SHA-256: $($Hash.Hash)"
Write-Host "Test this zip on a Windows PC WITHOUT Python before uploading.`n"
