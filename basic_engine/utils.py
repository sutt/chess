import sys
from basic import *

# example
# 1. e4 d5 2. d3 e5 3. Nf3 dxe4 4. dxe4 Qxd1+ 5. Kxd1 b6 6. Nxe5 Nf6 7. Bb5+ Bd7
# 8. a4 Bxb5 9. axb5 Bd6 10. Nc4 Nh5 11. e5 Kd7 12. exd6 Rg8 *



#TODO - move this to basic
def en_passant_pos(pos1, _player):
    upwards = -1 if _player else 1
    return (pos1[0] - upwards, pos1[1])

#TODO - move this to basic
def two_advances(pos0, pos1):
    return 2 == abs(pos0[0] - pos1[0])

#TODO - better please
def parse_instructions(s):
    """ input: s, a string 
        return: a list of alphanum-style instructions"""
    
    moves = []

    if len(s) == 0:
        return moves
    
    s2 =s.split(".")
    for _s in s2:
        _s = _s.lstrip()
        _s3 = _s.split(" ")
        if len(_s3) >= 2:
            raw = " ".join([_s3[0],_s3[1]])
            raw = raw.rstrip()
            moves.append(raw)
    return moves


def print_board_letters(board, pieces, b_lower_black = False):
    
    board.start_annotate()
    for p in pieces:
        board.mark_annotate(p, disambiguate = True, b_lower_case = b_lower_black)
    board.print_board(b_annotate = True, b_show_grid = True)    


def alphanum_to_pos(inp):
    letter_data = 'ABCDEFGH'
    pos0 = letter_data.index(str.upper(inp[0]))
    pos1 = int(inp[1]) - 1
    return (pos0,pos1)

def alphamove_to_posmove(inp):
    print inp
    try:
        inputs = inp.split(" ")
        if len(inputs) != 2:
            print 'could not parse alphanumeric move'
        else:
            pos0 = alphanum_to_pos(inputs[0])
            pos1 = alphanum_to_pos(inputs[1])
            return (pos0,pos1)
    except:
        print 'exception while parsing input.'
        return -1
        

def parse_player_input(raw, board, input_type = 'alphanum'):
    ret = -1
    if raw == "hint":
        return 1, []
    try:
        if input_type == 'numeric':
            data = raw.split('|')
            data = [x.split(',') for x in data]
            data = [tuple(map(int,item)) for item in data]
            data = tuple(data)
            if len(data) == 2 and \
            len(data[0]) == 2 and len(data[0]) == 2 and \
            all([ isinstance(data[i][j], int) for i in range(2) for j in range(2)]):
                ret = 0
            else:
                print 'failed to validate properties of move parse output'
        elif input_type == 'alphanum':
            out = alphamove_to_posmove(raw)
            if out == -1:
                return -1,[]
            else:
                ret = 0
                data = out
    except:
        data = []
        print 'failure in routine to parse user input.'
    return ret, data


def instruction_input(board, moves_player, instructions, i_turn):
    ret, the_move = parse_player_input(instructions[i_turn - 1], board)
    if ret == 0:
        for _m in moves_player:
            if the_move == _m[0:2]:
                return (_m[0:2], _m[2])
        return -1,-1  # to demonstrate an error in instruction input
    else:
        return -1,-1  # to demonstrate an error in instruction input

def player_control_input(board, moves_player, **kwargs):
    
    msg = "Type your move. Or type 'hint' to see list of all available moves..."
    msg += "\n"
    while(True):
        raw = raw_input(msg)    #example: >1,1 | 2,2
        ret, the_move = parse_player_input(raw, board)
        if ret == 0:
            for _m in moves_player:
                if the_move == _m[0:2]:
                    return (_m[0:2], _m[2])
            else:
                print 'this move is not legal according to the game engine.'
        if ret == 1: 
            print moves_player
        if ret == -1:
            print 'could not recognize move ', str(raw), ". Try again:"