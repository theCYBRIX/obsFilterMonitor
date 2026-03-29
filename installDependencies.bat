@echo off

set /p "version=Enter the desired websockets version (Eg: 9.1), or press Enter: "

if not exist lib (
    @echo Creating lib folder...
    mkdir lib 2>nul

    if errorlevel 1 (
        @echo ERROR! Failed to create lib folder. You may need to run the script as administrator.
        pause
        exit /b 1
    )
)

echo Installing Dependencies...
if "%version%"=="" (
    echo Installing websockets ^(latest^)...
    pip install websockets -t ./lib
) else (
    echo Installing websockets==%version%...
    pip install websockets==%version% -t ./lib
)

cd lib

@echo Creating __init__.py...
type nul > __init__.py

if errorlevel 1 (
    @echo ERROR! Failed to create __init__.py. You may need to run the script as administrator.
    pause
    exit /b 1
)

@echo Finished!
pause
