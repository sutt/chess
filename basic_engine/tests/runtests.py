'''
    This runs some or all the tests in the workspace

    >[start] python runtests.py [--hang]

        --2             - run with python2, pytest2 (default right now)
        --3             - run with python3, pytest3

        --all
        --src           - only src/ ; exlcudes StockfishNetwork.py
        --src-all       - includes StockfishNetwork.py and unittests
        --tools         - only tools/ 
        --batchverify   - only batchverify
        --stockfish     - run stockfishnetwork tests

        --vv            - verbosity vv
        --v             - verbosity v

        --clearcache   - clears pytest caches to run b/w win/wsl

        --hang          -use time.sleep to keep cmd window open
'''

import os
import subprocess
import argparse
import time
import copy
from pytest_utils import reset_pytest

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--2", action="store_true")
ap.add_argument("--3", action="store_true")
ap.add_argument("--v", action="store_true")
ap.add_argument("--vv", action="store_true")
ap.add_argument("--all", action="store_true")
ap.add_argument("--src", action="store_true")
ap.add_argument("--srcall", action="store_true")
ap.add_argument("--tools", action="store_true")
ap.add_argument("--batchverify", action="store_true")
ap.add_argument("--stockfish", action="store_true")
ap.add_argument("--clearcache", action="store_true")
ap.add_argument("--hang", action="store_true")
args = vars(ap.parse_args())


b_src               = False
b_tools             = False
b_batchverify       = False
b_stockfish         = False
b_linux             = False

if args["all"]:
    b_src           = True
    b_tools         = True
    b_batchverify   = True
    b_stockfish     = True

if args["src"]:
    b_src           = True
if args["srcall"]:
    b_src           = True
    b_stockfish     = True
if args["tools"]:
    b_tools         = True
if args["batchverify"]:
    b_batchverify   = True
if args["stockfish"]:
    b_stockfish     = True
if args["clearcache"]:
    print('clearing pytest caches: deleting __pycache__ folder and all .pyc in')
    print('src/ tools/ and tests/ ...')
    reset_pytest()

if os.name != "nt":
    b_stockfish     = False

if os.name == "posix":
    b_linux         = True

verbose_arg     = ""
if args["v"]:
    verbose_arg = "-v"
if args["vv"]:
    verbose_arg = "-vv"


pytest_cmd = ["python", "-m" , "pytest"]
if args["3"]:
    pytest_cmd = ["python3", "-m" , "pytest"]


if b_src:
    cmd =  copy.copy(pytest_cmd)
    cmd.extend([verbose_arg])
    print(cmd)
    p = subprocess.Popen(cmd, cwd="../src/")
    p.wait()

if b_linux and b_src:
    cmd =  copy.copy(pytest_cmd)
    cmd.extend(verbose_arg)
    p = subprocess.Popen(["pytest", verbose_arg, "StockfishCLApi.py"]
                            ,cwd = "../src/")
    p.wait()

if b_tools:
    p = subprocess.Popen(["pytest", verbose_arg], cwd="../tools/")
    p.wait()

if b_batchverify:
    
    p = subprocess.Popen(["pytest", verbose_arg, "batchverify.py"])
    p.wait()

if b_stockfish:
    
    verbose_arg_flag = "-" if verbose_arg == "" else verbose_arg

    if "test_tmp.txt" in os.listdir(os.getcwd()):
        os.remove("test_tmp.txt")

    p = subprocess.Popen( [  'run_pytest_file.bat'
                            ,'../src/StockfishNetwork.py'
                            ,verbose_arg_flag
                          ]
                          ,shell=True
                        )
    p.wait()

    #TODO - add stockfish_test.py unittest


print('done with runtests.')

if args["hang"]:
    print('..hanging for a long time...')
    time.sleep(999999)

