@echo off
echo Building App Sticky Memo...

REM Code quality check
echo Running code quality checks...
uv run pre-commit run --all-files
if errorlevel 1 (
    echo Code quality checks failed!
    pause
    exit /b 1
)

echo Code quality checks passed!

REM Clean previous build
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using spec file
echo Building application using PyInstaller spec file...
uv run pyinstaller app_sticky_memo.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build completed successfully!
echo Executable created at: dist\App Sticky Memo.exe

REM Test if the executable exists
if exist "dist\App Sticky Memo.exe" (
    echo Build verification: OK
) else (
    echo Build verification: FAILED - Executable not found
    pause
    exit /b 1
)

echo.
echo To run the application:
echo "dist\App Sticky Memo.exe"
echo.
pause
