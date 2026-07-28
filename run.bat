@echo off
cd /d "%~dp0"

echo ===================================================
echo   App Launcher (Windows)
echo ===================================================
echo.

:: 1. Auto-detect and fix 'uv' command path
where uv >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    if exist "%LOCALAPPDATA%\bin\uv.exe" set "PATH=%LOCALAPPDATA%\bin;%PATH%"
)

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Package manager 'uv' not found in PATH.
    echo Please install uv or add it to PATH.
    echo.
    pause
    exit /b 1
)

:: 2. Auto-detect Python entry point
set "ENTRY_POINT="
if exist "main.py" set "ENTRY_POINT=main.py"
if not defined ENTRY_POINT if exist "simple_notepad.py" set "ENTRY_POINT=simple_notepad.py"
if not defined ENTRY_POINT if exist "app.py" set "ENTRY_POINT=app.py"
if not defined ENTRY_POINT if exist "src\app.py" set "ENTRY_POINT=src\app.py"

if not defined ENTRY_POINT (
    echo [ERROR] Python entry point not found.
    echo.
    pause
    exit /b 1
)

echo [INFO] Entry point found: %ENTRY_POINT%

:: 3. Auto-create .venv and sync package dependencies
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    uv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo.
        pause
        exit /b 1
    )
)

if exist "pyproject.toml" (
    echo [INFO] Syncing dependencies...
    uv sync
    if %errorlevel% neq 0 (
        echo [ERROR] uv sync failed.
        echo.
        pause
        exit /b 1
    )
)

:: 4. Launch Python app
echo.
echo [INFO] Launching %ENTRY_POINT%...
echo.

uv run pythonw "%ENTRY_POINT%"

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Application exited with error code %errorlevel%.
)

echo.
pause
