import sys, random, time

from basic import *
from utils import *
from datatypes import moveHolder
from GameLog import GameLog
from TurnStage import increment_turn, get_available_moves, check_moves, apply_move
from TurnStage import filter_king_check

Move = moveHolder()

class Game():
    
    def __init__(
        self
        ,manual_control = () 
        ,instruction_control = () 
        ,s_instructions = ""
        ,b_log_show_opponent = False
        ,init_board = None
        ,init_player = None
        ,init_pieces = None
        ,test_exit_moves = None
        ):

        self.manual_control = manual_control
        self.instructions = parse_instructions(s_instructions)
        self.instruction_control = instruction_control 
        if len(self.instructions) > 0:
            self.instruction_control = (0,1)
        
        self.i_turn = 0
        
        self.b_test_exit = False
        self.test_data = None
        self.test_exit_iturn = test_exit_moves

        self.outcome = None

        self.init_player = init_player
        self.init_board = copy.deepcopy(init_board)
        self.init_pieces = copy.deepcopy(init_pieces)

        self.log = GameLog(manual_control = self.manual_control
                          ,b_log_show_opponent = b_log_show_opponent 
                           )
        


    def check_test_exit_moves(self, **kwargs):
        if self.test_exit_iturn is not None:
            if self.i_turn == self.test_exit_iturn:
                return True
        return False
            

    def check_test_exit(self, **kwargs):
        if len(self.instruction_control) > 0:
            if self.i_turn == len(self.instructions):
                return True
        return False
        
    
    def select_move(self, moves, player, board): 
    
        if int(player) in self.instruction_control:
            #TODO - instruction.pop(0)
            move = instruction_input(board, moves, self.instructions, self.i_turn)
        elif int(player) in self.manual_control:
            move = player_control_input(board, moves)
        else:
            move_i = random.sample(range(0,len(moves)),1)[0]
            move = moves[move_i]
        return move



    def play(self, **kwargs):

        board = Board()
        
        if self.init_board is not None:
            board.set_data(self.init_board)
            pieces = self.init_pieces
        else:
            board, pieces = place_pieces(board)
        
        player = False      #at increment_turn it will change to True
        if self.init_player is not None:
            player = not(self.init_player)

        self.i_turn = 0     #at increment_turn it will change to 1

        game_going = True
        
        while(game_going):
            
            if self.b_test_exit:
                return self.test_data
            
            player, self.i_turn = increment_turn(player, self.i_turn)

            moves = get_available_moves(pieces, board, player)

            moves = filter_king_check(board, pieces, moves, player)
            
            self.log.print_turn(board, pieces, player)

            if self.check_test_exit_moves():
                self.b_test_exit = True
                self.test_data = copy.deepcopy(moves)
                continue

            check_code = check_moves(moves, board, player)  #TODO - rename check_endgame()
            
            if check_code < 0:
                game.outcome = 'LOSS' # or 'STALEMATE'
                game_going = False
                continue

            move = self.select_move(moves, player, board)

            if move == -1:      #TODO if the_move is None:
                self.b_test_exit = True
                self.test_data = self.i_turn
                continue

            board, pieces = apply_move(move, board, pieces, player)
                        
            self.log.add_moves_log(move)

            if self.check_test_exit():
                self.b_test_exit = True
                self.test_data = copy.deepcopy(board)
                continue

        return self.outcome, self.log.get_moves_log()


def test_castling_allowed():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h7"
    game = Game(s_instructions = ss)
    board = game.play()
    assert board.data_by_player[7][5] == 1
    assert board.data_by_player[7][6] == 3

def test_castling_disallowed_rook():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h8 h7 8. b4 c4 9. h7 h8 10. b5 c5 11. h5 h7"
    game = Game(s_instructions = ss)
    break_turn = game.play()
    assert break_turn == 11

def test_castling_disallowed_king():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5 11. h5 h7"
    game = Game(s_instructions = ss)
    break_turn = game.play()
    assert break_turn == 11

def test_enpassant_take():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. d2 c3"
    game = Game(s_instructions = ss)
    board = game.play()
    board.print_board(b_player_data=True)
    assert board.data_by_player[2][2] == 1
    assert board.data_by_player[3][2] == 0
    

def test_enpassant_disallowed():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. g8 e8 6. b1 c1 7. d2 c3"
    game = Game(s_instructions = ss)
    break_turn = game.play()
    assert break_turn == 7

def test_king_in_check1():
    
    ''' Don't let white king move into check '''

    test_board = Board()
    test_pieces = []
    
    POS = (6,0)
    test_pieces.append( Pawn(b_white = True, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = 1

    POS = (7,0)
    white_king = King(b_white = True, pos = POS)
    white_king.king_can_castle = False
    test_pieces.append(white_king )
    test_board.data_by_player[POS[0]][POS[1]] = 3

    POS = (0,1)
    test_pieces.append( Rook(b_white = False, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = -1

    game = Game(init_board = test_board.data_by_player
                ,init_pieces = test_pieces
                ,init_player = True
                ,test_exit_moves = 1
                )
    
    moves = game.play()

    assert moves == [Move(pos0=(6, 0), pos1=(5, 0), code=0), Move(pos0=(6, 0), pos1=(4, 0), code=0)]
    #yes, namedtuples are assert as equivalent to generic-tuples
    assert moves == [ ( (6,0),(5,0),0), ( (6,0),(4,0),0) ]

def test_king_in_check2():
    
    ''' White can only kill the black rook putting him in check '''

    test_board = Board()
    test_pieces = []
    
    POS = (6,0)
    test_pieces.append( Pawn(b_white = True, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = 1

    POS = (7,0)
    white_king = King(b_white = True, pos = POS)
    white_king.king_can_castle = False
    test_pieces.append(white_king )
    test_board.data_by_player[POS[0]][POS[1]] = 3

    POS = (7,1)
    test_pieces.append( Rook(b_white = False, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = -1

    game = Game(init_board = test_board.data_by_player
                ,init_pieces = test_pieces
                ,init_player = True
                ,test_exit_moves = 1
                )
    
    moves = game.play()
    print moves
    assert moves == [ ( (7,0),(7,1),0) ]

def test_king_in_check3():
    
    ''' White can NOT kill the black rook putting him in check;
    only hide. '''

    test_board = Board()
    test_pieces = []
    
    POS = (5,0)
    test_pieces.append( Pawn(b_white = True, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = 1

    POS = (7,0)
    white_king = King(b_white = True, pos = POS)
    white_king.king_can_castle = False
    test_pieces.append(white_king )
    test_board.data_by_player[POS[0]][POS[1]] = 3

    POS = (7,1)
    test_pieces.append( Rook(b_white = False, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = -1

    POS = (0,1)
    test_pieces.append( Rook(b_white = False, pos = POS))
    test_board.data_by_player[POS[0]][POS[1]] = -1

    game = Game(init_board = test_board.data_by_player
                ,init_pieces = test_pieces
                ,init_player = True
                ,test_exit_moves = 1
                )
    
    moves = game.play()
    print moves
    assert moves == [ ( (7,0),(6,0),0) ]


if __name__ == "__main__":
    # test_king_in_check3()
    game = Game(manual_control = (1,), b_log_show_opponent = True)
    game.play()