'''
    This runs some or all the tests in the workspace

    >python runtests.py 

        --all
        --src           - only src/ ; exlcudes StockfishNetwork.py
        --src-all       - includes StockfishNetwork.py and unittests
        --tools         - only tools/ 

        --vv            - verbosity vv
        --v             - verbosity v

        --clear-cache   - clears pytest caches to run b/w win/wsl

        --disregard-err - dont use .bat to eliminate
'''

import os
import subprocess
#TODO - argparse
#TODO - add clear cache

#Note the single quotes enclosing double quotes

#This ignores the error, so run stockfish tests last

if True:
    p = subprocess.Popen("pytest", cwd="../src/")
    p.wait()
    p = subprocess.Popen("pytest", cwd="../tools/")
    p.wait()

#This is for dealing wtih stockfish tests

if False:

    p = subprocess.Popen( ['../tests/run_pytest_file.bat'  
                            ,'"-"'
                            ,'"-"'
                        ]
                        ,cwd = "../src/")
    p.wait()

    p = subprocess.Popen( [  'run_pytest_file.bat'
                            ,'"../src/StockfishNetwork.py"'
                            ,'"-"'
                        ]
                        )
    p.wait()


    p = subprocess.Popen( ['"../tests/run_pytest_file.bat"'  
                            ,'"-"'
                            ,'"-"'
                        ]
                        ,cwd = "../tools/")
    p.wait()

#TODO - add stockfish_test.py unittest

print 'done.'

