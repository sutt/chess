Chess
=======

From scratch chess engine & wsl+flask server pattern & profiling tools to examine perf-bottlenecks.

Experimental feature: Using WSL + Flask to integrate a linux-binary-cli-app into a windows-base app:
    
- the rules/display/interface-engine ("basic_engine/") can
be run on windows, while...

- the ai-engine ("stockfish/") is run in a separate process on a  server in wsl. Call/response over http communicates between processes, and python-subprocess interfaces of stdin/stdout with the stockfish-app.

This allows compuatational type workspaces to uses packages which only build easily for linux.

Code and Tests runs on python2.7 / python3.6+, and on windows and linux (wsl). This is handled with several switch statements (sys.version_info.major / os.name) where neccessary. Default as of March 2019 is Python3.6 on Win10.


Commands:

Playing...

    in basic_engine/

        >python[3] main.py

            runs interactive cli-game

        --1v1      - to control other player as well
        --myplayer <black, white>
        --network  - use the experimental wsl-server feature


Testing...

    in basic_engine/tests/

        [>wsl]

            use this if you want to enter wsl to run tests

        >python[3] runtests.py --all --3 [--2] [--vv] [--clearcache]

            --2:        use python2 
            --all:      run all types of tests
            --vv:       print each test name to stdout
            --clearcache run when alternating b/w wsl-vs-win32

    in stockfish/py_stockfish/

        >python3 -m tests.tests


Utilities / Perf Testing ...

    in ~basic_engine/tools/
    
        >python profile_test.py --classiccomparison

            profile_test reports function calls per experiment, from cProfile

    in ~/basic_engine/
    
        > python -m tools.perf_test --demo

        perf_test reports the elapsed time for the same game to run, under different different check-algo paths. Should take ~20 secs to complete for --demo.

    see docs/cmds-list.txt for more options