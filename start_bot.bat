@echo off
set Owner=TheBadNomads
set Repo=TheBadHR
set filename=latest.zip
set OutputDir=%CD%

curl -H "Authorization: token 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" https://api.github.com/repos/%Owner%/%Repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do (SET result=%%g)
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"
curl -H "Authorization: token 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" -L -o %filename% https://github.com/%Owner%/%Repo%/archive/%tag_name%/%filename%
"C:\Program Files\7-Zip\7z.exe" e %filename% -o%OutputDir% -y
del /f %filename%
del /f response.txt
