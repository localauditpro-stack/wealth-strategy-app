@echo off
echo Starting Financial Advisor Lead Generator...
echo Ensure you have installed requirements via 'pip install -r requirements.txt' if not already done.
python -m streamlit run app.py
if %errorlevel% neq 0 (
    echo.
    echo Error encounted! Trying to install dependencies...
    pip install -r requirements.txt
    echo Retrying launch...
    python -m streamlit run app.py
)
pause
