@echo off
set owner=TheBadNomads
set repo=TheBadHR
set filename=latest.zip
set outputDir=%CD%
set token=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

curl -H "Authorization: token %token%" https://api.github.com/repos/%owner%/%repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do (SET result=%%g)
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"
curl -H "Authorization: token %token%" -L -o %filename% https://github.com/%owner%/%repo%/archive/%tag_name%/%filename%
tar -xf %filename%
del /f %filename%
del /f response.txt
