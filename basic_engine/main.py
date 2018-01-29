import sys, random, time
from basic import *
from utils import *
from GameLog import GameLog

b_player_control = [True,True]
b_instruction_control = [False,False]


def game(**kwargs):

    #INIT Board and pieces
    board = Board()
    board, pieces = place_pieces(board)

    instructions = []
    s_instructions = kwargs.get('instructions',"")
    if len(s_instructions) > 0:
        instructions = parse_instructions(s_instructions)
        print instructions
        
    game_going = True
    i_turn = 0
    log = GameLog()
    dead_pieces = []

    print_board_letters(board, pieces, True)

    while(game_going):
        
        for _player in (True,False):
            
            i_turn += 1
            
            #Find all Moves available
            moves_player = []
            for p in pieces:
                if p.white == _player:
                    
                    moves_p = p.get_available_moves(board, move_type_flag = True)
                    moves_p = filter(lambda _m: len(_m) > 0, moves_p)
                    
                    current_pos = p.pos
                    d_moves_p = [(current_pos,_move[0],_move[1]) for _move in moves_p]
                    
                    moves_player.extend(d_moves_p)

            #TODO - Filter moves for king in check
            
            if log.all_moves: print moves_player

            #Check for end-game conditions
            num_moves = len(moves_player)
            if  num_moves == 0:
                game_going = False
                print 'Player ', str(board.player_name_from_bool(_player)), ' has no moves available. Game over.'
                #TODO - add checkmate detector
                continue
            else:
                if log.num_moves: print "Player: ", str(_player), " has num moves: ", str(num_moves)

            #Select the Move
            if b_instruction_control[1 - int(_player)]:
                #Predefined instructions
                the_move, the_move_code = instruction_input(board, moves_player, instructions, i_turn)
                if the_move == -1: return i_turn
            elif b_player_control[1 - int(_player)]:
                #Manual
                the_move, the_move_code = player_control_input(board, moves_player)
            else:
                #Random
                move_i = random.sample(range(0,num_moves),1)[0]
                the_move = moves_player[move_i][0:2]
                the_move_code = moves_player[move_i][2] 
                

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


            #clear previous before the move is applied
            board.clear_enpassant_vulnerability(_player)

            #Apply the Move
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

            

        if log.proc: print 'new turn...'

        if i_turn == 15:
            break

        

    print 'game over.'


# if __name__ == "__main__":
#     game()

b_instruction_control = [True,True]

def test_castling_allowed():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h7"
    board = game(instructions = ss)
    assert board.data_by_player[7][5] == 1
    assert board.data_by_player[7][6] == 3

def test_castling_disallowed_rook():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h8 h7 8. b4 c4 9. h7 h8 10. b5 c5 11. h5 h7"
    break_turn = game(instructions = ss)
    assert break_turn == 11

def test_castling_disallowed_king():
    
    ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5 11. h5 h7"
    break_turn = game(instructions = ss)
    assert break_turn == 11

def test_enpassant_take():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. d2 c3"
    board = game(instructions = ss)
    print 'IN TEST'
    board.print_board(b_player_data=True)
    assert board.data_by_player[2][2] == 1
    assert board.data_by_player[3][2] == 0
    

def test_enpassant_disallowed():
    
    ss = "1. g2 e2 2. b8 c8 3. e2 d2 4. b3 d3 5. g8 e8 6. b1 c1 7. d2 c3"
    break_turn = game(instructions = ss)
    assert break_turn == 7

if __name__ == "__main__":
    test_enpassant_take()
    game()
