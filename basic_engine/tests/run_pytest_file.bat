::This runs pytest but eliminates the cp65001 encoding error in 
::python27\lib\site-packages\colorama\ansitowin32.py

::Arg1:  - or "path/to/testfile.py"
::Arg2:  - or -v or -vv

::Examples: 
::[terse+specific run]
::  tests/ >run_pytest_file.bat ../src/StockfishNetwork.py -
::[verbose+specific run]
::  tests/ >run_pytest_file.bat ../src/StockfishNetwork.py -vv
::[verbose+directory run]
::  tests/ >run_pytest_file.bat - -vv
echo off

IF "%~1"=="-" (
    set arg1=""
) ELSE (
    set arg1=%1
)

IF "%~2"=="-" (
    set arg2=""
) ELSE (
    set arg2=%2
)

echo on

ECHO running: pytest %arg2% %arg1% > test_tmp.txt

pytest %arg2% %arg1% > test_tmp.txt

type test_tmp.txt