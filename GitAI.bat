@echo off
REM Check if the argument %1 is provided

REM SAVE CUR DIR
set CURDIR=%CD%

IF "%~1"=="" (
    echo Setting description to Updt
    echo.
    set Desc=Updt
) ELSE (
  set Desc=%1
)


 cd D:\Agent
 set GIT_TRACE=1
 echo TO FORCE A RE-READING OF THE .gitignore list uncomment the next line
 rem git rm -r --cached .
 git add -A
 REM git branch -M main
 git commit -m "%Desc%"
 REM COMMENTED OUT CODE FORCES A PUSH
 REM It loses track of remote updates
 REM git push origin main --force
 git push origin main
 if errorlevel 1 (
    echo.
    echo PUSH FAILED.
    pause
    exit /b
 )
 REM echo sem nada mostra o echo status
 echo.
 echo.
 echo VIEWS IF BATCH SUCCEEDED 
 echo.
 REM USING "git log -n 1" IS NOT TOO USEFUL
 git log -1 --name-status 
 echo.
 echo.
 echo VIEWS STATUS
 echo.
 git status
 cd %CURDIR%
 echo.
 

