from utils import print_board_letters

class GameLog:
    def __init__(self,**kwargs):
        
        self.board_pre_turn = True
        self.board_pre_turn_oppoenent = kwargs.get('b_log_show_opponent', False)
        self.manual_control = kwargs.get('manual_control', ())
        
        self.moves_log = []
        

    def print_turn(self, board, pieces, player, **kwargs):
        

        if (self.board_pre_turn and 
            ((player in self.manual_control) or 
                self.board_pre_turn_oppoenent)):

            print_board_letters(board, pieces, True)


    def log_game(self, **kwargs):
        print 'game over.'

