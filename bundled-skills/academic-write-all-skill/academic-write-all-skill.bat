@echo off
setlocal

set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo [academic-write-all-skill] runtime missing, bootstrapping first...
  call "%ROOT%bootstrap_academic_write_all_skill_runtime.bat" || exit /b 1
)

"%PY%" "%ROOT%scripts\awas_cli.py" %*
exit /b %errorlevel%
