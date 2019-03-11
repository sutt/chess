from src.main import Game
# import src.main.Game as Game

# if __name__ == "__main__":
#     import .src



game = Game( manual_control = (1,)
                ,stockfish_control= (0,)
                ,b_display_show_opponent = True
                ,b_log_move = True
                )
game.play()