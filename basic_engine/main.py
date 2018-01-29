import sys, random, time

from basic import *
from utils import *
from GameLog import GameLog
from TurnStage import get_available_moves, check_moves, select_move

b_player_control = [True,False]
b_instruction_control = [False,False]


def game(s_instructions = "", **kwargs):

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
            
            #Find all Moves available
            moves_player = get_available_moves(pieces,board,_player)

            #TODO - Filter moves for king in check
            #NOTE - how to get out of check? all moves filtered by king_in_check
            #   but how to handle killing the checking piece?

            #Check for end-game conditions
            check_code = check_moves(moves_player, board, _player)
            if check_code < 0:
                #It's a loss or a stalemate
                game_going = False
                continue

            #Select the Move
            #TODO - this should be self.select_move
            the_move, the_move_code = select_move(moves_player,_player, board, instructions,i_turn
                                        ,b_instruction_control, b_player_control)
            if the_move == -1: return i_turn



                

            #Interpret the Move
            b_enpassant, b_castling = False, False
            if the_move_code == MOVE_CODE['en_passant']: b_enpassant = True
            if the_move_code == MOVE_CODE['castling']: b_castling = True
                        
            pos0,pos1 = the_move[0], the_move[1]
            piece_i = filter(lambda _p: _p[1].pos == pos0, enumerate(pieces))[0][0]

            kill_flag = False   # before the move, check if opp's piece is there
            if (board.data_by_player[pos1[0]][pos1[1]] != 0 or b_enpassant) and \
                not(b_castling):
                kill_flag = True

            #Apply the Move

            #turn-reset: clear previous before the move is applied
            board.clear_enpassant_vulnerability(_player)
            #also "previous check has been cleared (but new check may apply)"

            if not(the_move_code == MOVE_CODE['castling']):
                
                board.old_player_pos(pos0)
                b_two_advances = two_advances(pos0,pos1)   #if its enpassant_vulnerable
                board.new_player_pos(_player, pos1, pieces[piece_i], b_two_advances)
                pieces[piece_i].pos = pos1
            
            else:
                # is it a left castle or a right castle, from POV of white
                castle_absolute_left = True if (KING_COL > pos1[1]) else False
                
                r_pos0, r_pos1 = board.get_rook_castle_move(_player 
                                            ,left_side = castle_absolute_left)
                k_pos0, k_pos1 = board.get_king_castle_move(_player
                                            ,left_side = castle_absolute_left)
                
                rook_i = filter(lambda _p: _p[1].pos == r_pos0, enumerate(pieces))[0][0]
                
                pieces[rook_i].pos = r_pos1   
                pieces[piece_i].pos = k_pos1   #already king
                
                board.new_player_pos(_player, k_pos1, pieces[piece_i])
                board.new_player_pos(_player, r_pos1, pieces[rook_i])


            #Fallout from Move
            pieces[piece_i].modify_castling_property()
            board.modify_castling_property( _player, pieces[piece_i], pos0)


            if kill_flag:
                kill_pos = pos1 if not(b_enpassant) else en_passant_pos(pos1, _player)
                
                killed_piece_i = filter(lambda _p: (_p[1].pos == kill_pos) and 
                                                    not(_p[1].white == _player)
                                        ,enumerate(pieces))
                killed_piece_i = killed_piece_i[0][0]
                pieces[killed_piece_i].alive = False
                dead_pieces.append(pieces.pop(killed_piece_i))
                board.old_player_pos(kill_pos)
                
            #TODO - any promotions here


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
    board = game(s_instructions = ss)
    assert board.data_by_player[7][5] == 1
    assert board.data_by_player[7][6] == 3

def test_castling_disallowed_rook():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h8 h7 8. b4 c4 9. h7 h8 10. b5 c5 11. h5 h7"
    break_turn = game(s_instructions = ss)
    assert break_turn == 11

def test_castling_disallowed_king():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5 11. h5 h7"
    break_turn = game(s_instructions = ss)
    assert break_turn == 11

def test_enpassant_take():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. d2 c3"
    board = game(s_instructions = ss)
    print 'IN TEST'
    board.print_board(b_player_data=True)
    assert board.data_by_player[2][2] == 1
    assert board.data_by_player[3][2] == 0
    

def test_enpassant_disallowed():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. g8 e8 6. b1 c1 7. d2 c3"
    break_turn = game(s_instructions = ss)
    assert break_turn == 7

# if __name__ == "__main__":
#     test_enpassant_take()
#     game()
    # test_castling_disallowed_king()
