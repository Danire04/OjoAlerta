@echo off
setlocal
cd /d "%~dp0"
set "OJOALERTA_PYTHON=python"
if exist ".venv\Scripts\python.exe" set "OJOALERTA_PYTHON=.venv\Scripts\python.exe"
"%OJOALERTA_PYTHON%" -X utf8 -m streamlit run app.py
if errorlevel 1 pause
