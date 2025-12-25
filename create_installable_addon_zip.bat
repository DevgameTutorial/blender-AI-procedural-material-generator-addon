@echo off
REM ========================================
REM Blender AI Material Generator
REM Create Installable Addon ZIP
REM ========================================

echo.
echo ========================================
echo   AI Material Generator - Package Tool
echo   Create Installable Addon ZIP
echo ========================================
echo.

REM Configuration
set "ADDON_NAME=blender_ai_material_gen"
set "ZIP_NAME=%ADDON_NAME%.zip"
set "TEMP_DIR=%ADDON_NAME%_temp"

REM Cleanup old files
if exist "%TEMP_DIR%" (
    echo [CLEANUP] Removing old temporary files...
    rmdir /s /q "%TEMP_DIR%"
)

if exist "%ZIP_NAME%" (
    echo [CLEANUP] Deleting old package...
    del "%ZIP_NAME%"
)

echo.
echo [BUILD] Creating addon package structure...

REM Create directory structure
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\%ADDON_NAME%"

REM Copy all Python addon files
echo [COPY] Adding core files...
copy "__init__.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "operators.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "panels.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "ai_connector.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "material_generator.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "utils.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul

echo [COPY] Adding AI templates...
copy "prompt_templates.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "material_schema.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul

echo [COPY] Adding node reference...
copy "node_reference.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul
copy "material_references.py" "%TEMP_DIR%\%ADDON_NAME%\" >nul

echo [SUCCESS] All files copied!
echo.

REM Create zip archive using PowerShell
echo [PACKAGE] Compressing to ZIP archive...
powershell -command "Compress-Archive -Path '%TEMP_DIR%\%ADDON_NAME%' -DestinationPath '%ZIP_NAME%' -Force"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create ZIP package!
    echo Please make sure PowerShell is available.
    echo.
    pause
    exit /b 1
)

REM Cleanup temporary directory
echo [CLEANUP] Removing temporary files...
rmdir /s /q "%TEMP_DIR%"

echo.
echo ========================================
echo   PACKAGE CREATED SUCCESSFULLY!
echo ========================================
echo.
echo Output: %ZIP_NAME%
echo Size: 
dir "%ZIP_NAME%" | find "%ZIP_NAME%"
echo.
echo ----------------------------------------
echo   INSTALLATION INSTRUCTIONS
echo ----------------------------------------
echo.
echo 1. Open Blender
echo 2. Edit ^> Preferences ^> Add-ons
echo 3. Click "Install..." button
echo 4. Select file: %ZIP_NAME%
echo 5. Enable "Material: AI Procedural Material Generator"
echo 6. Enter your Gemini API key in Settings panel
echo.
echo ----------------------------------------
echo   IMPORTANT - DEPENDENCIES REQUIRED
echo ----------------------------------------
echo.
echo Before using the addon, you MUST install dependencies:
echo    ^> Double-click: install_dependencies.bat
echo.
echo This will install:
echo    - pydantic (schema validation)
echo    - google-genai (NEW Gemini SDK)
echo    - requests
echo.
pause
