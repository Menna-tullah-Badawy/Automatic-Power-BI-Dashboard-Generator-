@echo off
echo ==============================================================
echo Automatic Power BI Dashboard Generator
echo ==============================================================
echo.
echo Available themes:
echo   [1] FitPro_Red_Sports
echo   [2] Wallet_Teal
echo   [3] Dark_Analytics_Purple
echo   [4] Trading_Neon_Green
echo   [5] Luxury_Gold
echo   [6] Rexora_Light_Green
echo   [7] Control_Dark_Blue
echo.
set /p theme=Enter theme number (1-7): 
set /p file=Enter data file path (example: sales_data.xlsx): 
python auto_powerbi_generator.py %theme% %file%
pause
