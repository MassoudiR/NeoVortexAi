@echo off
:: -----------------------------
:: Setup virtual environment
:: -----------------------------
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Please create one.
)

:: Run FastAPI app
echo Starting FastAPI server...
uvicorn main:app --reload 

:: Pause to keep the window open
pause

uvicorn main:app --reload --host 0.0.0.0 --port 8000
fastapi dev main.py  