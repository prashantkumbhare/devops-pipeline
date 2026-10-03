@echo off
where git >nul 2>nul
if errorlevel 1 goto missing
where code >nul 2>nul
if errorlevel 1 goto missing
where docker >nul 2>nul
if errorlevel 1 goto missing
docker version
if errorlevel 1 exit /b 1
docker compose version
if errorlevel 1 exit /b 1
if /I "%~1"=="--smoke-test" (
    docker run --rm hello-world
    if errorlevel 1 exit /b 1
)
echo Environment checks passed.
exit /b 0
:missing
echo Missing Git, VS Code or Docker on PATH. Open a fresh terminal after installation.
exit /b 1

