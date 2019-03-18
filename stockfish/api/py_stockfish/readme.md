This is repo for holding src/package-files for Ilya Zhelyabuzhsky 's "stockfish" pypi package in the stockfish/ directory. https://github.com/zhelyabuzhsky

The main code in stockfish.py is copied into lib_stockfish.py in the parent directory api/ and is used by serverA.py to communicate with the compiled executable in root/stockfish/Stockfish/bin/

In this directory, I've changed the structure to separate tests that come with the package ("test_stockfish.py") into it's own directory in py_stockfish/tests/tests.py. These tests help assert this wrapper package is correctly calling the main-engine-program, and that the main-engine program is giving answers as expected. These tests are not run as part of basic_engine/tests/runtests.py test-runner; must call them separately here.

To run these tests:

    >[wsl]           # enter wsl environment before testing; advised
    >python[3] -m tests.tests   

    this works on python3 but not python2:
    >python3 -m unittest tests/tests.py

    the tests should report a warning about an unclosed IO file, but still pass:

        /usr/lib/python3.5/subprocess.py:842: ResourceWarning: unclosed file <_io.TextIOWrapper name=4 encoding='UTF-8'>

The main idea of this module is to be able to run stockfish as a linux-app in a wsl environment while the main app (basic_engine/main.py) runs in win32. For these reason it's advised to run these tests in a wsl-environ shell (first type wsl, then enter into console), however the main-engine-program can be compiled to win32 so these tests can also be run in windows-environ.

Note all other modules+tests in this workspace use pytest, while this one uses unittest.

