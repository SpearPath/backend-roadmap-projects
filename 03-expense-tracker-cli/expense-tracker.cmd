@echo off
set "PYTHON_EXE=python"
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    set "PYTHON_EXE=C:\Users\dmtol\AppData\Local\Programs\Python\Python313\python.exe"
)

set "SCRIPT_PATH=%~dp0main.py"
if not exist "%SCRIPT_PATH%" (
    if exist "%CD%\main.py" (
        set "SCRIPT_PATH=%CD%\main.py"
    ) else (
        set "SCRIPT_PATH=d:\code\work\backendDeveloperRoadmap\03-expense-tracker-cli\main.py"
    )
)

"%PYTHON_EXE%" "%SCRIPT_PATH%" %*
