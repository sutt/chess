import sys, random, time

from basic import *
from utils import *
from datatypes import moveHolder
from GameLog import GameLog
from Display import Display
from TurnStage import increment_turn, get_available_moves, apply_move
from TurnStage import check_endgame
from TurnStage import filter_king_check
from TurnStage import is_king_in_check
from TurnStage import filter_king_check_test_copy   #temp
from TurnStage import filter_king_check_test_copy_apply   #temp
from TurnStage import filter_king_check_optimal   #emp
from TurnStage import filter_king_check_optimal_2   #temp
from TurnStage import filter_king_check_test_copy_apply_2   #temp
from TurnStage import filter_king_check_test_copy_apply_3   #temp
from TurnStage import filter_king_check_test_copy_apply_4   #temp

Move = moveHolder()

class Game():
    
    def __init__(
        self
        ,manual_control = () 
        ,instruction_control = () 
        ,pgn_control = ()
        ,s_instructions = ""
        ,s_pgn_instructions = ""
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
        ):

        self.manual_control = manual_control
        self.instructions = parse_instructions(s_instructions)
        self.instruction_control = instruction_control 
        if len(self.instructions) > 0:
            self.instruction_control = (0,1)
        
        self.pgn_control = pgn_control
        self.pgn_instructions = parse_pgn_instructions(s_pgn_instructions)
        if len(self.pgn_instructions) > 0:
            self.pgn_control = (0,1)

        self.i_turn = 0
        
        self.b_test_exit = False
        self.test_data = None
        self.test_exit_iturn = test_exit_moves

        self.outcome = None

        self.init_player = init_player
        self.init_board = copy.deepcopy(init_board)
        self.init_pieces = copy.deepcopy(init_pieces)

        self.display = Display(b_show_opponent = b_display_show_opponent
                               ,b_never_print = b_display_never_print
                               ,b_always_print = b_display_always_print
                               ,manual_control = self.manual_control
                               )

        self.log = GameLog(manual_control = self.manual_control
                          ,b_log_move = b_log_move
                          ,b_turn_time = b_log_turn_time
                          ,b_num_available = b_log_num_available
                           )
        
    def get_gamelog(self):
        return self.log


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
        return False
        
    
    def select_move(self, moves, player, pieces, board): 
    
        if int(player) in self.instruction_control:
            move = instruction_input(board, moves, self.instructions, self.i_turn)
        elif int(player) in self.manual_control:
            move = player_control_input(board, moves, self.log)
        elif int(player) in self.pgn_control:
            move = pgn_deduction(board, pieces, moves, self.pgn_instructions, self.i_turn)
        else:
            move_i = random.sample(range(0,len(moves)),1)[0]
            move = moves[move_i]
        return move



    def play(self, **kwargs):

        board = Board()
        
        if self.init_board is not None:
            board.set_data(self.init_board)     #init_board represent data_by_player
            pieces = self.init_pieces
        else:
            board, pieces = place_pieces(board)
        
        #These incremetent at top-of-turn-loop
        self.i_turn = 0
        player = False 
        if self.init_player is not None:
            player = not(self.init_player)

        game_going = True
        
        while(game_going):
            
            if self.b_test_exit:
                return self.test_data
            
            player, self.i_turn = increment_turn(player, self.i_turn)

            b_player_in_check = is_king_in_check(board, pieces, player)
            board.set_player_in_check(player, b_player_in_check)

            moves = get_available_moves(pieces, board, player)

            if kwargs.get('king_in_check_on', False):
                moves = filter_king_check(board, pieces, moves, player)
            if kwargs.get('king_in_check_test_copy', False):
                moves = filter_king_check_test_copy(board, pieces, moves, player)
            if kwargs.get('king_in_check_test_copy_apply', False):
                moves = filter_king_check_test_copy_apply(board, pieces, moves, player)
            if kwargs.get('king_in_check_test_copy_apply_2', False):
                moves = filter_king_check_test_copy_apply_2(board, pieces, moves, player)
            if kwargs.get('king_in_check_test_copy_apply_3', False):
                moves = filter_king_check_test_copy_apply_3(board, pieces, moves, player)
            if kwargs.get('king_in_check_test_copy_apply_4', True):
                moves = filter_king_check_test_copy_apply_4(board, pieces, moves, player)
            if kwargs.get('king_in_check_optimal', False):
                moves = filter_king_check_optimal(board, pieces, moves, player)
            if kwargs.get('king_in_check_optimal_2', False):
                moves = filter_king_check_optimal_2(board, pieces, moves, player)
            
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
                        
            self.log.add_turn_log(move, len(moves))

            if self.check_test_exit():
                self.b_test_exit = True
                self.test_data = {}
                self.test_data['pieces'] = copy.deepcopy(pieces)
                self.test_data['board'] = copy.deepcopy(board)
                continue

        #True exit: only here when check_endgame has been satisfied
        return self.outcome, board, pieces


def test_castling_allowed_misc():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h7"
    game = Game(s_instructions = ss)
    board = game.play()
    board = board['board']
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
    board = board['board']
    # board.print_board(b_player_data=True)
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

    ss_post_castling = "1. h7 f8 2. b8 c8 3. g5 e5 4. b1 d1 5. h6 f4 6. b2 c2 7. h5 h7 8. a8 b8 9. h6 h5 10. a7 c6"    
    game = Game(s_instructions = ss_post_castling)
    board = game.play()
    board = board['board']
    assert board.data_by_player[7][4] == 1
    assert board.data_by_player[7][5] == 0

def test_player_in_and_out_of_check():
    
    #Black is checked on 7th move
    ss = "1. g4 e4 2. b5 d5 3. h2 f1 4. d5 e4 5. h4 e4 6. b8 d8 7. e4 e5 8. a6 b5 9. e5 d5 10. b1 c1"
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
    ss = "1. h7 f8 2. b4 d4 3. g5 e5 4. a4 c4 5. h6 f4 6. b1 d1 7. e5 d5 8. c4 d5 9. h5 h7 10.g1 e1"
    game = Game(s_instructions = ss)
    exit_turn = game.play()
    assert exit_turn == 9

def test_castling_disallowed_into_check():  

    #Black queen has King-Castling destination in check on turn 8, try to castle turn 9
    ss = "1. h7 f8 2. b4 d4 3. g5 e5 4. a4 c4 5. h6 e3 6. c4 f7 7. g1 e1 8. f7 g7 9. h5 h7 10. g2 e2"
    game = Game(s_instructions = ss)
    exit_turn = game.play()
    assert exit_turn == 9  

def test_castling_disallowed_when_dead():
    
    #Setup
    ss = '1. h2 f3 2. b2 d2 3. g4 e4 4. d2 e2 5. h3 f5 6. e2 f3 7. h4 f4 8. f3 g2'

    #Turn 10 capture rook, Turn 11 Castle
    ss = '1. h2 f3 2. b2 d2 3. g4 e4 4. d2 e2 5. h3 f5 6. e2 f3 7. h4 f4 8. f3 g2 9. g8 e8 10. g2 h1 11. h5 h3 12. b8 d8'
    
    game = Game(s_instructions = ss)
    exit_turn = game.play()
    assert exit_turn == 11

def test_promotion_on_advance():
    
    #Test for pawn gone
    #Test for queen there
    #Test for putting king in check with promoted piece

    #pawn promoted causing check
    ss = '1. g1 e1 2. b2 d2 3. e1 d2 4. b4 d4 5. d2 c2 6. a3 c1 7. c2 b3 8. a4 c4 9. b3 a3 10. b8 d8'

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
    ret_data2a = game2a.play(king_in_check_test_copy_apply_4 = False
                            ,king_in_check_on = True
                            )
    generic_check_moves = ret_data2a['moves']

    #2b - "Opt": Computationally cheap, but incorrect result
    game2b = Game(init_board = copy.deepcopy(my_board.data_by_player)
                ,init_pieces = copy.deepcopy(my_pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )
    ret_data2b = game2b.play(king_in_check_test_copy_apply_4 = True
                            ,king_in_check_on = False
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

if __name__ == "__main__":

    test_filter_check_pawn_1()

    # Interactive Setup
    # game = Game(manual_control = (0,1)
    #             ,b_display_show_opponent = True
    #             ,b_log_move = True
    #             )
    # game.play()

    
    #PGN Setup
    
    #a kasparov game
    # ss_pgn = '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7 '

    # My game witha  promotion on turn ~95, breaks turn 97?
    ss_pgn = "1. e4 Nh6 2. d4 c5 3. c3 g6 4. Nf3 Ng4 5. h3 d5 6. hxg4 dxe4 7. Nfd2 e3 8. fxe3 cxd4 9. cxd4 Bxg4 10. Qxg4 f6 11. Qe4 Qd6 12. Qxb7 Qg3+ 13. Kd1 a5 14. Qxa8 Bg7 15. Ne4 Qc7 16. Bb5+ Kf7 17. Nbc3 Qb6 18. Qd5+ Qe6 19. Bc4 Qxd5 20. Bxd5+ e6 21. Nd6+ Ke7 22. Nde4 g5 23. Bb3 Kf8 24. Rf1 Nc6 25. Nxf6 Nb4 26. Nxh7+ Ke8 27. Nxg5 e5 28. Bf7+ Kd7 29. dxe5 Rh2 30. e6+ Kd8 31. a3 Bxc3 32. axb4 Bxb4 33. Bd2 Bxd2 34. Kxd2 Rxg2+ 35. Kd3 Rxg5 36. Rfd1 Rd5+ 37. Ke2 Rxd1 38. Rxd1+ Ke7 39. Rd7+ Kf6 40. e4 a4 41. Ke3 Kg7 42. e5 Kf8 43. Rd8+ Kg7 44. Kd4 a3 45. bxa3 Kh6 46. e7 Kh7 47. e8=Q Kh6 48. Rd6+ Kg5 49. Qg8+ Kf4 50. Qh8 Kf3 51. Qh5+ Kf2 52. Rf6+ Kg2 53. Qf3+ Kg1 54. Qf2+ Kh1 55. Rh6# 1-0"
    
    #Heres where the problems start...Kf4 (for black) isn't available from my in_check() module. Prolly because it sees pawn diagonally attacking backwards?
    #47. e8=Q Kh6 48. Rd6+ Kg5 49. Qg8+ ... !!! Kf4 !!! 50. Qh8 Kf3 51. Qh5+ Kf2 52. Rf6+ Kg2 53. Qf3+ Kg1 54. Qf2+ Kh1 55. Rh6# 1-0"

    # game = Game(s_pgn_instructions = ss_pgn
    #             ,pgn_control = (0,1)
    #             ,b_log_move = True
    #             ,test_exit_moves = 110
    #             ,b_display_always_print = True
    #             )
    # ret = game.play()
    # print ret
    
    #Printout a game to observe it
    # ss_long = '1. g1 e1 2. b1 d1 3. g2 e2 4. b3 d3 5. e2 d3 6. b6 d6 7. g5 e5 8. a2 c3 9. h4 d8 10. b7 c7 11. h6 c1 12. a1 c1 13. h1 f1 14. a6 c8 15. h7 f6 16. b2 d2 17. h3 g2 18. a5 a6 19. e1 d2 20. c8 d7 21. d8 c7 22. d7 e6 23. h5 h7 24. b8 c8 25. g3 e3 26. e6 b3 27. g7 e7 28. c3 e4 29. c7 b7 30. a6 a5 31. b7 c7 32. c1 c7 33. d2 c2 34. b4 d4 35. f6 e4 36. d6 e5 37. h2 f3 38. c8 d8 39. f1 d1 40. c7 c4 '            
    # game = Game(s_instructions = ss_long
    #         ,test_exit_moves = None
    #         ,b_display_show_opponent = True
    #         ,b_log_move = True
    #         )

    # game.play(king_in_check_on=False, king_in_check_test_copy_apply_4=True)
    