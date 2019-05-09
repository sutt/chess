
class Messages:

    def __init__(self):

        self.WELCOME_MSG = (
''' 
-------------------------------------
|      Welcome to Chess!            |
-------------------------------------
Play against Stockfish8 on Cmd Line.
   Set all configurations in flags;
     see --confighelp for options.
       Move cmds like: "a2 a4"
'''
        )
        self.CONFIG_HELP_MSG = (
''' 
Set your game like this, all params optional:
  --myplayer <black, white>
  --1v1      (for control of both players)
  --network  (stockfish runs on WSL)
e.g. >python3 main.py --myplayer black --network
'''
        )

    @staticmethod
    def CONFIG_INIT_MSG(b_interactive, b_white, b_stockfish_cli):
        return (
''' 
  You're playings against a: %s
  You're playing as:         %s
  Stockfish Interface:       %s
''' %  (
'human' if b_interactive        else 'computer',
'white' if b_white              else 'black',
'cli'   if b_stockfish_cli      else 'network',
       )
)

    @staticmethod
    def BAD_PLAYER(s_myplayer):
        return (
'''
failed to recognize player color, --mycolor `%s`
''' % str(s_myplayer)
        )