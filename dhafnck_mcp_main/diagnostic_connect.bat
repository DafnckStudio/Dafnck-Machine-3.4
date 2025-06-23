@echo off
REM Diagnostic batch script for dhafnck_mcp_main (Windows/Cursor)
REM Runs the WSL-based diagnostic_connect.sh from Windows

REM Change to project directory (if not already there)
cd /d %~dp0

REM Print info
echo =============================================
echo  Running MCP Diagnostic (WSL) for dhafnck_mcp_main
echo =============================================

REM Run the diagnostic script in WSL
wsl bash diagnostic_connect.sh

REM Capture exit code
set EXITCODE=%ERRORLEVEL%

REM Print result
echo.
echo Diagnostic script exited with code %EXITCODE%.

exit /b %EXITCODE% 