@echo off
FOR /f "tokens=1,2 delims== " %%G in ('FIND "Batch_Repo_Owner" ".env"') do set owner=%%H
FOR /f "tokens=1,2 delims== " %%G in ('FIND "Batch_Repo" ".env"') do set repo=%%H
FOR /f "tokens=1,2 delims== " %%G in ('FIND "Batch_File_Name" ".env"') do set filename=%%H
FOR /f "tokens=1,2 delims== " %%G in ('FIND "Batch_Output_Dir" ".env"') do set outputDir=%%H

curl https://api.github.com/repos/%Owner%/%Repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do set result=%%g
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"

curl -L -o %filename% https://github.com/%Owner%/%Repo%/archive/%tag_name%/%filename%
mkdir %OutputDir%
tar -zxvf %filename% -C %OutputDir%
for /D %%x in (%OutputDir%\*) do set newOutDir=%%x
Xcopy "%newOutDir%" "%CD%" /E /H /C /Y
del /f %filename%
del /f response.txt
rmdir /s /q %OutputDir%

py -3 main.py