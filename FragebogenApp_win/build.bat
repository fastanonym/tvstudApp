@echo off
title Baue FragebogenApp mit PyInstaller...
echo Starte Build-Prozess...

REM Stelle sicher, dass wir im Projektverzeichnis sind
cd /d %~dp0

REM Baue die App mit PyInstaller und der .spec-Datei
pyinstaller build.spec

echo.
echo Build abgeschlossen. Die EXE befindet sich in: dist\FragebogenApp\
pause