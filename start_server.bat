@echo off
echo Starting Marshalats Backend Server...
echo.
python -c "import uvicorn; from server import app; uvicorn.run(app, host='0.0.0.0', port=8003, log_level='info')"
pause
