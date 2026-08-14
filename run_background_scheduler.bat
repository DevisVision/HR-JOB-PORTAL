@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m services.background_scheduler
