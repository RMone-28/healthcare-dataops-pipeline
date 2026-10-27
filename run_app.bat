@echo off
title Healthcare DataOps Pipeline Control Center
echo ======================================================================
echo    Starting Healthcare DataOps Control Center (Roll No: 23ME1A54C7)
echo    Supervisor: Dr. P. Sudhakar
echo ======================================================================
echo.
cd /d %~dp0
streamlit run app.py
pause
