@echo off
title Stop FamilyCare Server
echo Stopping FamilyCare server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo Server on port 5000 has been stopped.
timeout /t 3 >nul
