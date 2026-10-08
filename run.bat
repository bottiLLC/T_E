@echo off
setlocal

:: 0. Silent Launch Delegation (Suppresses Terminal Console Window)
if "%~1"=="--silent" goto :RUN_PAYLOAD
if "%~1"=="--console" goto :RUN_PAYLOAD

if exist "%~dp0run.vbs" (
    wscript.exe //nologo "%~dp0run.vbs"
    exit /b 0
)

powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Process cmd.exe -ArgumentList '/c `\"%~f0`\" --silent' -WindowStyle Hidden"
exit /b 0

:RUN_PAYLOAD
set "IS_SILENT="
if "%~1"=="--silent" set "IS_SILENT=1"

set "PROJ_ROOT=%~dp0"
cd /d "%PROJ_ROOT%"

if not defined IS_SILENT (
    echo ===================================================
    echo   App Launcher (Windows / Python-only Environment)
    echo ===================================================
    echo.
)

:: 1. Force uv to use local system Python (disable downloading Python binaries)
set "UV_PYTHON_PREFERENCE=only-system"

:: 2. Auto-detect existing uv in standard locations
where uv >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    if exist "%LOCALAPPDATA%\bin\uv.exe" set "PATH=%LOCALAPPDATA%\bin;%PATH%"
    if exist "%USERPROFILE%\.local\bin\uv.exe" set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    if exist "%APPDATA%\Python\Scripts\uv.exe" set "PATH=%APPDATA%\Python\Scripts;%PATH%"
)

:: 3. Bootstrap 'uv' via Python pip if missing
where uv >nul 2>&1
if %errorlevel% neq 0 (
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        if defined IS_SILENT (
            mshta "vbscript:MsgBox(\"Python is not installed or not in PATH.\",16,\"T_E Error\")(window.close)"
        ) else (
            echo [ERROR] Python is not installed or not in PATH.
            pause
        )
        exit /b 1
    )
    if not defined IS_SILENT echo [INFO] 'uv' package manager not found. Bootstrapping via pip...
    python -m pip install --upgrade pip >nul 2>&1
    python -m pip install uv >nul 2>&1
    if %errorlevel% neq 0 (
        if defined IS_SILENT (
            mshta "vbscript:MsgBox(\"Failed to install 'uv'.\",16,\"T_E Error\")(window.close)"
        ) else (
            echo [ERROR] Failed to install 'uv'.
            pause
        )
        exit /b 1
    )
)

:: 4. Auto-detect Python entry point with multi-tier path resolution
set "ENTRY_POINT="

:: Check 1: In batch directory (%PROJ_ROOT%)
if exist "%PROJ_ROOT%app.py" set "ENTRY_POINT=app.py"
if not defined ENTRY_POINT if exist "%PROJ_ROOT%main.py" set "ENTRY_POINT=main.py"
if not defined ENTRY_POINT if exist "%PROJ_ROOT%src\app.py" set "ENTRY_POINT=src\app.py"

:: Check 2: In current working directory (%CD%)
if not defined ENTRY_POINT if exist "%CD%\app.py" (
    set "PROJ_ROOT=%CD%\"
    set "ENTRY_POINT=app.py"
)
if not defined ENTRY_POINT if exist "%CD%\main.py" (
    set "PROJ_ROOT=%CD%\"
    set "ENTRY_POINT=main.py"
)
if not defined ENTRY_POINT if exist "%CD%\src\app.py" (
    set "PROJ_ROOT=%CD%\"
    set "ENTRY_POINT=src\app.py"
)

:: Check 3: In parent directory (if run.bat was moved into a subfolder)
if not defined ENTRY_POINT if exist "%PROJ_ROOT%..\app.py" (
    cd /d "%PROJ_ROOT%.."
    set "PROJ_ROOT=%CD%\"
    set "ENTRY_POINT=app.py"
)

if not defined ENTRY_POINT (
    if defined IS_SILENT (
        mshta "vbscript:MsgBox(\"Python entry point [main.py] not found.\",16,\"T_E Error\")(window.close)"
    ) else (
        echo [ERROR] Python entry point [main.py] not found.
        pause
    )
    exit /b 1
)

cd /d "%PROJ_ROOT%"

:: 5. Auto-create .venv and sync package dependencies
if not exist ".venv" (
    if not defined IS_SILENT echo [INFO] Creating virtual environment...
    uv venv --python python >nul 2>&1
    if %errorlevel% neq 0 (
        if defined IS_SILENT (
            mshta "vbscript:MsgBox(\"Failed to create virtual environment .venv.\",16,\"T_E Error\")(window.close)"
        ) else (
            echo [ERROR] Failed to create virtual environment .venv.
            pause
        )
        exit /b %errorlevel%
    )
)

if exist "pyproject.toml" (
    if not defined IS_SILENT echo [INFO] Syncing dependencies...
    uv sync >nul 2>&1
    if %errorlevel% neq 0 (
        if defined IS_SILENT (
            mshta "vbscript:MsgBox(\"Dependency sync [uv sync] failed.\",16,\"T_E Error\")(window.close)"
        ) else (
            echo [ERROR] Dependency sync [uv sync] failed.
            pause
        )
        exit /b %errorlevel%
    )
)

:: 6. Launch Application (silent execution without console window)
findstr /i "streamlit" pyproject.toml >nul 2>&1
if %errorlevel% equ 0 (
    uv run streamlit run "%ENTRY_POINT%" --server.headless false
) else (
    if defined IS_SILENT (
        uv run pythonw "%ENTRY_POINT%"
    ) else (
        uv run python "%ENTRY_POINT%"
    )
)

if not defined IS_SILENT (
    echo.
    pause
)
