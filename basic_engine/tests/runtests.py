'''
    This runs some or all the tests in the workspace

    >start python runtests.py 

        --all
        --src           - only src/ ; exlcudes StockfishNetwork.py
        --src-all       - includes StockfishNetwork.py and unittests
        --tools         - only tools/ 
        --batchverify   - only batchverify
        --stockfish     - run stockfishnetwork tests

        --vv            - verbosity vv
        --v             - verbosity v

        --clear-cache   - clears pytest caches to run b/w win/wsl

        --disregard-err - dont use .bat to eliminate pytest cp encoding err
'''

import os
import subprocess
import argparse

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--v", action="store_true")
ap.add_argument("--vv", action="store_true")
ap.add_argument("--all", action="store_true")
ap.add_argument("--src", action="store_true")
ap.add_argument("--srcall", action="store_true")
ap.add_argument("--tools", action="store_true")
ap.add_argument("--batchverify", action="store_true")
ap.add_argument("--stockfish", action="store_true")
ap.add_argument("--clearcache", action="store_true")
args = vars(ap.parse_args())


b_src               = False
b_tools             = False
b_batchverify       = False
b_stockfish         = False

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
    raise Exception("Not Implemented Yet")
    #TODO - add clear cache
    #TODO - add clear .pyc

verbose_arg     = ""
if args["v"]:
    verbose_arg = "-v"
if args["vv"]:
    verbose_arg = "-vv"


if b_src:
    p = subprocess.Popen(["pytest", verbose_arg], cwd="../src/")
    p.wait()

if b_tools:
    p = subprocess.Popen(["pytest", verbose_arg], cwd="../tools/")
    p.wait()

if b_batchverify:
    p = subprocess.Popen(["pytest", verbose_arg, "batchverify.py"])
    p.wait()

if b_stockfish:
    
    verbose_arg_flag = "-" if verbose_arg == "" else verbose_arg

    p = subprocess.Popen( [  'run_pytest_file.bat'
                            ,'../src/StockfishNetwork.py'
                            ,verbose_arg_flag
                          ]
                          ,shell=True
                        )
    p.wait()

    #TODO - add stockfish_test.py unittest


print 'done with runtests.'

