@echo off
set owner=TheBadNomads
set repo=TheBadHR
set filename=latest.zip
set outputDir=%CD%

FOR /F "tokens=*" %%t IN ('FIND "Personal_Access_Token" ".env"') do (SET token_result=%%t)
set "token=%token_result:~24%"
echo %token%

curl -H "Authorization: token %token%" https://api.github.com/repos/%owner%/%repo%/releases/latest > response.txt
FOR /F "tokens=*" %%g IN ('FIND "tag_name" "response.txt"') do (SET result=%%g)
set "tag_name=%result:"tag_name": "=%"
set "tag_name=%tag_name:",=%"

curl -H "Authorization: token %token%" -L -o %filename% https://github.com/%owner%/%repo%/archive/%tag_name%/%filename%
"C:\Program Files\7-Zip\7z.exe" e %filename% -o%outputDir% -y
del /f %filename%
del /f response.txt
