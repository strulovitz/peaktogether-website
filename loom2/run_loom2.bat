@echo off
REM ============================================================
REM  LOOM2 -- Sonifiquation : run it yourself, Nir!  :-)
REM  Double-click this file, OR run it from PowerShell.
REM  Unbuffered (-u) so you see prints LIVE; the window stays
REM  open after exit so you can read any message / traceback.
REM ============================================================
setlocal
cd /d "%~dp0"
echo Launching LOOM2 -- Sonifiquation ...
echo (Close the game window, or press Esc, to quit.)
echo.
python -u main.py
echo.
echo ============================================================
echo LOOM2 has exited. Read any message above.
echo ============================================================
pause
endlocal
