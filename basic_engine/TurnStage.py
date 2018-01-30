import random

from utils import *
from basic import *
from datatypes import moveHolder
Move = moveHolder()

def increment_turn(player, i_turn):
    i_turn += 1
    return not(player), i_turn

def get_available_moves(pieces, board, player):

    moves = []
    for p in pieces:
        if p.white == player:
            
            moves_p = p.get_available_moves(board, move_type_flag = True)
            moves_p = filter(lambda _m: len(_m) > 0, moves_p)
            
            d_moves = [Move(p.pos, _m.pos1, _m.code) for _m in moves_p]
            
            moves.extend(d_moves)
    
    return moves


def check_moves(moves, board, player):
    
    if  len(moves) == 0:
        #TODO - add checkmate detector
        return -1
    else:
        return 0
    


# def apply_move(the_move, the_move_code, board, pieces, _player):
def apply_move(the_move, board, pieces, _player):
    
    the_move_code = the_move.code
    the_move = (the_move.pos0, the_move.pos1)
    
    b_enpassant, b_castling = False, False
    if the_move_code == MOVE_CODE['en_passant']: b_enpassant = True
    if the_move_code == MOVE_CODE['castling']: b_castling = True
                
    pos0,pos1 = the_move[0], the_move[1]
    piece_i = filter(lambda _p: _p[1].pos == pos0, enumerate(pieces))[0][0]

    kill_flag = False   # before the move, check if opp's piece is there
    if (board.data_by_player[pos1[0]][pos1[1]] != 0 or b_enpassant) and \
        not(b_castling):
        kill_flag = True

    
    #Turn-Reset: clear previous before the move is applied
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
        board.old_player_pos(kill_pos)
                
    #TODO - any promotions here    

    return board, pieces

