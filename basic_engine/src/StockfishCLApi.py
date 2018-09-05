import os
from utils import alphamove_to_posmove
from utils import pos_to_alphanum
from utils import find_app_path_root
from StockfishLib import Stockfish

class StockfishCLApi():

    def __init__(self):
    
        self.interface = Stockfish(path=os.path.join(
                                        find_app_path_root(__file__)
                                        ,"stockfish"
                                        ,"Stockfish"
                                        ,"src"
                                        ,"stockfish"
                                        )
                                    )

        # self.interface = Stockfish(path="../../stockfish/Stockfish/src/stockfish")

    def get_move(self, list_log_moves, available_moves):
        ''' 
            Args:
                list_log_moves:   list of MoveCode's
                available_moves:  moves from play(), list of MoveCode's
            Returns:
                move: one MoveCode (or None on failed validation)
        '''

        list_log = self._movecodelist_to_movelist(list_log_moves)

        if list_log != []:                   #disregard for first ply
            self._set_position(list_log)

        str_best_move = self._get_best_move()
        if str_best_move == "":
            return None
            
        movetuple_best_move = self._movestr_to_movecode(str_best_move)
        
        for _m in available_moves:
            if movetuple_best_move == (_m.pos0, _m.pos1):
                return _m

        return None     #Error - movetuple is not in available_moves

    

    def _set_position(self, list_log):
        self.interface.set_position(list_log)


    def _get_position(self):
        pass


    def _get_best_move(self):
        return self.interface.get_best_move()
        


    @staticmethod
    def _movecodelist_to_movelist(list_log_moves):
        ''' 
            input:  list_log_moves: list of MoveCode's
            output: list of strings (or [] for empty list)
            example:
                [
                  MoveHolder(pos0=(6, 4), pos1=(4, 4), code=0)
                 ,MoveHolder(pos0=(1, 4), pos1=(4, 3), code=0)
                ]
              ->
                ["e2e4", "g7g5"]
        '''
        temp = [
                str(pos_to_alphanum(elem.pos0)) + 
                str(pos_to_alphanum(elem.pos1))
                for elem in list_log_moves
                ]
        
        return temp

    
    @staticmethod
    def _movestr_to_movecode(str_move):
        ''' input: str of two alphanums corresponsding to pos0 and pos1
            output: 2-ple of 2-ple's corresponding int coords for pos0 and pos1
            example: "e2e4" -> ((6,4), (4,4))
        '''
        space_sep_move = str_move[:2] + " " + str_move[2:]
        return alphamove_to_posmove(space_sep_move)





from datatypes import moveHolder, moveAHolder
Move = moveHolder()
MoveA = moveAHolder()


def test_sn_movecodelist_to_movestr():
    
    sn = StockfishCLApi    #note: no need to instantiate

    list_move_1 = [
         Move(pos0 = (6,4), pos1 = (4,4), code = 0)
        ,Move(pos0 = (1,4), pos1 = (3,4), code = 0)
    ]

    str_alpha_1 = sn._movecodelist_to_movelist(list_move_1)

    assert str_alpha_1 == ["e2e4","e7e5"]

    list_move_blank = []

    str_alpha_blank = sn._movecodelist_to_movelist(list_move_blank)

    assert str_alpha_blank == []

    #TODO - convert alphanum moves to movecode
    #TODO - castling
    #TODO - enpassant


def test_sn_movestr_to_movecode():

    sn = StockfishCLApi
    assert sn._movestr_to_movecode("e2e4") == ((6,4), (4,4))
    assert sn._movestr_to_movecode("a2e8") == ((6,0), (0,4))

    
    
def test_sn_get_best_move_1():
    ''' basic example of bestmove on ply 3 '''
    
    #e4 e5 game
    list_log_moves = [
         Move(pos0 = (6,4), pos1 = (4,4), code = 0)
        ,Move(pos0 = (1,4), pos1 = (3,4), code = 0)
    ]

    #available moves for white; ply=3
    MoveHolder = moveHolder()
    available_moves = [MoveHolder(pos0=(7, 1), pos1=(5, 2), code=0), MoveHolder(pos0=(7, 1), pos1=(5, 0), code=0), MoveHolder(pos0=(7, 3), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 3), pos1=(5, 5), code=0), MoveHolder(pos0=(7, 3), pos1=(4, 6), code=0), MoveHolder(pos0=(7, 3), pos1=(3, 7), code=0), MoveHolder(pos0=(7, 4), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 5), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 5), pos1=(5, 3), code=0), MoveHolder(pos0=(7, 5), pos1=(4, 2), code=0), MoveHolder(pos0=(7, 5), pos1=(3, 1), code=0), MoveHolder(pos0=(7, 5), pos1=(2, 0), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 7), code=0), MoveHolder(pos0=(7, 6), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 0), pos1=(5, 0), code=0), MoveHolder(pos0=(6, 0), pos1=(4, 0), code=0), MoveHolder(pos0=(6, 1), pos1=(5, 1), code=0), MoveHolder(pos0=(6, 1), pos1=(4, 1), code=0), MoveHolder(pos0=(6, 2), pos1=(5, 2), code=0), MoveHolder(pos0=(6, 2), pos1=(4, 2), code=0), MoveHolder(pos0=(6, 3), pos1=(5, 3), code=0), MoveHolder(pos0=(6, 3), pos1=(4, 3), code=0), MoveHolder(pos0=(6, 5), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 5), pos1=(4, 5), code=0), MoveHolder(pos0=(6, 6), pos1=(5, 6), code=0), MoveHolder(pos0=(6, 6), pos1=(4, 6), code=0), MoveHolder(pos0=(6, 7), pos1=(5, 7), code=0), MoveHolder(pos0=(6, 7), pos1=(4, 7), code=0)]

    sn = StockfishCLApi()
    best_move = sn.get_move(list_log_moves, available_moves)

    assert best_move == Move(pos0 = (6,3), pos1 = (4,3), code = 0)


def test_sn_best_move_2():
    ''' basic example of bestmove on ply 1 '''
    
    #start-position game
    list_log_moves = []

    #available moves for white; ply=1
    MoveHolder = moveHolder()
    available_moves = [MoveHolder(pos0=(7, 1), pos1=(5, 2), code=0), MoveHolder(pos0=(7, 1), pos1=(5, 0), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 7), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 0), pos1=(5, 0), code=0), MoveHolder(pos0=(6, 0), pos1=(4, 0), code=0), MoveHolder(pos0=(6, 1), pos1=(5, 1), code=0), MoveHolder(pos0=(6, 1), pos1=(4, 1), code=0), MoveHolder(pos0=(6,2), pos1=(5, 2), code=0), MoveHolder(pos0=(6, 2), pos1=(4, 2), code=0), MoveHolder(pos0=(6, 3),pos1=(5, 3), code=0), MoveHolder(pos0=(6, 3), pos1=(4, 3), code=0), MoveHolder(pos0=(6, 4), pos1=(5, 4), code=0), MoveHolder(pos0=(6, 4), pos1=(4, 4), code=0), MoveHolder(pos0=(6, 5), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 5), pos1=(4, 5), code=0), MoveHolder(pos0=(6, 6), pos1=(5, 6), code=0), MoveHolder(pos0=(6, 6), pos1=(4, 6), code=0), MoveHolder(pos0=(6, 7), pos1=(5, 7), code=0), MoveHolder(pos0=(6, 7), pos1=(4, 7), code=0)]

    sn = StockfishCLApi()
    best_move = sn.get_move(list_log_moves, available_moves)

    assert best_move == Move(pos0 = (6,4), pos1 = (4,4), code = 0)  # e4
