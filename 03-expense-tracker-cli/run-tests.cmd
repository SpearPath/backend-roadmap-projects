@echo off
set "PYTHON_EXE=python"
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    set "PYTHON_EXE=C:\Users\dmtol\AppData\Local\Programs\Python\Python313\python.exe"
)
"%PYTHON_EXE%" -m unittest discover tests -v
