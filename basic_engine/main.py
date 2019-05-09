import os, sys
import argparse
from src.main import Game
from src.messages import Messages

''' this script is called to run as a command line game 
    for a user; to run developer / data science type operations 
    see docs/cmds-list.txt
'''

msg = Messages()

ap = argparse.ArgumentParser()
ap.add_argument("--1v1", action="store_true")
ap.add_argument("--myplayer", type=str)
ap.add_argument("--network", action="store_true")
ap.add_argument("--confighelp", action="store_true")

args = vars(ap.parse_args())

if args["confighelp"]:
    print(msg.CONFIG_HELP_MSG)
    sys.exit(0)

# default config options
b_interactive = False
b_white = True
b_stockfish_cli = True

# change defaults with flags
if args["1v1"]:
    b_interactive = True

if args["myplayer"] is not None:

    str_myplayer = str(args["myplayer"]).strip().lower()

    if str_myplayer not in ("black", "white"):

        print(msg.BAD_PLAYER(str_myplayer))
        sys.exit(0)
    
    if str_myplayer == "black":
            b_white = False

if args["network"]:
    b_stockfish_cli = False

# set args for game class
if b_interactive:
    manual_control      = (1,0)
    stockfish_control   = ()
elif b_white:
    manual_control      = (1,)
    stockfish_control   = (0,)
else:
    manual_control      = (0,)
    stockfish_control   = (1,)


print(msg.WELCOME_MSG)
print(msg.CONFIG_INIT_MSG(b_interactive,b_white,b_stockfish_cli))

game = Game(     manual_control = manual_control
                ,stockfish_control= stockfish_control
                ,b_stockfish_cli = b_stockfish_cli
                ,b_display_show_opponent = True
                ,b_log_move = True
                )
game.play()

print("exiting chess app\n")