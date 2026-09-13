@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m src.loader >> logs\loader_cron.log 2>&1
