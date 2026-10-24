@echo off
echo ========================================================
echo Pushing Northstar Deletion Audit Agent to GitHub...
echo Target: https://github.com/bhuvibagrecha23-ai/hackerrank.git
echo ========================================================
echo.

cd /d "C:\Users\bhuvi\.gemini\antigravity\scratch\hackerrank-orchestrate-october26"
set "PATH=C:\Users\bhuvi\.gemini\antigravity\tools\mingit\cmd;C:\Users\bhuvi\.gemini\antigravity\tools\mingit\ucrt64\bin;%PATH%"

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo SUCCESS! Repository successfully pushed to GitHub:
    echo https://github.com/bhuvibagrecha23-ai/hackerrank
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo PUSH FAILED. Please review the error message above.
    echo ========================================================
)
echo.
pause
