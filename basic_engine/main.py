import sys
from src.main import Game

game = Game( manual_control = (1,)
                ,stockfish_control= (0,)
                ,b_display_show_opponent = True
                ,b_log_move = True
                )
game.play()