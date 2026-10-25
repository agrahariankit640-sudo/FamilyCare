@echo off
cd /d "%~dp0"
title FamilyCare Web Server - DO NOT CLOSE
color 0A
cls
echo ================================================================
echo           FamilyCare - Digital Family Health Record
echo ================================================================
echo.
echo   [!] IMPORTANT: KEEP THIS WINDOW OPEN!
echo   [!] If you close this black window, the website will STOP working.
echo   [!] You can minimize this window to the taskbar.
echo.
echo   Opening Chrome now...
echo   URL 1: http://127.0.0.1:5000
echo   URL 2: http://localhost:5000
echo.
echo   Demo Login  : demo@familycare.com  / Demo@123
echo   Admin Login : admin@familycare.com / Admin@123
echo ================================================================
echo.
start http://127.0.0.1:5000
".\venv\Scripts\python.exe" "app.py"
echo.
echo Server has stopped.
pause
