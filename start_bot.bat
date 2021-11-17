@echo off
set Owner=AbdoHamed-TheBadNomads
set Repo=Abdo_Test_Repo_public
set filename=Abdo.zip
set OutputDir=%CD%

curl https://api.github.com/repos/%Owner%/%Repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do (SET result=%%g)
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"
curl -L -o %filename% https://github.com/%Owner%/%Repo%/archive/%tag_name%/%filename%
"C:\Program Files\7-Zip\7z.exe" e %filename% -o%OutputDir% -y
del /f %filename%
del /f response.txt
