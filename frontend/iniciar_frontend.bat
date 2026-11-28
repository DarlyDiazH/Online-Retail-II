@echo off
chcp 65001 >nul
title Frontend - Online Retail II
cd /d "%~dp0"
where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js no esta instalado.
  echo Descargalo en https://nodejs.org  ^(boton LTS^), instalalo y vuelve a abrir este archivo.
  pause
  exit /b 1
)
if not exist "node_modules" (
  echo Instalando dependencias ^(solo la primera vez, 1-2 minutos^)...
  call npm install
  if errorlevel 1 (
    echo ERROR instalando dependencias.
    pause
    exit /b 1
  )
)
echo.
echo Abriendo la pagina en http://localhost:5173
echo Deja esta ventana abierta. Para detener: Ctrl+C
echo.
start "" http://localhost:5173
call npm run dev
pause
