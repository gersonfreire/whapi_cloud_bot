
@REM cd C:\Users\Administrator\repos\crypto_zap\zaptwillio\
@REM call .venv\Scripts\Activate

@REM cd C:\Users\Administrator\repos\crypto_zap\zaptwillio\whapi_cloud_bot\
@REM python crypto_webhook.py


@REM This script is used to run the bot in the Windows environment

@REM Go to current directory
cd %~dp0\..

@REM Activate the virtual environment and run the bot
call .venv\Scripts\Activate

@REM set python script name to the first argument
@REM set SCRIPT_NAME=%1

@REM Get the script name without the extension
@REM for %%F in ("%~f0") do set SCRIPT_NAME=%%~nF
set SCRIPT_NAME=crypto_webhook

@REM Run the bot script repassing the arguments
python whapi_cloud_bot\%SCRIPT_NAME%.py  %*
