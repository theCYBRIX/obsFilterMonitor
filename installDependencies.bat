@echo off

echo Installing Dependencies...
pip install websockets==9.1 -t ./lib

@echo Creating __init__.py
cd lib
type nul > __init__.py

@echo Finished!