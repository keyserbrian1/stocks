@echo off 
manage.py makemigrations 
if not %errorlevel% == 0 goto error 
manage.py migrate 
if not %errorlevel% == 0 goto error 
start manage.py runserver 
goto end 
:error 
pause 
:end 
