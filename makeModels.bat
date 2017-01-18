%"%@echo off%"% 
%"%if "%1" == "" (%"% 
%"%set /p target="Enter name of app to make models for:"%"% 
%"%) else (%"% 
%"%set app=%1%"% 
%"%)%"% 
%"%%"% 
%"%cd apps/%target%%"% 
%"%if %errorlevel%==1 goto error%"% 
%"%%"% 
%"%choice.exe /M "Before we start making models, would you like to import any models from another app?"%"% 
%"%if %errorlevel%==2 goto startmodel%"% 
%"%%"% 
:importmodelfile 
%"%set /p app="Enter name of app to import:"%"% 
%"%%"% 
:importmodelfromfile 
%"%set model=%"% 
%"%set name=%"% 
%"%set /p model="Enter name of model to import from %app%, or blank to end importing from this file:"%"% 
%"%if "%model%"=="" goto endimport%"% 
%"%set /p name="Enter name to import the model as, or blank to keep original name:"%"% 
%"%if "%name%"=="" (%"% 
%"%  grep -rl 'from django.db import models' ./ | xargs sed -i 's/from django.db import models/\0\nfrom ..%app%.models import %model%/g'%"% 
%"%) else (%"% 
%"%  grep -rl 'from django.db import models' ./ | xargs sed -i 's/from django.db import models/\0\nfrom ..%app%.models import %model% as %name%/g'%"% 
%"%)%"% 
%"%goto importmodelfromfile%"% 
%"%%"% 
:endimport 
%"%choice.exe /M "Would you like to import any models from another app?"%"% 
%"%if %errorlevel%==1 goto importmodelfile%"% 
%"%%"% 
:startmodel 
%"%echo Would you like to create a new model or a model that extends another model?%"% 
%"%echo 1: New Model%"% 
%"%echo 2: Extend Existing Model%"% 
%"%choice.exe /C 12 /N /M "Enter your choice:"%"% 
%"%%"% 
%"%if %errorlevel% == 2 goto extendmodel%"% 
%"%%"% 
:newmodel 
%"%set unique=off%"% 
%"%set /p model="Enter Model Name: "%"% 
echo class %model%(models.Model): >> models.py 
%"%goto :newfield%"% 
:extendmodel 
%"%set unique=off%"% 
%"%set /p model="Enter Model Name: "%"% 
%"%set /p extends="Enter Model to Extend"%"% 
echo class %model%(%extends%): >> models.py 
:newfield 
%"%echo What type of field should be added?%"% 
%"%echo 1: Character Field%"% 
%"%echo 2: Text Field%"% 
%"%echo 3: Integer Field%"% 
%"%echo 4: Decimal Field%"% 
%"%echo 5: Float Field%"% 
%"%echo 6: Date/Time Field%"% 
%"%echo 7: One to One Field%"% 
%"%echo 8: Many to One Field%"% 
%"%echo 9: Many to Many Field%"% 
%"%echo U: Toggle Uniqueness Constraint (currently %unique%) (Note: Ignored for foreign-key fields)%"% 
%"%echo E: End Model%"% 
%"%choice.exe /c 123456789UE /N /M "Enter your choice:"%"% 
%"%%"% 
%"%set type=%errorlevel%%"% 
%"%%"% 
%"%if %type% == 10 goto toggleunique%"% 
%"%if %type% == 11 goto endmodel%"% 
%"%%"% 
%"%set /p field="Enter Field Name: "%"% 
%"%%"% 
%field% = models.%"%grep -rl '%field%' ./ | xargs sed -i 's/%field%/    \0/g'%"% 
%"%%"% 
%"%if %type% == 1 goto char%"% 
%"%if %type% == 2 goto text%"% 
%"%if %type% == 3 goto int%"% 
%"%if %type% == 4 goto dec%"% 
%"%if %type% == 5 goto float%"% 
%"%if %type% == 6 goto date%"% 
%"%if %type% == 7 goto onetoone%"% 
%"%if %type% == 8 goto manytoone%"% 
%"%if %type% == 9 goto manytomany%"% 
%"%%"% 
:char 
CharField(%"%goto len%"% 
:text 
TextField(%"%goto len%"% 
:int 
IntegerField(%"%goto unique%"% 
:dec 
DecimalField(%"%goto declen%"% 
:float 
FloatField(%"%goto unique%"% 
:date 
DateTimeField(%"%goto unique%"% 
:onetoone 
OneToOneField(%"%goto foreignfield%"% 
:manytoone 
ForeignKey(%"%goto foreignfield%"% 
:manytomany 
ManyToManyField(%"%goto foreignfield%"% 
%"%%"% 
:len 
%"%set /p length="Enter Max Length: "%"% 
max_length = %length%, %"%goto unique%"% 
%"%%"% 
:declen 
%"%set /p digits="Enter Max Digits: "%"% 
%"%set /p decimals="Enter Number of Decimals: "%"% 
max_digits = %digits%, decimal_places = %decimals%, %"%goto unique%"% 
%"%%"% 
:unique 
%"%if "%unique%" == "on" (%"% 
  echo unique=True) >> models.py 
%"%) else (%"% 
  echo unique=False) >> models.py 
%"%)%"% 
%"%goto endfield%"% 
%"%%"% 
:foreignfield 
%"%set /p table="Enter Foreign Table: "%"% 
echo %table%) >> models.py 
%"%%"% 
:endfield 
%"%echo Field Added!%"% 
%"%goto newfield%"% 
%"%%"% 
:toggleunique 
%"%if "%unique%" == "on" (%"% 
%"%  set unique=off%"% 
%"%) else (%"% 
%"%  set unique=on%"% 
%"%)%"% 
%"%goto newfield%"% 
%"%%"% 
:endmodel 
%"%echo Would you like to create another model?%"% 
%"%choice.exe%"% 
%"%if %errorlevel%==1 goto startmodel%"% 
%"%%"% 
%"%cd ../..%"% 
%"%goto end%"% 
%"%%"% 
:error 
%"%echo App not found%"% 
%"%cd ..%"% 
%"%%"% 
:end 
