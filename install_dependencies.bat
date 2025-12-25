@echo off
echo ========================================
echo Blender AI Material Generator
echo Dependency Installer
echo ========================================
echo.
echo Mencari instalasi Blender...
echo.

REM Default installation paths
set "BASE_PATH_1=C:\Program Files\Blender Foundation"
set "BASE_PATH_2=C:\Program Files (x86)\Blender Foundation"

REM Try to find Blender installation - check each version
set "PYTHON_EXE="

REM Check Blender 6.0
if exist "%BASE_PATH_1%\Blender 6.0\6.0\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 6.0\6.0\python\bin\python.exe"
    echo [FOUND] Blender 6.0
    goto :found
)
if exist "%BASE_PATH_2%\Blender 6.0\6.0\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 6.0\6.0\python\bin\python.exe"
    echo [FOUND] Blender 6.0
    goto :found
)

REM Check Blender 5.1
if exist "%BASE_PATH_1%\Blender 5.1\5.1\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 5.1\5.1\python\bin\python.exe"
    echo [FOUND] Blender 5.1
    goto :found
)
if exist "%BASE_PATH_2%\Blender 5.1\5.1\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 5.1\5.1\python\bin\python.exe"
    echo [FOUND] Blender 5.1
    goto :found
)

REM Check Blender 5.0
if exist "%BASE_PATH_1%\Blender 5.0\5.0\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 5.0\5.0\python\bin\python.exe"
    echo [FOUND] Blender 5.0
    goto :found
)
if exist "%BASE_PATH_2%\Blender 5.0\5.0\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 5.0\5.0\python\bin\python.exe"
    echo [FOUND] Blender 5.0
    goto :found
)

REM Check Blender 4.3
if exist "%BASE_PATH_1%\Blender 4.3\4.3\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 4.3\4.3\python\bin\python.exe"
    echo [FOUND] Blender 4.3
    goto :found
)
if exist "%BASE_PATH_2%\Blender 4.3\4.3\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 4.3\4.3\python\bin\python.exe"
    echo [FOUND] Blender 4.3
    goto :found
)

REM Check Blender 4.2
if exist "%BASE_PATH_1%\Blender 4.2\4.2\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 4.2\4.2\python\bin\python.exe"
    echo [FOUND] Blender 4.2
    goto :found
)
if exist "%BASE_PATH_2%\Blender 4.2\4.2\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 4.2\4.2\python\bin\python.exe"
    echo [FOUND] Blender 4.2
    goto :found
)

REM Check Blender 4.1
if exist "%BASE_PATH_1%\Blender 4.1\4.1\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 4.1\4.1\python\bin\python.exe"
    echo [FOUND] Blender 4.1
    goto :found
)
if exist "%BASE_PATH_2%\Blender 4.1\4.1\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 4.1\4.1\python\bin\python.exe"
    echo [FOUND] Blender 4.1
    goto :found
)

REM Check Blender 4.0
if exist "%BASE_PATH_1%\Blender 4.0\4.0\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 4.0\4.0\python\bin\python.exe"
    echo [FOUND] Blender 4.0
    goto :found
)
if exist "%BASE_PATH_2%\Blender 4.0\4.0\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 4.0\4.0\python\bin\python.exe"
    echo [FOUND] Blender 4.0
    goto :found
)

REM Check Blender 3.6
if exist "%BASE_PATH_1%\Blender 3.6\3.6\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_1%\Blender 3.6\3.6\python\bin\python.exe"
    echo [FOUND] Blender 3.6
    goto :found
)
if exist "%BASE_PATH_2%\Blender 3.6\3.6\python\bin\python.exe" (
    set "PYTHON_EXE=%BASE_PATH_2%\Blender 3.6\3.6\python\bin\python.exe"
    echo [FOUND] Blender 3.6
    goto :found
)

REM If not found, ask user for manual path
echo.
echo [WARNING] Blender tidak ditemukan di path default.
echo.
echo Silakan masukkan path lengkap ke python.exe Blender Anda.
echo Contoh: C:\Program Files\Blender Foundation\Blender 4.0\4.0\python\bin\python.exe
echo.
echo Atau tekan CTRL+C untuk membatalkan.
echo.
set /p PYTHON_EXE="Path ke python.exe: "

REM Verify manual path
if not exist "%PYTHON_EXE%" (
    echo.
    echo [ERROR] File tidak ditemukan!
    echo Instalasi dibatalkan.
    echo.
    pause
    exit /b 1
)

:found
echo.
echo ========================================
echo Installing dependencies...
echo ========================================
echo.
echo Menggunakan: %PYTHON_EXE%
echo.

REM Upgrade pip first
echo [1/4] Upgrading pip...
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Pip upgrade gagal, melanjutkan...
)

echo.
echo [2/4] Installing pydantic...
"%PYTHON_EXE%" -m pip install pydantic
if errorlevel 1 (
    echo.
    echo [ERROR] Instalasi pydantic gagal!
    pause
    exit /b 1
)

echo.
echo [3/5] Uninstalling old google-generativeai (deprecated)...
"%PYTHON_EXE%" -m pip uninstall -y google-generativeai
if errorlevel 1 (
    echo [INFO] google-generativeai not found, skipping...
)

echo.
echo [4/5] Installing google-genai (new SDK)...
"%PYTHON_EXE%" -m pip install google-genai
if errorlevel 1 (
    echo.
    echo [ERROR] Instalasi google-genai gagal!
    pause
    exit /b 1
)

echo.
echo [5/5] Installing requests...
"%PYTHON_EXE%" -m pip install requests
if errorlevel 1 (
    echo.
    echo [ERROR] Instalasi requests gagal!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Dependencies berhasil diinstall:
echo   - pydantic (for schema validation)
echo   - google-genai (NEW Gemini SDK)
echo   - requests
echo.
echo IMPORTANT: Old google-generativeai has been removed!
echo Using latest google-genai SDK for Gemini 2.5 models.
echo.
echo Anda sekarang bisa enable addon di Blender:
echo 1. Buka Blender
echo 2. Edit ^> Preferences ^> Add-ons
echo 3. Klik Install, pilih __init__.py dari folder addon
echo 4. Enable checkbox addon
echo.
pause
