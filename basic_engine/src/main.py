import os, sys, random, time

from basic import *
from utils import *
from GameLog import *
from datatypes import moveHolder
from GameLog import GameLog
from GameLog import GameSchema
from Display import Display
from TurnStage import increment_turn, get_available_moves, apply_move
from TurnStage import check_endgame
from TurnStage import is_king_in_check
from TurnStage import filter_check_naive
from TurnStage import filter_check_opt   

from TurnStage import filter_check_test_copy   
from TurnStage import filter_check_test_copy_apply   
from TurnStage import filter_check_test_copy_apply_2
from TurnStage import filter_check_test_copy_apply_3
from TurnStage import filter_check_test_copy_opt

if os.name == 'nt':
    from StockfishNetwork import StockfishNetworking
if os.name == 'posix':
    from StockfishCLApi import StockfishCLApi



Move = moveHolder()

class Game():
    
    def __init__(
        self
        ,manual_control = () 
        ,instruction_control = () 
        ,pgn_control = ()
        ,stockfish_control = ()
        ,s_instructions = ""
        ,s_pgn_instructions = ""
        ,b_initialize = True
        ,init_board = None
        ,init_player = None
        ,init_pieces = None
        ,test_exit_moves = None
        ,b_display_show_opponent = False
        ,b_display_always_print = False
        ,b_display_never_print = False
        ,b_log_move = False
        ,b_log_turn_time = False
        ,b_log_num_available = False
        ,b_log_check_schedule = False
        ,b_log_full = False
        ):

        self.manual_control = manual_control

        self.stockfish_control = stockfish_control
        if len(self.stockfish_control) > 0:
            if os.name == 'nt':
                self.stockfish_interface = StockfishNetworking(b_launch_server=True)
            if os.name == 'posix':
                self.stockfish_interface =StockfishCLApi()
            

        self.instructions = parse_instructions(s_instructions)
        self.instruction_control = instruction_control 
        if len(self.instructions) > 0:
            self.instruction_control = (0,1)
        
        self.pgn_control = pgn_control
        self.pgn_instructions = parse_pgn_instructions(s_pgn_instructions)
        self.pgn_num_insturctions = len(self.pgn_instructions)
        if len(self.pgn_instructions) > 0:
            self.pgn_control = (0,1)

        self.i_turn = 0
        
        self.b_test_exit = False
        self.test_data = None
        self.test_exit_iturn = test_exit_moves

        self.outcome = None

        self.init_switch = b_initialize
        self.init_player = init_player
        self.init_board = copy.deepcopy(init_board)
        self.init_pieces = copy.deepcopy(init_pieces)

        self.saved_state = {}

        self.display = Display(b_show_opponent = b_display_show_opponent
                               ,b_never_print = b_display_never_print
                               ,b_always_print = b_display_always_print
                               ,manual_control = self.manual_control
                               )

        self.log = GameLog(manual_control = self.manual_control
                          ,b_log_move = b_log_move
                          ,b_turn_time = b_log_turn_time
                          ,b_num_available = b_log_num_available
                          ,b_check_schedule = b_log_check_schedule
                          ,b_full_log = b_log_full
                           )
        
    def get_gamelog(self):
        return self.log

    def reset_test(self):
        self.b_test_exit = False

    def reset_init_switch(self):
        self.init_switch = True

    def check_test_exit_moves(self, **kwargs):
        '''bool: exit after 'moves' is calcd / before check_enggame() in play().'''
        if self.test_exit_iturn is not None:
            if self.i_turn == self.test_exit_iturn:
                return True
        return False
            
    def check_test_exit(self, **kwargs):
        '''bool: exit at bottom of turn loop in play(), after apply_move(). '''
        if len(self.instruction_control) > 0:
            if self.i_turn == len(self.instructions):
                return True
        if len(self.pgn_control) > 0:
            if self.i_turn == self.pgn_num_insturctions:
                return True
            
        return False
        
    
    def select_move(self, moves, player, pieces, board): 
    
        if int(player) in self.instruction_control:
            move = instruction_input(board, moves, self.instructions, self.i_turn)
        elif int(player) in self.manual_control:
            move = player_control_input(board, moves, self.log)
        elif int(player) in self.pgn_control:
            move = pgn_deduction(board, pieces, moves, self.pgn_instructions, self.i_turn)
        elif int(player) in self.stockfish_control:
            move = self.stockfish_interface.get_move(self.log.get_log_move(), moves)
        else:
            move_i = random.sample(range(0,len(moves)),1)[0]
            move = moves[move_i]
        return move


    def initialize(self, init_to_save=False):
        ''' '''
        _board = Board()
        
        #Set board and pieces
        if self.init_board is not None:
            # init_board represent data_by_player
            _board.set_data(self.init_board)     
            _pieces = self.init_pieces
        else:
            _board, _pieces = place_pieces(_board)
        
        # Set player and i_turn
        # These incremetent at top-of-turn-loop; 
        # so they're off by one right now.
        
        #TODO - make i_turn local and overideable
        self.i_turn = 0

        _player = False 
        if self.init_player is not None:
            _player = not(self.init_player)        
        
        self.init_switch = False

        if init_to_save:
            self.save(_board,_pieces,_player)

        return _board, _pieces, _player


    def load(self):
        ''' load relevant state from Game into play '''
        return (
                self.saved_state['board']
                ,self.saved_state['pieces']
                ,self.saved_state['player']
            )


    def save(self, board, pieces, player):
        ''' save relevant state from play into Game '''
        self.saved_state['board'] = board
        self.saved_state['pieces'] = pieces
        self.saved_state['player'] = player
        

    def play(self, **kwargs):

        if self.init_switch:
            board, pieces, player = self.initialize()
        if kwargs.get('init_load', False):
            board, pieces, player = self.load()
            self.log.set_t0()

        game_going = True
        
        while(game_going):
            
            if self.b_test_exit:
                return self.test_data
            
            player, self.i_turn = increment_turn(player, self.i_turn)

            if kwargs.get('check_for_check', True):
                b_player_in_check = is_king_in_check(board, pieces, player)
            else:
                b_player_in_check = False
            board.set_player_in_check(player, b_player_in_check)

            moves = get_available_moves(pieces, board, player)

            b_bypass = kwargs.get('bypass_irregular', False)

            if kwargs.get('filter_check_naive', False):
                moves = filter_check_naive(board, pieces, moves, player, b_bypass)
            if kwargs.get('filter_check_opt', True):
                moves = filter_check_opt(board, pieces, moves, player, b_bypass)

            if kwargs.get('filter_check_test_copy', False):
                moves = filter_check_test_copy(board, pieces, moves, player)
            if kwargs.get('filter_check_test_copy_apply', False):
                moves = filter_check_test_copy_apply(board, pieces, moves, player)
            if kwargs.get('filter_check_test_copy_apply_2', False):
                moves = filter_check_test_copy_apply_2(board, pieces, moves, player)
            if kwargs.get('filter_check_test_copy_apply_3', False):
                moves = filter_check_test_copy_apply_3(board, pieces, moves, player)
            if kwargs.get('filter_check_test_copy_opt', False):
                moves = filter_check_test_copy_opt(board, pieces, moves, player)
            
            
            self.display.print_turn(pieces, player)

            if self.check_test_exit_moves():
                self.b_test_exit = True
                self.test_data = {}
                self.test_data['moves'] = copy.deepcopy(moves)
                self.test_data['board'] = copy.deepcopy(board)
                self.test_data['pieces'] = copy.deepcopy(pieces)
                continue

            check_code, outcome = check_endgame(moves, pieces, board, player)
            
            if check_code < 0:
                self.outcome = outcome
                game_going = False
                continue

            move = self.select_move(moves, player, pieces, board)

            if move is None:                #Catch move which is not legal
                self.b_test_exit = True
                self.test_data = self.i_turn
                continue

            board, pieces = apply_move(move, board, pieces, player)
                        
            self.log.add_turn_log(move, moves, pieces, player, b_player_in_check)

            if self.check_test_exit():
                self.b_test_exit = True
                self.test_data = {}
                self.test_data['last_player'] = player
                self.test_data['pieces'] = copy.deepcopy(pieces)
                self.test_data['board'] = copy.deepcopy(board)
                continue

        #True exit: only here when check_endgame has been satisfied
        ret_data = {}
        ret_data['outcome'] = self.outcome
        ret_data['board'] = board
        ret_data['pieces'] = pieces
        return ret_data


PATH_TO_DATA = os.path.join(find_app_path_root(__file__), 'basic_engine', 'data')

def test_castling_allowed_misc():
    
    ss = "1. g1 h3 2. a7 a6 3. e2 e4 4. b7 b6 5. f1 d3 6. c7 c6 7. e1 g1"
    game = Game(s_instructions = ss)
    board = game.play()
    board = board['board']
    assert board.data_by_player[7][5] == 1
    assert board.data_by_player[7][6] == 3

def test_castling_disallowed_rook():
    
    ss = "1. g1 h3 2. a7 a6 3. e2 e4 4. b7 b6 5. f1 d3 6. c7 c6 7. h1 g1 8. d7 d6 9. g1 h1 10. e7 e6 11. e1 g1"
    game = Game(s_instructions = ss)
    break_turn = game.play()
    assert break_turn == 11

def test_castling_disallowed_king():
    
    ss = "1. g1 h3 2. a7 a6 3. e2 e4 4. b7 b6 5. f1 d3 6. c7 c6 7. e1 f1 8. d7 d6 9. f1 e1 10. e7 e6 11. e1 g1"
    game = Game(s_instructions = ss)
    break_turn = game.play()
    assert break_turn == 11

def test_enpassant_take():
    
    ss = "1. b2 b4 2. h7 h6 3. b4 b5 4. c7 c5 5. b5 c6"
    game = Game(s_instructions = ss)
    board = game.play()
    board = board['board']
    # board.print_board(b_player_data=True)
    assert board.data_by_player[2][2] == 1
    assert board.data_by_player[3][2] == 0
    

def test_enpassant_disallowed():
    
    ss = "1. b2 b4 2. h7 h6 3. b4 b5 4. c7 c5 5. h2 h4 6. a7 a6 7. b5 c6"
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
    moves = moves['moves']

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
    moves = moves['moves']
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
    moves = moves['moves']
    print moves
    assert moves == [ ( (7,0),(6,0),0) ]

def test_post_castling_move_rook():

    ss_post_castling = "1. g1 h3 2. h7 h6 3. e2 e4 4. a7 a5 5. f1 d3 6. b7 b6 7. e1 g1 8. h8 h7 9. f1 e1 10. g8 f6"
    game = Game(s_instructions = ss_post_castling)
    board = game.play()
    board = board['board']
    assert board.data_by_player[7][4] == 1
    assert board.data_by_player[7][5] == 0

def test_player_in_and_out_of_check():
    
    #Black is checked on 7th move
    ss = "1. d2 d4 2. e7 e5 3. b1 a3 4. e5 d4 5. d1 d4 6. h7 h5 7. d4 e4 8. f8 e7 9. e4 e5 10. a7 a6"
    _i_exit_moves = 8
    _b_current_player = False
    
    game = Game(s_instructions = ss
                ,test_exit_moves = _i_exit_moves
                )
    test_data = game.play()
    
    board_data = test_data['board']
    b_check = board_data.b_in_check(_b_current_player)
    
    assert b_check == True

    #Black is not in check after white's 9th move
    _i_exit_moves = 10
    _b_current_player = False
    
    game = Game(s_instructions = ss
                ,test_exit_moves = _i_exit_moves
                )
    test_data = game.play()
    
    board_data = test_data['board']
    b_check = board_data.b_in_check(_b_current_player)
    
    assert b_check == False

def test_castling_disallowed_in_check():    

    #Black queen has King in check on turn 8
    ss = "1. g1 h3 2. d7 d5 3. e2 e4 4. d8 d6 5. f1 d3 6. a7 a5 7. e4 e5 8. d6 e5 9. e1 g1 10.a2 a4"
    game = Game(s_instructions = ss)
    exit_turn = game.play()
    assert exit_turn == 9

def test_castling_disallowed_into_check():  

    #Black queen has King-Castling destination in check on turn 8, try to castle turn 9
    ss = "1. g1 h3 2. d7 d5 3. e2 e4 4. d8 d6 5. f1 c4 6. d6 g3 7. a2 a4 8. g3 g2 9. e1 g1 10. b2 b4"
    game = Game(s_instructions = ss)
    exit_turn = game.play()
    assert exit_turn == 9  

def test_castling_disallowed_when_dead():
    
    #Setup
    ss = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2"

    #Turn 10 capture rook, Turn 11 Castle
    ss = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"
    
    game = Game(s_instructions = ss)
    exit_turn = game.play()
    assert exit_turn == 11

def test_promotion_on_advance():
    
    #Test for pawn gone
    #Test for queen there
    #Test for putting king in check with promoted piece

    #pawn promoted causing check
    ss = "1. a2 a4 2. b7 b5 3. a4 b5 4. d7 d5 5. b5 b6 6. c8 a6 7. b6 c7 8. d8 d6 9. c7 c8 10. h7 h5"
    game = Game(s_instructions = ss, test_exit_moves = 10)
    test_data = game.play()
    
    board = test_data['board']
    pieces = test_data['pieces']
    moves = test_data['moves']
    
    #Test a white piece is there
    assert board.data_by_player[0][2] == 1
    
    #Test there is no pawn at that pos
    back_row_pawns = filter(lambda p: p.white and p.__class__.__name__ == "Pawn"
                              and p.pos == (0,2) ,pieces)
    assert len(back_row_pawns) == 0

    #Test there is a queen there
    queen_at_pos = filter(lambda p: p.__class__.__name__ == "Queen" 
                            and p.pos == (0,2) ,pieces)

    assert len(queen_at_pos) == 1
    
    #Test there are two queens total
    white_queens = filter(lambda p: p.__class__.__name__ == "Queen" 
                            and p.white,pieces)

    assert len(white_queens) == 2

    #Test that black is incheck by the limited moves available to him
    assert moves == [Move(pos0=(2, 0), pos1=(0, 2), code=0), Move(pos0=(2, 3), pos1=(0, 3), code=0)]


def test_init_midgame_1():
    
    # A long game
    ss_pgn = "1. e4 Nh6 2. d4 c5 3. c3 g6 4. Nf3 Ng4 5. h3 d5 6. hxg4 dxe4 7. Nfd2 e3 8. fxe3 cxd4 9. cxd4 Bxg4 10. Qxg4 f6 11. Qe4 Qd6 12. Qxb7 Qg3+ 13. Kd1 a5 14. Qxa8 Bg7 15. Ne4 Qc7 16. Bb5+ Kf7 17. Nbc3 Qb6 18. Qd5+ Qe6 19. Bc4 Qxd5 20. Bxd5+ e6 21. Nd6+ Ke7 22. Nde4 g5 23. Bb3 Kf8 24. Rf1 Nc6 25. Nxf6 Nb4 26. Nxh7+ Ke8 27. Nxg5 e5 28. Bf7+ Kd7 29. dxe5 Rh2 30. e6+ Kd8 31. a3 Bxc3 32. axb4 Bxb4 33. Bd2 Bxd2 34. Kxd2 Rxg2+ 35. Kd3 Rxg5 36. Rfd1 Rd5+ 37. Ke2 Rxd1 38. Rxd1+ Ke7 39. Rd7+ Kf6 40. e4 a4 41. Ke3 Kg7 42. e5 Kf8 43. Rd8+ Kg7 44. Kd4 a3 45. bxa3 Kh6 46. e7 Kh7 47. e8=Q Kh6 48. Rd6+ Kg5 49. Qg8+ Kf4 50. Qh8 Kf3 51. Qh5+ Kf2 52. Rf6+ Kg2 53. Qf3+ Kg1 54. Qf2+ Kh1 55. Rh6# 1-0"
    
    display = Display()

    # OK, here's what happens with test_exit_moves:
    #   play:
    #       get_available_moves()
    #       print_board (before move is made or even selected)
    #       check_test_exit_moves
    #           continue -> top-of-loop (wihtout increment) and exit
    # So, to get board on black move (i_turn=2) use test_exit_moves = 2
    # Even though you would think exiting on an even number turn would 
    # cause you to start at an odd turn (therefore white turn), that's not
    # true because the final move in terst_exit_moves isnt applied,
    # it exits during consideration phase. 
    # Another tricky thing is a turn's printout corresponds to the board
    # under consideration, the move you select and execute only printsout
    # next turn, during opponents consideration phase.

    game = Game(s_pgn_instructions = ss_pgn
                ,pgn_control = (0,1)
                ,b_log_move = True
                ,test_exit_moves = 98   #exiting during black's consideration in pgn 49
                ,b_display_always_print = False
                )
    ret_data = game.play()
    
    moves = ret_data['moves']
    print moves
    
    my_board = ret_data['board']
    my_pieces = ret_data['pieces']    
    display.print_board_letters(my_pieces)

    #by test_exit_moves = 1, you never advance the game just
    #consider the current board
    game2 = Game(init_board = my_board.data_by_player   #note
                ,init_pieces = my_pieces
                ,init_player = False     #black has first play
                ,test_exit_moves = 1    #moves have reset
                )
    ret_data2 = game2.play()

    my_pieces2 = ret_data2['pieces']
    display.print_board_letters(my_pieces2)
    
    moves2 = ret_data2['moves']
    print moves2

    my_board2 = ret_data2['board']

    assert moves2 == moves
    assert my_board.data_by_player == my_board2.data_by_player


def test_filter_check_pawn_1():
    
    #Current optimal_filter_check() breaks on i_turn 98 (PGN 49 black move)
    ss_pgn = "1. e4 Nh6 2. d4 c5 3. c3 g6 4. Nf3 Ng4 5. h3 d5 6. hxg4 dxe4 7. Nfd2 e3 8. fxe3 cxd4 9. cxd4 Bxg4 10. Qxg4 f6 11. Qe4 Qd6 12. Qxb7 Qg3+ 13. Kd1 a5 14. Qxa8 Bg7 15. Ne4 Qc7 16. Bb5+ Kf7 17. Nbc3 Qb6 18. Qd5+ Qe6 19. Bc4 Qxd5 20. Bxd5+ e6 21. Nd6+ Ke7 22. Nde4 g5 23. Bb3 Kf8 24. Rf1 Nc6 25. Nxf6 Nb4 26. Nxh7+ Ke8 27. Nxg5 e5 28. Bf7+ Kd7 29. dxe5 Rh2 30. e6+ Kd8 31. a3 Bxc3 32. axb4 Bxb4 33. Bd2 Bxd2 34. Kxd2 Rxg2+ 35. Kd3 Rxg5 36. Rfd1 Rd5+ 37. Ke2 Rxd1 38. Rxd1+ Ke7 39. Rd7+ Kf6 40. e4 a4 41. Ke3 Kg7 42. e5 Kf8 43. Rd8+ Kg7 44. Kd4 a3 45. bxa3 Kh6 46. e7 Kh7 47. e8=Q Kh6 48. Rd6+ Kg5 49. Qg8+ Kf4 50. Qh8 Kf3 51. Qh5+ Kf2 52. Rf6+ Kg2 53. Qf3+ Kg1 54. Qf2+ Kh1 55. Rh6# 1-0"

    #Setup to the move in question
    game = Game(s_pgn_instructions = ss_pgn
                ,pgn_control = (0,1)
                ,b_log_move = True
                ,test_exit_moves = 98
                ,b_display_always_print = False
                )
    
    ret_data = game.play()
    my_board = ret_data['board']
    my_pieces = ret_data['pieces']    
    
    #2a - "Generic": Computationally expensive, but correct result
    game2a = Game(init_board = copy.deepcopy(my_board.data_by_player)
                ,init_pieces = copy.deepcopy(my_pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )
    ret_data2a = game2a.play(filter_check_opt = False
                            ,filter_check_naive = True
                            )
    generic_check_moves = ret_data2a['moves']

    #2b - "Opt": Computationally cheap, but incorrect result
    game2b = Game(init_board = copy.deepcopy(my_board.data_by_player)
                ,init_pieces = copy.deepcopy(my_pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )
    ret_data2b = game2b.play(filter_check_opt = True
                            ,filter_check_naive = False
                            )
    opt_check_moves = ret_data2b['moves']

    #Assess the difference
    print generic_check_moves
    print opt_check_moves

    #Heres the key move that Opt doesnt allow
    assert  Move(pos0=(3, 6), pos1=(4, 5), code=0) in generic_check_moves
    assert  Move(pos0=(3, 6), pos1=(4, 5), code=0) in opt_check_moves

    #More generally, they should always match
    assert generic_check_moves == opt_check_moves


def test_filter_check_pawn_2():
    
    #Based off check_pawn_1, 
    # here we move pawn (manually) to make sure its accounted for and prevents 
    # black king's move to (4,5)
    
    display = Display()

    s_test = """
   1 2 3 4 5 6 7 8

A  ~ ~ ~ ~ ~ ~ Q ~
B  ~ ~ ~ ~ ~ B ~ ~
C  ~ ~ ~ R ~ ~ ~ ~
D  ~ ~ ~ ~ ~ ~ k ~
E  ~ ~ ~ K ~ ~ ~ ~
F  P ~ ~ ~ P ~ ~ ~
G  ~ ~ ~ ~ ~ ~ ~ ~
H  ~ ~ ~ ~ ~ ~ ~ ~
"""    
    my_board, my_pieces = printout_to_data(s_test)

    game2a = Game(init_board = copy.deepcopy(my_board.data_by_player)
                ,init_pieces = copy.deepcopy(my_pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )
    ret_data2a = game2a.play(filter_check_opt = False
                            ,filter_check_naive = True
                            )
    generic_check_moves = ret_data2a['moves']

    game2b = Game(init_board = copy.deepcopy(my_board.data_by_player)
                ,init_pieces = copy.deepcopy(my_pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )
    ret_data2b = game2b.play(filter_check_opt = True
                            ,filter_check_naive = False
                            )
    opt_check_moves = ret_data2b['moves']
    
    
    #This is the move that the pawn should stop
    assert not(Move(pos0=(3, 6), pos1=(4, 5), code=0) in opt_check_moves)

    #This was originally wrong untill check_flag return added to pawn section 
    # filter_by_blocking_pieces().
    #That's why you don't split up your returns within a function.
    assert generic_check_moves == opt_check_moves

def test_filter_forward_diagonal_1():
    
    """This is looking at MOVE_TYPE['forward-diagonal'] used in Mirror.
        It looks to see that optimzed_check_filter views non-pawn pieces
        which attack by diagonal are viewed the same from "in front" and "behind".
        """
    
    s_test = """
    A  B ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert not(Move(pos0=(2, 2), pos1=(1, 1), code=0) in opt_check_moves)

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ B ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert not(Move(pos0=(2, 2), pos1=(3, 3), code=0) in opt_check_moves)


def test_filter_forward_diagonal_2():
    
    """This continues tests for forward-diagonal when right next to the piece.
        Also it tests the idea of moving king to capture and eliminate an
        unprotected opponent piece. Can opt do this?
        """
        

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ B ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(2, 2), pos1=(1, 1), code=0) in opt_check_moves

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ B ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(2, 2), pos1=(3, 3), code=0) in opt_check_moves

def test_pawn_check_true_positive_1():
    
    """Do filter_check() functions identify a pawn's attack as threatening king?"""
        

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ k ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ P ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print "\n".join(map(lambda s: str(s), generic_check_moves))
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(1, 2), pos1=(2, 2), code=0) in opt_check_moves

    assert not(Move(pos0=(1, 2), pos1=(1, 2), code=0) in opt_check_moves)
    assert not(Move(pos0=(1, 2), pos1=(2, 3), code=0) in opt_check_moves)

    #test it on promotion too.

    s_test = """
    A  ~ ~ k ~ ~ ~ ~ ~
    B  ~ ~ P ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(0, 2), pos1=(1, 2), code=0) in opt_check_moves
    
    assert not(Move(pos0=(0, 2), pos1=(0, 1), code=0) in opt_check_moves)
    assert not(Move(pos0=(0, 2), pos1=(0, 3), code=0) in opt_check_moves)

def test_pawn_check_negative_1():
    
    """Do filter_check() functions correctly not identify pawn's rear-diagonal 
        attack as threatening king?"""
        

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ P ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ k ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(3, 2), pos1=(2, 2), code=0) in opt_check_moves
    assert Move(pos0=(3, 2), pos1=(2, 1), code=0) in opt_check_moves
    assert Move(pos0=(3, 2), pos1=(2, 3), code=0) in opt_check_moves

    #test it without on promotion too.

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ P ~ ~ ~ ~ ~
    D  ~ ~ k ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(filter_check_opt = False
                                ,filter_check_naive = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    game.reset_init_switch()
    ret_data_opt = game.play(filter_check_opt = True
                                ,filter_check_naive = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(3, 2), pos1=(2, 2), code=0) in opt_check_moves
    assert Move(pos0=(3, 2), pos1=(2, 1), code=0) in opt_check_moves
    assert Move(pos0=(3, 2), pos1=(2, 3), code=0) in opt_check_moves


def test_cant_castle_into_check_1():
    
    """Do filter_check() functions correctly not identify pawn's rear-diagonal 
        attack as threatening king?"""
        
    #control case: can castle
    s_test = """
    A  r ~ ~ ~ k ~ ~ r
    B  p ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ R
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test, b_king_can_castle=True)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()

    moves = ret['moves']

    print "\n".join(map(lambda s:str(s), moves))

    assert Move(pos0=(0, 4), pos1=(0, 5), code=0) in moves
    assert Move(pos0=(0, 4), pos1=(0, 6), code=2) in moves

    #test case: cant castle
    s_test = """
    A  r ~ ~ ~ k ~ ~ r
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ R ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test, b_king_can_castle=True)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()

    moves = ret['moves']

    assert Move(pos0=(0, 4), pos1=(0, 5), code=0) in moves
    assert not(Move(pos0=(0, 4), pos1=(0, 6), code=2) in moves)

#test case: cant castle
    s_test = """
    A  r ~ ~ ~ k ~ ~ r
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ R ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test, b_king_can_castle=True)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()

    moves = ret['moves']

    assert Move(pos0=(0, 4), pos1=(0, 3), code=0) in moves
    assert not(Move(pos0=(0, 4), pos1=(0, 2), code=2) in moves)

def test_checkmate_simple_1():
    
    """Basic Checkmate test: that there are no moves remaining unfiltered,
        after filter_check has been applied. This doesn't look forn plays()
        return codes, only the test_exit_moves() return data."""
        
    #CONTROL case: not checkmate
    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ k
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ R
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()
    moves = ret['moves']

    assert len(moves) > 0

    #TEST case: checkmate
    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ k
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ R R
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()
    moves = ret['moves']

    assert len(moves) == 0

    #TEST case2: no moves of other pieces either
    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ k
    B  p ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ R R
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()
    moves = ret['moves']

    assert len(moves) == 0

    #TEST case3: you can block check
    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ k
    B  r ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ R R
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret = game.play()
    moves = ret['moves']

    assert len(moves) > 0


def test_checkmate_returncode_1():
    
    """Check return codes from play() a checkmate."""
        
    #Black is checkmated
    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ k
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ R R
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ K ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = pieces
                ,init_player = False     
                )

    ret = game.play()

    assert ret['outcome'] == (False, 'LOSS', 'CHECKMATE')

    assert len(ret['pieces']) == 4

    assert board.data_by_player == ret['board'].data_by_player

    #White is checkmated (note this is all backwards on purpose)
    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ K
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ r r
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ k ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = True
                )

    ret = game.play()

    assert ret['outcome'] == (True, 'LOSS', 'CHECKMATE')
    

def test_multi_pgn_games_1():
    
    '''test if we can load some pgn's and run them thru the final move'''

    num_games = 5

    f = open(os.path.join(PATH_TO_DATA ,'GarryKasparovGames.txt'), 'r')
    lines = f.readlines()
    f.close()

    s_games = lines[:num_games]

    for i, s_game in enumerate(s_games):
        
        game = Game(s_pgn_instructions = s_game)
        ret = game.play()
        
        #Printout
        print 'Line Num: ', str(i + 1)

        if isinstance(ret, dict):
            s_last_player = str(ret.get('last_player', 'N/A: no last_player'))
            print 'last player to move: ', s_last_player
        if isinstance(ret, int):
            print 'exited from move incompatiability'            
            print 'game.i_turn: ', str(ret)
            
            b_whites_move = ((ret % 2) == 1)

            pgn_turn = (ret + int(b_whites_move)) / 2
            s_player = 'White' if b_whites_move else 'Black'

            print 'On PGN turn: ', str(pgn_turn), ' Player: ', s_player
            print '\n'
            print s_game


def test_kasparov_game_10_pgn_err():
    
    '''This particular game caused a problem due to disambig pgn (turn 33 white) 
        info not included. From the parse. Using this mostly as regression test.'''
    
    problem_game_ind = 9
    
    f = open(os.path.join(PATH_TO_DATA ,'GarryKasparovGames.txt'), 'r')
    lines = f.readlines()
    f.close()

    s_game = lines[problem_game_ind]

    game = Game(s_pgn_instructions = s_game)
    ret = game.play()

    assert ret['last_player'] == True
    
def batchtest_multi_pgn_games_1(**kwargs):
    
    '''Function naming disables running by default. 
        This runs through all the games to see if play() can parse them.'''

    max_games = kwargs.get('max_games', None)
    modulo_print = kwargs.get('modulo_print', 100)
    data_path = os.path.join(PATH_TO_DATA ,'GarryKasparovGames.txt')

    f = open(data_path, 'r')
    lines = f.readlines()
    f.close()

    if max_games is not None:
        s_games = lines[:max_games]
    else:
        s_games = lines

    t = time.time()
    err_cntr = 0

    b_naive_check = kwargs.get('naive_check', False)
    print b_naive_check

    for i, s_game in enumerate(s_games):
        
        try:
            game = Game(s_pgn_instructions = s_game)
            if b_naive_check:
                ret = game.play(filter_check_naive = True
                                ,filter_check_opt = False)
            else:
                ret = game.play()
        except Exception as e:
            print 'Error in play() | line_i: ', str(i + 1)
            print str(e)
            err_cntr += 1
            continue
            
        if i % modulo_print == 0:
            s_secs = str(time.time() - t).split(".")[0]
            t = time.time()
            print 'line_i: ', str(i + 1), '  secs: ', s_secs
        
        
        if isinstance(ret, dict):
            s_last_player = str(ret.get('last_player', None))
            if s_last_player is None:
                print 'No Last Player | line_i: ', str(i + 1)
                print ret
                err_cntr += 1
            
        if isinstance(ret, int):
            print 'Move Incompatibility | line_i: ', str(i + 1)
            print 'game.i_turn: ', str(ret)    
            b_whites_move = ((ret % 2) == 1)
            pgn_turn = (ret + int(b_whites_move)) / 2
            s_player = 'White' if b_whites_move else 'Black'
            print 'On PGN turn: ', str(pgn_turn), ' Player: ', s_player
            err_cntr += 1
            # print '\n'
            # print s_game

    print 'err_cntr: ', str(err_cntr)

def test_filter_check_pinned_piece_1():
    
    #dont let white-knight at (5,2) move; it's pinned to king.

    s_test = """    
       1 2 3 4 5 6 7 8
    A  r ~ b q k ~ ~ r
    B  p p p p ~ p p p
    C  ~ ~ n ~ ~ n ~ ~
    D  ~ ~ ~ ~ p ~ ~ ~
    E  ~ b B ~ P ~ ~ ~
    F  ~ ~ N P ~ ~ ~ ~
    G  P P P ~ ~ P P P
    H  R ~ B Q K ~ N R
    """

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = True
                ,test_exit_moves = 1    
                )

    # ret = game.play(filter_check_naive=True)
    ret = game.play(filter_check_naive=False)
    moves = ret['moves']

    assert not(Move(pos0=(5, 2), pos1=(6, 4), code=0) in moves)

def test_printout_grid():
    
    ''' pretty printouts baselined here.
        b_grid_pos: view pos (row_num, col_num) [index-0]'''

    game = Game(test_exit_moves=1)
    ret = game.play()
    pieces = ret['pieces']

    display = Display()
    ret = display.print_board_letters(pieces)
    
    #note trailing \n on row 8
    s_benchmark = \
"""   A B C D E F G H

8  r n b q k b n r
7  p p p p p p p p
6  ~ ~ ~ ~ ~ ~ ~ ~
5  ~ ~ ~ ~ ~ ~ ~ ~
4  ~ ~ ~ ~ ~ ~ ~ ~
3  ~ ~ ~ ~ ~ ~ ~ ~
2  P P P P P P P P
1  R N B Q K B N R
"""
    assert ret == s_benchmark


    ret2 = display.print_board_letters(pieces, b_grid_pos=True)
    s_benchmark2 = \
"""   0 1 2 3 4 5 6 7

0  r n b q k b n r
1  p p p p p p p p
2  ~ ~ ~ ~ ~ ~ ~ ~
3  ~ ~ ~ ~ ~ ~ ~ ~
4  ~ ~ ~ ~ ~ ~ ~ ~
5  ~ ~ ~ ~ ~ ~ ~ ~
6  P P P P P P P P
7  R N B Q K B N R
"""
    assert ret2 == s_benchmark2

def test_log_schema_check_schedule_1():
    
    ''' Use GameSchema to record all the [alleged] checks in the pgn, and
        Use GameLog to record all checks in play(), verify they match up. 
    '''
    
    s_pgn = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'
    
    schema = GameSchema()
    schema.set_pgn_instructions(s_pgn)
    schema.all_parse_pgn_instructions()
    pgn_check_schedule = schema.get_check_schedule()

    game = Game(s_pgn_instructions = s_pgn
                ,b_log_check_schedule=True
                )
    ret = game.play()

    log_check_schedule = game.get_gamelog().get_log_check_schedule()

    #they're off by one b/c pgn records play who checks
    #but log records who is checked, thus one behind.

    assert pgn_check_schedule == [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, True, False, False, False, False, True, False, False, True, False, False, True, False, True, False, False, False, False, False, True, False, True]

    assert log_check_schedule == [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, True, False, False, False, False, True, False, False, True, False, False, True, False, True, False, False, False, False, False, True, False]

    assert log_check_schedule[1:] == pgn_check_schedule[:-1]

def test_log_schema_check_schedule_2():
    
    ''' Use GameLog to record info about game state. 
        Verify it exists and in correct form. '''
    
    s_pgn = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'

    game = Game(s_pgn_instructions = s_pgn
                ,b_log_full=True            #new-arg: GameLog collects all data
                )
    ret = game.play()

    num_pieces = game.get_gamelog().get_log_num_pieces()
    num_player_pieces = game.get_gamelog().get_log_num_player_pieces()

    assert num_pieces == [32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 31, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 29, 28, 28, 27, 26, 25, 24, 23, 22, 21, 20, 20, 20, 19, 18, 18, 18, 18, 18, 18, 18, 18, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 13, 13, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    assert num_player_pieces == [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 14, 14, 13, 13, 12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 7, 6, 7, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6]



def test_check_for_check_off():
    ''' Test that play() does not account for check when calc'ing with
        check_for_check set to False. '''

    #black move 19 is a check move
    ss = '1. d4 d5 2. c4 c6 3. Nf3 Nf6 4. Nc3 e6 5. Bg5 Nbd7 6. e3 Qa5 7. Nd2 Bb4 8. Qc2 O-O 9. Be2 e5 10. O-O exd4 11. Nb3 Qb6 12. exd4 dxc4 13. Bxc4 a5 14. a4 Qc7 15. Rae1 h6 16. Bh4 Bd6 17. h3 Nb6 18. Bxf6 Nxc4 19. Ne4 Bh2+ 20. Kh1 Nd6 21. Kxh2 Nxe4+ 22. Be5 Nd6 23. Qc5 Rd8 24. d5 Qd7 25. Nd4 Nf5 26. dxc6 bxc6 27. Nxc6 Re8 28. Rd1 Qe6 29. Rfe1 Bb7 30. Nd4 Nxd4 31. Qxd4 Qg6 32. Qg4 Qxg4 33. hxg4 Bc6 34. b3 f6 35. Bc3 Rxe1 36. Rxe1 Bd5 37. Rb1 Kf7 38. Kg3 Rb8 39. b4 axb4 40. Bxb4 Bc4 41. a5 Ba6 42. f3 Kg6 43. Kf4 h5 44. gxh5+ Kxh5 45. Rh1+ Kg6 46. Bc5 Rb2 47. Kg3 Ra2 48. Bb6 Kf7 49. Rc1 g5 50. Rc7+ Kg6 51. Rc6 Bf1 52. Bf2'

    game = Game(s_pgn_instructions=ss
                ,b_log_check_schedule=True)
    ret = game.play(check_for_check=False)

    check_log = game.get_gamelog().get_log_check_schedule()

    assert any(check_log) == False


if __name__ == "__main__":

    # Two-Player Setup
    # game = Game( manual_control = (0,1)
    #             ,b_display_show_opponent = True
    #             ,b_log_move = True
    #             )
    # game.play()

    # Player-v-AI Setup
    game = Game( manual_control = (1,)
                ,stockfish_control= (0,)
                ,b_display_show_opponent = True
                ,b_log_move = True
                )
    game.play()

    # s_instructions = "1. d4 e6 2. Nf3 Nf6 3. c4 Bb4+ 4. Nc3 b6 5. Qb3 Qe7 6. Bf4 d5 7. e3 Bb7 8. a3 Bxc3+ 9. Qxc3 O-O 10. Be2 dxc4 11. Qxc4 Rc8 12. O-O Ba6 13. Qc2 Bxe2 14. Qxe2 c5 15. Rac1 Nbd7 16. Qa6 h6 17. h3 Qe8 18. Bh2 cxd4 19. Nxd4 Nc5 20. Qe2 Qa4 21. Rc4 Qe8 22. Rfc1 a5 23. f3 a4 24. e4 Nfd7 25. Nb5 Qe7 26. Qe3 Qf6 27. e5 Qg6 28. Nd6 Rd8 29. Rg4 Qh7 30. Bf4 Kf8 31. Rd1 f5 32. exf6 Nxf6 33. Rh4 Nd5 34. Qe5 Nxf4 35. Rxf4+ Kg8 36. Rfd4 Rd7 37. Ne4 Rxd4 38. Rxd4 Qf5 39. Qxf5 exf5 40. Nxc5 bxc5 41. Rd5 Ra5 42. Rxf5 Rb5 43. Rf4 Rxb2 44. Rxa4 Ra2 45. h4 c4 46. Rxc4 Rxa3 47. Rc5 Ra4 48. h5 Ra2 49. Kh2 Rb2 50. Kh3 Rd2 51. g4 Rd1 52. Kg3 Rd4 53. Rc7 Ra4 54. Re7 Kf8 55. Re4 Ra5 56. Kf4 Kf7 57. Re5 Ra3 58. Ke4 Rb3 59. f4 Rb4+ 60. Kf5 Rb7 61. Rc5 Ra7 62. g5 hxg5 63. fxg5 g6+ 64. hxg6+ Kg7 65. Rc6 Ra5+ 66. Kg4 Ra1"
    # s_instructions = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'

    # game = Game(s_pgn_instructions=s_instructions
    #             # ,b_display_show_opponent = True
    #             ,b_log_full=True
    #             # ,test_exit_moves=20
    #             )
    # ret = game.play()
    # print ret

    # num_pieces = game.get_gamelog().get_log_num_pieces()
    # print num_pieces

    # num_player_pieces = game.get_gamelog().get_log_num_player_pieces()
    # print num_player_pieces
    