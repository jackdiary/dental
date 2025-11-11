@echo off
echo Starting Django Backend Server...
echo.
echo Make sure PostgreSQL and Redis are running!
echo.
python manage.py runserver
pause