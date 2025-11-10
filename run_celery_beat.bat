@echo off
echo Starting Celery Beat Scheduler...
echo.
celery -A config beat -l info
pause