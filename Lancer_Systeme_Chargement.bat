@echo off
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Le programme s'est arrete avec une erreur.
    pause
)
