::This runs pytest but eliminates the cp65001 encoding error in 
::python27\lib\site-packages\colorama\ansitowin32.py
::Example: tests/ >run_pytest_file.bat ../src/StockfishNetwork.py
echo off
set arg1=%1
ECHO running: pytest -vv %arg1%
pytest -vv %arg1% > test_tmp.txt
echo on
type test_tmp.txt