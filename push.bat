@echo off

set commit_message=%~1

if "%commit_message%"=="" (

    set /p commit_message="Enter commit message: "

)

echo MODE: %commit_message%

git add .

git commit -m "%commit_message%"

git push -f

pause