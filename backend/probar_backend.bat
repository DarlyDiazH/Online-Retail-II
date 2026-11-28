@echo off
chcp 65001 >nul
cd /d "%~dp0"
set LOG=%~dp0resultado_pruebas.txt
echo Probando el modulo de carrito... (no cierres esta ventana)
echo === %date% %time% === > "%LOG%"
set PY=
where py >nul 2>nul && set PY=py
if not defined PY (where python >nul 2>nul && set PY=python)
if not defined PY (
  echo ERROR: Python no esta instalado en este PC. >> "%LOG%"
  echo ERROR: Python no esta instalado. Descargalo en https://www.python.org/downloads/
  pause
  exit /b 1
)
%PY% --version >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: Python no esta instalado en este PC. >> "%LOG%"
  echo ERROR: Python no esta instalado. Instalalo desde https://www.python.org/downloads/ marcando "Add python.exe to PATH".
  pause
  exit /b 1
)
echo Instalando dependencias (puede tardar 1-2 minutos)...
echo --- instalando paquetes de prueba --- >> "%LOG%"
%PY% -m pip install -q --only-binary=:all: fastapi "sqlalchemy>=2" httpx python-dotenv bcrypt >> "%LOG%" 2>&1
echo --- verificando driver de Neon (psycopg2) --- >> "%LOG%"
%PY% -m pip install -q --only-binary=:all: psycopg2-binary >> "%LOG%" 2>&1 && echo psycopg2 OK >> "%LOG%"
echo --- pruebas --- >> "%LOG%"
echo Ejecutando pruebas...
%PY% -m unittest -v >> "%LOG%" 2>&1
echo === FIN (codigo %errorlevel%) === >> "%LOG%"
echo.
echo Listo. Ya puedes decirle a Claude "listo".
pause
