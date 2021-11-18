@echo off
set Owner=TheBadNomads
set Repo=TheBadHR
set filename=latest.zip
set outputDir="C:\bot_latest_tmp"
set currentDir=%CD%
set token=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

curl -H "Authorization: token %token%" https://api.github.com/repos/%Owner%/%Repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do set result=%%g
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"
curl -H "Authorization: token %token%" -L -o %filename% https://github.com/%Owner%/%Repo%/archive/%tag_name%/%filename%
mkdir %OutputDir%
tar -zxvf %filename% -C %OutputDir%
for /D %%x in (%OutputDir%\*) do set newOutDir=%%x
Xcopy %newOutDir% %currentDir% /E /H /C /I /Y
del /f %filename%
del /f response.txt
rmdir /s /q %OutputDir%

py -3 main.py
