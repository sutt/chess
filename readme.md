Chess
=======

From scratch chess engine & wsl+flask server pattern & profiling tools to examine perf-bottlenecks.

Using WSL + Flask to integrate a linux-binary-cli-app into a windows-base app:
    
    - the rules/display/interface-engine ("basic_engine/") can
    be run on windows, while
    - the ai-engine ("stockfish/") is run in a server on wsl

    this allows compuatational type workspaces to uses packages
    which only build easily for linux


Commands:

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

Playing...

    in basic_engine/

        >python[3] main.py

            runs interactive cli-game

            edit main.py code to change the type of game

            TODO - add cli args / input()-configuration instead of editing code


Utilities... (deprecated)

    [from basic_engine/]
    add pgn_to_xpgn() plus args to src/hack.py
    >python hack.py
    (this runs the conversion routine in the data/ directory)