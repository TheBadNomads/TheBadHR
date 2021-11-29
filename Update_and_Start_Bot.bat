@echo off

set filename=latest.zip

FOR /f "tokens=1,2 delims== " %%G in ('FIND "Repo_Owner" ".env"') do set owner=%%H
FOR /f "tokens=1,2 delims== " %%G in ('FIND "Repo" ".env"') do set repo=%%H

curl https://api.github.com/repos/%Owner%/%Repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do set result=%%g
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"

curl -L -o %filename% https://github.com/%Owner%/%Repo%/archive/%tag_name%/%filename%
tar -zxvf %filename% -C "%CD%" --strip-components=1
del /f %filename%
del /f response.txt

py -3 main.py
