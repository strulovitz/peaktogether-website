$ErrorActionPreference = "Stop"
$Version = if ($env:PT_VERSION) { $env:PT_VERSION } else { Get-Date -Format "yyyy.MM.dd" }
$ZipName = "PeakTogether-DescentQED-Windows-$Version.zip"

if (!(Test-Path ".\descent\app.py")) { throw "Run from repo root (\.descent\app.py not found)." }

Write-Host "Cleaning..."
Remove-Item -Recurse -Force ".\build", ".\dist", ".\release" -ErrorAction SilentlyContinue

Write-Host "Creating build venv..."
if (!(Test-Path ".\.venv-build")) { py -3.12 -m venv .venv-build }
$Python = ".\.venv-build\Scripts\python.exe"

& $Python -m pip install --upgrade pip setuptools wheel
& $Python -m pip install -r requirements-runtime.txt -r requirements-build.txt

Write-Host "Building..."
& $Python -m PyInstaller ".\packaging\descent_qed_windows.spec" --noconfirm --clean

if (!(Test-Path ".\dist\Descent QED\Descent QED.exe")) { throw "Build failed: exe missing." }

New-Item -ItemType Directory -Force ".\release" | Out-Null

@"
Descent QED  -  Peak Together

How to play:
1. If you're reading this inside the zip, extract the zip first.
2. Open the extracted folder.
3. Double-click "Descent QED.exe".

No Python. No terminal. No installer. No admin needed.
To uninstall: delete this folder.

If it crashes, a log may appear at:
%LOCALAPPDATA%\PeakTogether\DescentQED\crash-log.txt

Website: https://peaktogether.me
Source:  https://github.com/strulovitz/peaktogether-website
"@ | Set-Content -Path ".\dist\Descent QED\README - How to Play.txt" -Encoding UTF8

Write-Host "Zipping..."
Compress-Archive -Path ".\dist\Descent QED\*" -DestinationPath ".\release\$ZipName" -Force

$Hash = Get-FileHash ".\release\$ZipName" -Algorithm SHA256
"$($Hash.Hash)  $ZipName" | Set-Content -Path ".\release\$ZipName.sha256.txt" -Encoding ASCII

Write-Host "`nDONE."
Write-Host "  .\release\$ZipName"
Write-Host "  SHA-256: $($Hash.Hash)"
Write-Host "Test this zip on a Windows PC WITHOUT Python before uploading.`n"
