import random

from utils import *
from basic import *


def get_available_moves(pieces, board, player):

    moves = []
    for p in pieces:
        if p.white == player:
            
            moves_p = p.get_available_moves(board, move_type_flag = True)
            moves_p = filter(lambda _m: len(_m) > 0, moves_p)
            
            d_moves_p = [(p.pos,_move[0],_move[1]) for _move in moves_p]
            
            moves.extend(d_moves_p)
    
    return moves

def check_moves(moves, board, player):
    
    num_moves = len(moves)
    if  num_moves == 0:
        game_going = False
        print 'Player ', str(board.player_name_from_bool(player)), ' has no moves available. Game over.'
        #TODO - add checkmate detector
    else:
        pass
        #if log.num_moves: print "Player: ", str(_player), " has num moves: ", str(num_moves))
    
    return 1

#TODO this should be a function of game to use self.propA, etc.
#TODO this should include check and checkmate logging
def select_move(moves, player,board, instructions, i_turn, b_instruction_control, b_player_control ):

    if b_instruction_control[1 - int(player)]:
        #Predefined instructions
        the_move, the_move_code = instruction_input(board, moves, instructions, i_turn)
    elif b_player_control[1 - int(player)]:
        #Manual
        the_move, the_move_code = player_control_input(board, moves)
    else:
        #Random
        num_moves = len(moves)
        move_i = random.sample(range(0,num_moves),1)[0]
        the_move = moves[move_i][0:2]
        the_move_code = moves[move_i][2] 
    
    return the_move, the_move_code

