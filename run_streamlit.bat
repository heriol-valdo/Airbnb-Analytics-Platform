@echo off
echo.
echo ======================================
echo  Airbnb Analytics - Streamlit App
echo ======================================
echo.

cd /d "%~dp0"

echo Verifying dbt models...
cd airbnb_analytics
dbt run > nul 2>&1
cd ..

echo.
echo Starting Streamlit application...
echo Opening http://localhost:8501 in your browser...
echo.
echo Press Ctrl+C to stop the application.
echo.

streamlit run streamlit_app.py

pause
