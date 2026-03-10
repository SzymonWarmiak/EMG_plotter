@echo off
echo Trwa instalacja bibliotek potrzebnych do programu EKG...
pip install -r src\requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Wystapil blad. Upewnij sie, ze Python jest zainstalowany i dodany do zmiennej PATH.
) else (
    echo.
    echo Gotowe! Wszystkie biblioteki zostaly zainstalowane.
)
pause