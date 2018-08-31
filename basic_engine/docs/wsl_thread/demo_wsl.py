import subprocess

'''
Paths to different shells:
    "C:\\Windows\\System32\\cmd.exe"
    "C:\\Program Files\\Git\\bin\\bash.exe",
    "C:\\WINDOWS\\Sysnative\\cmd.exe

subprocess.call(["wsl", "export FLASK_APP=serverA.py && flask run"])

What if I made a bash script in api directory for getting flask running?
You need to add it to your ~/.profile or ~/.bashrc file


THIS IS WHERE WE STAND 2PM, 8/24:
    There is something wrong with our syntax of subprocess.Popen args
    which means that we have to a cmd like 'printenv && ' ahead of what 
    we want to work...

        Still to investigate: all that other stuff actually works 
                              as long as we prepend?

THIS IS WHERE WE STAND NOON, 8/24:

We can run a flask launch from a "wsl 1-liner" 
    But we can't duplicate that in subprocess.
        Because 'export FLASK_APP' doesn't work appear to work

        FixA: find the syntax to make export command work in subprocess
        FixB: find another command that also works, like running .sh that sets path
        FixC: find another way to stat flask without env-var FLASK_APP getting set
        FixD: Use a Popen / communicate, "2-liner" approach to wsl
        FixE: put the FLASK_APP in .profile? / source a .custom_dot_file


FixC:
    
    Call the subprocess in the api/ directory, by naming flask-app as 'app.py'.
    This removes the need for FLASK_APP env-var
    
        We had reltive import path issues going from:
            chess/basic_engine/src/calling.py
            ->
            chess/stockfish/api/subproc.py  ->  server.py
    
        And we have issues of where os.getcwd() when app-stack is calling from src/
        
FixD:
    
    p = subprocess.Popen(["wsl"])
    p.communicate("export FLASK_APP=serverA.py", etc..)
    
    Won't communicate kill the server?

FixE:

    add FLASK_APP=[full/path/serverA.py]
    but this will make all wsl-logins run that server!?

    api/.custom:
        export FLASK_APP=serverA.py

    > wsl /bin/bash -c "printenv && source .custom && printenv"
    (shows env-set)

    Now try as a 1-liner ("works"):
                wsl /bin/bash -c "source .custom && source ~/.profile && flask run"


WHAT WEVE LEARNED

    The reason we need to source .profile is for bash to find flask application
    withing user's private bin (/home/user/.local/bin/flask)

    Use double quotes around multiple && cmd when calling from windows-cmd.
    Otherwise, the && is interpreted as for multi-windows-calls not multi-wsl-calls


we can launch a subprocess in that directory with app.py and get it to run
    (because the )
The problem with subprocess is it can't find the file / path to serverA.py??
NO...
The problem is the export statement isn't working in subprocess call
Solutions...
    source another file?
        test if export works in a bash script with printenv-bookends
        >it does.
        -> So now how do we run a script.sh in subprocess?
        -> verify this works as a substitute to the export statement in the wsl-1-liner

            NOPES:
            wsl /bin/bash -c "./demo.sh && source ~/.profile && flask run"
            wsl /bin/bash -c "source ~/.profile && ./demo.sh && flask run"

            THIS WORKS
            wsl /bin/bash -c "export FLASK_APP=serverA.py && source ~/.profile && flask run"
            wsl /bin/bash -c "source ~/.profile && export FLASK_APP=serverA.py && flask run"

            BREAKING IT
            (no source of profile)
            wsl /bin/bash -c "export FLASK_APP=serverA.py && flask run"

            wsl /bin/bash -c "export FLASK_APP=serverA.py && /home/user/.local/bin/flask run"
            

        could be that you don't need export/set in a script
            just PATH=/blah/blah/
            
Ideas:
 - set a symlink with ln?  (How does this help tho)


This was a problem until we sourced .profile:
    set PATH so it includes user's private bin directories
    PATH="$HOME/bin:$HOME/.local/bin:$PATH"
        use a set statement?



THIS WORKS FROM WINDOWS-CMD
wsl /bin/bash -c "export FLASK_APP=serverA.py && source ~/.profile && flask run"

THIS WORKS FROM SUBPROC
Note - how cmds and cmd-arg's are separated in the list, and &&'s get their own element in the list
Note also how its not one
subprocess.call(['c:/windows/sysnative/bash.exe','-c', "ls",  "&&",  "ls", "-l"])

c:/windows/sysnative/bash.exe
subprocess.call(['c:/windows/sysnative/bash.exe','-c', 'ls'])

subprocess.call(['wsl', 'bin/bash', '-c', '"export FLASK_APP=serverA.py && source ~/.profile && flask run"'])

p = subprocess.Popen(['c:/windows/sysnative/bash.exe', 'bin/bash', '-c', '"export FLASK_APP=serverA.py && source ~/.profile && flask run"'])
p = subprocess.Popen(['c:/windows/sysnative/bash.exe', '-c', '"export FLASK_APP=serverA.py && source ~/.profile && flask run"'])

replace "export" with "set" ?


use a app.py in directory...

https://stackoverflow.com/questions/39812882/python-subprocess-call-cannot-find-windows-bash-exe
import os
import platform
import subprocess

is32bit = (platform.architecture()[0] == '32bit')
system32 = os.path.join(os.environ['SystemRoot'], 
                        'SysNative' if is32bit else 'System32')
bash = os.path.join(system32, 'bash.exe')

subprocess.call(["wsl", "export", "FLASK_APP=../../stockfish/api/serverA.py"])


THIS WORKS with app.py in the directory
    -> therefore can remove the export FLASK_APP which apparently isnt working
But can it work outside the directory?
shell=True?
suppress stdout from interfering with Game:Display() ?
    -> or can send to a tmp txt file

'''

# subprocess.Popen(['c:/windows/sysnative/bash.exe'
#                     ,'-c'
#                     ,"export"
#                     ,"FLASK_APP=serverA.py"
#                     ,"&&"
#                     ,"source"
#                     , "~/.profile"
#                     ,"&&"
#                     ,"printenv"
#                     ,"&&"
#                     ,"flask"
#                     ,"run"
#                     ])

# subprocess.Popen(['c:/windows/sysnative/bash.exe'
#                     ,'-c'
#                     ,"source"
#                     ,"/mnt/c/Users/wsutt/Desktop/files/chess/stockfish/api/.custom"
#                     ,"&&"
#                     ,"source"
#                     , "~/.profile"
#                     ,"&&"
#                     ,"printenv"
#                     ,"&&"
#                     ,"flask"
#                     ,"run"
#                     ])

#THIS WORKS
subprocess.Popen(['c:/windows/sysnative/bash.exe'
                    ,'-c'
                    ,"printenv"
                    ,"&&"
                    ,"source"
                    , "~/.customprofile"
                    ,"&&"
                    ,"flask"
                    ,"run"
                    ])

#BUT THIS DOESNT ?!
# subprocess.Popen(['c:/windows/sysnative/bash.exe'
#                     ,'-c'
#                     ,"source"
#                     , "~/.customprofile"
#                     ,"&&"
#                     ,"flask"
#                     ,"run"
#                     ])

# subprocess.Popen(['c:/windows/sysnative/bash.exe'
#                     ,'-c'
#                     ,"printenv"
#                     ,"&&"
#                     ,"printenv"
#                     ])

# subprocess.Popen(['c:/windows/sysnative/bash.exe', 'python', 'serverA.py'])

# Depending on what you're doing, you also may want to symlink to binaries:
# cd /usr/bine


# export PATH=$PATH:$HOME/.local/bin
# echo $(printenv)
# echo $(which flask)
# echo $(which bash)
# echo $(ls /home/user/)
# echo $(ls /home/user/.local/)
# echo $(ls /home/user/.local/bin/)

# LIKELY SOURCE OF PROBLEM!
# the following ~/.profile is only executed on login shells!

# HMMM....bashrc gets triggered on login from ">wsl"
#       ...but so does .profile

# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
# if [ -n "$BASH_VERSION" ]; then
#     # include .bashrc if it exists
#     if [ -f "$HOME/.bashrc" ]; then
#         . "$HOME/.bashrc"
#     fi
# fi

# # set PATH so it includes user's private bin directories
# PATH="$HOME/bin:$HOME/.local/bin:$PATH"