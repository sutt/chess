import time

from utils import print_board_letters

class GameLog:
    def __init__(self,**kwargs):
        
        self.board_pre_turn = True
        self.board_pre_turn_oppoenent = kwargs.get('b_log_show_opponent', False)
        self.manual_control = kwargs.get('manual_control', ())
        
        self.b_moves_log = False
        self.moves_log = []
        
        self.b_num_available = kwargs.get('b_num_available',False)
        self.log_num_available = []
        
        self.b_turn_time = kwargs.get('b_turn_time',False)
        self.t0 = time.time()
        self.log_turn_time = []
        

    def add_moves_log(self
                     ,move
                     ,num_available = None
                     ):
        if self.b_moves_log:
            self.moves_log.append(move)
        
        if self.b_num_available:
            #note this first
            self.log_num_available.append(num_available)
        
        if self.b_turn_time:
            _time = time.time() - self.t0
            self.log_turn_time.append(_time)
            self.t0 = time.time()


    def get_moves_log(self):
        return copy.copy(self.moves_log)

    def get_log_num_available(self):
        return copy.copy(self.log_num_available)

    def get_log_turn_time(self):
        return copy.copy(self.log_num_available)

    
    def print_turn(self, board, pieces, player, **kwargs):

        if (self.board_pre_turn and 
            ((player in self.manual_control) or 
                self.board_pre_turn_oppoenent)):

            print_board_letters(board, pieces, True)

