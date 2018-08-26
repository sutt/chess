::This runs pytest but eliminates the cp65001 encoding error in 
::python27\lib\site-packages\colorama\ansitowin32.py
ECHO 'here we go...'
pytest -vv StockfishNetwork.py > tmp.txt
type tmp.txt