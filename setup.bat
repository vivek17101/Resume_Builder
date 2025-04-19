@echo off
setlocal

:: Set the folder path where your project is located
set folder=D:\StreamLit

:: Change to the project folder (resume-enhancer)
cd /d %folder%\resume-enhancer

:: Display menu
echo 1. Create all files and setup (fresh setup)
echo 2. Install dependencies (without reinstalling)
echo 3. Activate virtual environment and run Streamlit app
echo 4. Clean up (remove generated files)
echo 5. Exit
set /p choice=Choose an option: 

:: Process choice
if "%choice%"=="1" goto create_all
if "%choice%"=="2" goto install_dependencies
if "%choice%"=="3" goto run_app
if "%choice%"=="4" goto cleanup
if "%choice%"=="5" exit

:: Option 1: Create all files and setup
:create_all
echo Creating all files and setting up the environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Running Streamlit app...
streamlit run app.py

pause
exit

:: Option 2: Install dependencies (without reinstalling)
:install_dependencies
if exist venv (
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo Virtual environment not found. Please run option 1 to create the environment.
)
pause
exit

:: Option 3: Activate virtual environment and run Streamlit app
:run_app
if exist venv (
    call venv\Scripts\activate.bat
    echo Running Streamlit app...
    streamlit run app.py
) else (
    echo Virtual environment not found. Please run option 1 to create the environment.
)
pause
exit

:: Option 4: Clean up (remove generated files)
:cleanup
echo Cleaning up generated files...
if exist venv (
    rmdir /s /q venv
    echo Removed virtual environment.
)
if exist requirements.txt (
    del requirements.txt
    echo Removed requirements.txt.
)
if exist app.py (
    del app.py
    echo Removed app.py.
)
if exist .env (
    del .env
    echo Removed .env file.
)
if exist run-resume-enhancer.bat (
    del run-resume-enhancer.bat
    echo Removed run-resume-enhancer.bat.
)

echo Cleanup complete.
pause
exit
