import os
import subprocess

# class MyClass:
#     @staticmethod

def foo():
    print(os.name)
    print(os.getcwd())

    subprocess.Popen(['c:/windows/sysnative/bash.exe'
                        ,'-c'
                        ,"export"
                        ,"FLASK_APP=serverA.py"
                        ,"&&"
                        ,"source"
                        , "~/.profile"
                        ,"&&"
                        ,"printenv"
                        ,"&&"
                        ,"flask"
                        ,"run"
                        ])
