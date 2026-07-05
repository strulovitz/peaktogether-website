$ErrorActionPreference = "Stop"
$Version = if ($env:PT_VERSION) { $env:PT_VERSION } else { Get-Date -Format "yyyy.MM.dd" }
$ZipName = "PeakTogether-Homeworld-Windows-$Version.zip"

if (!(Test-Path ".\app.py")) { throw "Run from the homeworld\ folder (.\app.py not found)." }

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
& $Python -m PyInstaller ".\packaging\homeworld_windows.spec" --noconfirm --clean --workpath ".\build" --distpath ".\dist"

if (!(Test-Path ".\dist\Homeworld\Homeworld.exe")) { throw "Build failed: exe missing." }

New-Item -ItemType Directory -Force ".\release" | Out-Null

@"
Homeworld: A Good Basis  -  Peak Together  (SNEAK PEEK)

A two-player-one-screen space RTS where commanding your fleet IS doing
linear algebra. Fly your ships with vector combinations; reshape the whole
formation at once with a transformation matrix.

How to play:
1. If you're reading this inside the zip, extract the zip first.
2. Open the extracted folder.
3. Double-click "Homeworld.exe".

No Python. No terminal. No installer. No admin needed.
To uninstall: delete this folder.

CONTROLS (two seats, one screen -- or one person does both):
  PILOT  (keyboard)
    W / S  A / D  R / F ... edit the combination coefficients c1, c2, c3
    ENTER ................. commit the order (fleet flies the combination)
    X ..................... toggle diagonal / staged flight
    BACKSPACE ............. clear the coefficients
    Q / E ................. switch which squad you command
    TAB ................... select the next ship
    C ..................... recenter the camera on the selected ship
    Arrows / PgUp / PgDn .. orbit / zoom the camera
    P ..................... pause      F1 debug      F12 screenshot
    Esc ................... quit
  NAVIGATOR  (mouse -- the Bridge console)
    ORDER sliders ......... drive the same combination the Pilot sees
    TRANSFORM grid ........ edit a 3x3 matrix M, preview p -> M p on the
                            whole formation, then APPLY to reshape the fleet
                            (rotate / scale / scatter); watch det, rank, and
                            the amber fixed-axis line.

This is an early "sneak peek" build of the template game -- the full
16-mission journey home is still being built.

If it crashes, a log is written to:
%LOCALAPPDATA%\PeakTogether\Homeworld\crash-log.txt

Website: https://peaktogether.me
Source:  https://github.com/strulovitz/peaktogether-website
"@ | Set-Content -Path ".\dist\Homeworld\README-How-to-Play.txt" -Encoding UTF8

Write-Host "Zipping..."
Compress-Archive -Path ".\dist\Homeworld\*" -DestinationPath ".\release\$ZipName" -Force

$Hash = Get-FileHash ".\release\$ZipName" -Algorithm SHA256
"$($Hash.Hash)  $ZipName" | Set-Content -Path ".\release\$ZipName.sha256.txt" -Encoding ASCII

Write-Host "`nDONE."
Write-Host "  .\release\$ZipName"
Write-Host "  SHA-256: $($Hash.Hash)"
Write-Host "Test this zip on a Windows PC WITHOUT Python before uploading.`n"
