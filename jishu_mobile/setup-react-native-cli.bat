@echo off
SETLOCAL EnableDelayedExpansion

echo ================================================
echo   Jishu Mobile - React Native CLI Setup
echo ================================================
echo.

REM Check if we're in the mobile directory
if not exist "package.json" (
    echo Error: Please run this script from the /mobile directory
    exit /b 1
)

REM Step 1: Check prerequisites
echo Step 1: Checking prerequisites...

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js 18+
    exit /b 1
)

echo Node.js detected
node -v

REM Step 2: Initialize React Native project
echo.
echo Step 2: Initializing React Native project...
echo This will create the ios/ and android/ native directories

set TEMP_DIR=JishuTemp

if exist "%TEMP_DIR%" (
    rmdir /s /q "%TEMP_DIR%"
)

echo Creating temporary React Native project...
call npx react-native init %TEMP_DIR% --version 0.73.6 --skip-install

REM Copy native directories if they don't exist
if not exist "android\app\src" (
    echo Copying Android files...
    xcopy /E /I /Y "%TEMP_DIR%\android" "android\"
    
    REM Update package name (basic replacement, manual editing may be needed)
    echo Please manually update package names in android/ to com.jishu.app
)

REM Clean up temp directory
if exist "%TEMP_DIR%" (
    rmdir /s /q "%TEMP_DIR%"
)

echo Native project structure created

REM Step 3: Install dependencies
echo.
echo Step 3: Installing dependencies...
call npm install

if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b 1
)

echo Dependencies installed

REM Step 4: Run migration script
echo.
echo Step 4: Migrating Expo imports to React Native CLI...

if exist "scripts\migrate-imports.js" (
    node scripts\migrate-imports.js
    echo Import migration complete
) else (
    echo Migration script not found, skipping...
)

REM Step 5: Configure Android
echo.
echo Step 5: Configuring Android...

findstr /C:"react-native-vector-icons" android\app\build.gradle >nul
if %errorlevel% neq 0 (
    echo. >> android\app\build.gradle
    echo apply from: "../../node_modules/react-native-vector-icons/fonts.gradle" >> android\app\build.gradle
    echo Added vector icons to Android build.gradle
) else (
    echo Vector icons already configured in Android
)

REM Summary
echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo   To run on Android:
echo   npm run android
echo.
echo   To start Metro bundler:
echo   npm start
echo.
echo Troubleshooting:
echo   - Clear cache: npm start -- --reset-cache
echo   - Clean build: npm run clean
echo.
echo Happy coding!
echo.

ENDLOCAL
