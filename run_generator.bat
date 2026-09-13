@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m src.generator >> logs\generator_cron.log 2>&1
