$ErrorActionPreference = "Stop"
$Version = if ($env:PT_VERSION) { $env:PT_VERSION } else { Get-Date -Format "yyyy.MM.dd" }
$ZipName = "PeakTogether-LOOM2-Windows-$Version.zip"

if (!(Test-Path ".\main.py")) { throw "Run from the loom2\ folder (.\main.py not found)." }

Write-Host "Cleaning..."
Remove-Item -Recurse -Force ".\build", ".\dist", ".\release" -ErrorAction SilentlyContinue

Write-Host "Creating build venv..."
if (!(Test-Path ".\.venv-build")) {
    if (Get-Command py -ErrorAction SilentlyContinue) { py -3.12 -m venv .venv-build }
    else { python -m venv .venv-build }
}
$Python = ".\.venv-build\Scripts\python.exe"

& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install -r requirements-runtime.txt -r requirements-build.txt

Write-Host "Building..."
& $Python -m PyInstaller ".\packaging\loom2_windows.spec" --noconfirm --clean --workpath ".\build" --distpath ".\dist"

if (!(Test-Path ".\dist\LOOM2\LOOM2.exe")) { throw "Build failed: exe missing." }

New-Item -ItemType Directory -Force ".\release" | Out-Null

@"
LOOM2 -- Sonifiquation  -  Peak Together  (Game 5)

Hear multivariable calculus. A mathematical surface z = f(x, y) becomes an
ORCHESTRA: plant a Listening Totem in the landscape and every musician inside
its hearing circle plays at once -- height becomes pitch, angle becomes timbre,
radius becomes rhythm. Move the totem and the whole song re-orchestrates.

How to play:
1. If you're reading this inside the zip, extract the zip first.
2. Open the extracted folder.
3. Double-click "LOOM2.exe".

No Python. No terminal. No installer. No admin needed. Headphones recommended.
To uninstall: delete this folder.

CONTROLS (two seats, one screen -- or one person does both):
  PLAYER 1  (keyboard)
    A / D ................. move the totem left / right   (the x axis)
    S / W ................. move the totem near / far     (the y axis)
  PLAYER 2  (mouse)
    click-drag up / down .. move the totem near / far     (the y axis)
  SHARED
    Arrow keys ............ orbit the camera (Left/Right) + tilt (Up/Down)
    Page Up / Page Down ... zoom in / out
    Home ................. recenter the camera
    1 2 3 4  (or A/B/C/D) . choose a quiz answer
    Enter ................. confirm / OK
    H ..................... hint (free, never penalized)
    C ..................... Slice Mode -- the Glass Blade (cut the surface)
    Esc ................... quit
  GAMEPAD (optional: joystick + Xbox controller)
    left stick ............ move the totem       right stick ... orbit / tilt
    A B X Y ............... answers A B C D       Start ......... confirm
    LB hint   RB slice     D-pad up/down zoom     Back .......... quit

LOOM2 teaches multivariable calculus by EAR: level curves as unison, critical
points (max / min / saddle) as chord quality, the gradient as transposition.

If it crashes, a log is written to:
%LOCALAPPDATA%\PeakTogether\LOOM2\crash-log.txt

Website: https://peaktogether.me
Source:  https://github.com/strulovitz/peaktogether-website
"@ | Set-Content -Path ".\dist\LOOM2\README-How-to-Play.txt" -Encoding UTF8

Write-Host "Zipping..."
Compress-Archive -Path ".\dist\LOOM2\*" -DestinationPath ".\release\$ZipName" -Force

$Hash = Get-FileHash ".\release\$ZipName" -Algorithm SHA256
"$($Hash.Hash)  $ZipName" | Set-Content -Path ".\release\$ZipName.sha256.txt" -Encoding ASCII

Write-Host "`nDONE."
Write-Host "  .\release\$ZipName"
Write-Host "  SHA-256: $($Hash.Hash)"
Write-Host "Test this zip on a Windows PC WITHOUT Python before uploading.`n"
