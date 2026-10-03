@echo off
echo ========================================
echo   Building Kent.exe
echo ========================================
echo.

:: Activate venv if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

echo Installing / updating packages...
py -m pip install -r requirements.txt
py -m pip install pyinstaller

echo.
echo Building executable (this may take a few minutes)...
py -m PyInstaller --noconfirm --clean --windowed --name "Kent" ^
  --add-data ".env.example;." ^
  --hidden-import=pynput.mouse._win32 ^
  --hidden-import=pynput.keyboard._win32 ^
  --hidden-import=speech_recognition ^
  --hidden-import=google.genai ^
  --hidden-import=google.genai.types ^
  --collect-all=PySide6 ^
  --collect-all=speech_recognition ^
  main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo BUILD FAILED
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Your executable is here:
echo   dist\Kent\Kent.exe
echo.
echo IMPORTANT:
echo   1. Copy your .env file into the dist\Kent\ folder
echo   2. Or rename .env.example to .env and add your Gemini key
echo.
pause
