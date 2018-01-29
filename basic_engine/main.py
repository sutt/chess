import sys, random, time

from basic import *
from utils import *
from GameLog import GameLog
from TurnStage import get_available_moves, check_moves, select_move, apply_move

b_player_control = [True,False]
b_instruction_control = [False,False]

class Game():
    
    def __init__(self,**kwargs):
        pass


    def play(self,s_instructions = "", **kwargs):

        #INIT Board and pieces
        board = Board()
        board, pieces = place_pieces(board)
        dead_pieces = []

        instructions = parse_instructions(s_instructions)
        log = GameLog()

        game_going = True
        i_turn = 0

        print_board_letters(board, pieces, True)

        #Turn Loop
        while(game_going):
            
            #TODO this is a counter-mod, not a for-loop
            for _player in (True,False):
                
                i_turn += 1
                
                moves_player = get_available_moves(pieces,board,_player)

                #TODO - Filter moves for king in check
                #NOTE - how to get out of check? all moves filtered by king_in_check
                #   but how to handle killing the checking piece?

                check_code = check_moves(moves_player, board, _player)
                if check_code < 0:
                    #It's a loss or a stalemate
                    game_going = False
                    continue

                #TODO - this should be self.select_move
                the_move, the_move_code = select_move(moves_player,_player
                                            ,board, instructions,i_turn
                                            ,b_instruction_control
                                            ,b_player_control)

                if the_move == -1: return i_turn

                #Apply the Move
                board, pieces, dead_pieces, kill_flag, pos0, pos1 = apply_move(the_move,the_move_code,board, pieces, dead_pieces, _player)
                
                #Log / Record the Move
                log.moves_log.append(the_move)

                log.print_turn(  board = board
                                ,pieces = pieces
                                ,dead_pieces = dead_pieces
                                ,kill_flag = kill_flag
                                ,pos0 = pos0
                                ,pos1 = pos1
                                )

                #Exit from main for predefined instructions
                if any(b_instruction_control):    
                    if i_turn == len(instructions):
                        game_going = False
                        return board

        log.log_game()


if __name__ == "__main__":
    game()

b_instruction_control = [True,True]

def test_castling_allowed():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h7"
    game = Game()
    board = game.play(s_instructions = ss)
    assert board.data_by_player[7][5] == 1
    assert board.data_by_player[7][6] == 3

def test_castling_disallowed_rook():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h8 h7 8. b4 c4 9. h7 h8 10. b5 c5 11. h5 h7"
    game = Game()
    break_turn = game.play(s_instructions = ss)
    assert break_turn == 11

def test_castling_disallowed_king():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5 11. h5 h7"
    game = Game()
    break_turn = game.play(s_instructions = ss)
    assert break_turn == 11

def test_enpassant_take():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. d2 c3"
    game = Game()
    board = game.play(s_instructions = ss)
    board.print_board(b_player_data=True)
    assert board.data_by_player[2][2] == 1
    assert board.data_by_player[3][2] == 0
    

def test_enpassant_disallowed():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. g8 e8 6. b1 c1 7. d2 c3"
    game = Game()
    break_turn = game.play(s_instructions = ss)
    assert break_turn == 7

# if __name__ == "__main__":
#     test_castling_disallowed_king()
