%"%@echo off%"% 
%"%if "%1" == "" (%"% 
%"%set /p app="Enter App Name: "%"% 
%"%) else (%"% 
%"%set app=%1%"% 
%"%)%"% 
%"%%"% 
%"%%"% 
%"%pushd apps%"% 
%"%echo Making app...%"% 
%"%..\manage.py startapp %app%%"% 
%"%if not %errorlevel% == 0 goto cleanup%"% 
%"%cd ..\stocks%"% 
%"%echo Performing first-time config for app...%"% 
%"%grep -rl 'INSTALLED_APPS = \[' ./ | xargs sed -i 's/INSTALLED_APPS = \[/\0\n    \'apps.%app%\',/g'%"% 
%"%grep -rl 'urlpatterns = \[' ./ | xargs sed -i 's_urlpatterns = \[_\0\nurl(r\'^%app%/\', include(\'apps.%app%.urls\')),_g'%"% 
%"%%"% 
%"%cd ..\apps\%app%%"% 
echo from django.conf.urls import url > urls.py 
echo from . import views >> urls.py 
echo urlpatterns = [ >> urls.py 
echo url(r'^$', views.index) >> urls.py 
echo ] >> urls.py 
%"%%"% 
echo from django.shortcuts import render, redirect >> views.py 
echo from django.contrib import messages >> views.py 
echo.>>views.py 
echo from models import * >> views.py 
echo.>>views.py 
echo # Create your views here. >> views.py 
echo def index(response): >> views.py 
echo     return render(response, "%app%/index.html") >> views.py 
%"%%"% 
%"%mkdir templates%"% 
%"%cd templates%"% 
%"%mkdir %app%%"% 
cd .. 
mkdir static 
cd static 
mkdir users 
cd users 
mkdir js 
mkdir css 
%"%popd%"% 
%"%%"% 
%"%choice.exe /M "Would you like to make models for this app now?"%"% 
%"%if %errorlevel%==2 goto eof%"% 
%"%../makeModels.bat %app%%"% 
%"%goto eof%"% 
:cleanup 
%"%popd%"% 
%"%%"% 
:eof 
