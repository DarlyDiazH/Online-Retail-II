@echo off
chcp 65001 >nul
title Backend - Online Retail II
cd /d "%~dp0"
set PY=
where py >nul 2>nul && set PY=py
if not defined PY (where python >nul 2>nul && set PY=python)
if not defined PY goto sinpython
%PY% --version >nul 2>&1 || goto sinpython

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo Se creo el archivo backend\.env. Abrelo y pega la cadena de conexion de Neon en DATABASE_URL.
  echo Sin eso la API funciona con una base local de prueba, sin los segmentos reales.
  echo.
)

echo Instalando dependencias (solo tarda la primera vez)...
%PY% -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo ERROR instalando dependencias. Revisa tu conexion a internet.
  pause
  exit /b 1
)

echo.
echo API lista en http://localhost:8000   (documentacion: http://localhost:8000/docs)
echo Deja esta ventana abierta mientras usas la pagina. Para detener: Ctrl+C
echo.
%PY% -m uvicorn app.main:app --reload --port 8000
pause
exit /b 0

:sinpython
echo ERROR: Python no esta instalado. Descargalo en https://www.python.org/downloads/
echo y marca "Add python.exe to PATH" al instalar.
pause
exit /b 1
