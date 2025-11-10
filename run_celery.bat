@echo off
echo Starting Celery Worker...
echo.
celery -A config worker -l info
pause