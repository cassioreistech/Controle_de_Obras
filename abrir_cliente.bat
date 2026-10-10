@echo off
cd /d "%~dp0"
set "CONTROLE_OBRAS_DATA_DIR=%APPDATA%\ControleDeObras_cliente"
set "PYTHONPATH=%~dp0src"
start "" ".venv\Scripts\pythonw.exe" -m controle_obras.main