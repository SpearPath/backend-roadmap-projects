@echo off
setlocal

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python "%~dp0main.py" %*
    exit /b %ERRORLEVEL%
)

where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py "%~dp0main.py" %*
    exit /b %ERRORLEVEL%
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" "%~dp0main.py" %*
    exit /b %ERRORLEVEL%
)

echo Error: Python was not found in PATH.
exit /b 1
