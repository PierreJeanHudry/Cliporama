@echo off
REM Double-clique sur ce fichier pour lancer le bot (telephone branche, debogage USB actif).
cd /d "%~dp0"
if not exist .venv (
  echo Installation des dependances (une seule fois)...
  py -3 -m venv .venv || python -m venv .venv
  .venv\Scripts\python -m pip install -r requirements.txt
)
.venv\Scripts\python -m foodhunt run %*
pause
