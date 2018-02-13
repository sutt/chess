import sys
from basic import *
from datatypes import moveHolder
Move = moveHolder()

# example
# 1. e4 d5 2. d3 e5 3. Nf3 dxe4 4. dxe4 Qxd1+ 5. Kxd1 b6 6. Nxe5 Nf6 7. Bb5+ Bd7
# 8. a4 Bxb5 9. axb5 Bd6 10. Nc4 Nh5 11. e5 Kd7 12. exd6 Rg8 *





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





def alphanum_to_pos(inp):
    letter_data = 'ABCDEFGH'
    pos0 = letter_data.index(str.upper(inp[0]))
    pos1 = int(inp[1]) - 1
    return (pos0,pos1)

def pos_to_alphanum(inp):
    letter_data = 'abcdefgh'
    number_data = [i+1 for i in range(8)]
    s1 = letter_data[inp[0]]
    s2 = str(number_data[inp[1]])
    return s1 + s2

def alphamove_to_posmove(inp):
    
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
    if raw == 'out_log':
        return 2, []
    try:
        #TODO - out numeric section
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

#TODO - add return_the_move() for common return function

def instruction_input(board, moves, instructions, i_turn):
    ret, the_move = parse_player_input(instructions[i_turn - 1], board)
    if ret == 0:
        #TODO - call common return function
        for _m in moves:
            if the_move == (_m.pos0, _m.pos1):
                return Move(_m.pos0, _m.pos1, _m.code)
        return None  # to demonstrate an error in instruction input
    else:
        return None  # to demonstrate an error in instruction input

def moves_to_alphanum(list_inp):
    
    # return [(i,v) for i, v in enumerate(list_inp)]
    temp = [
        str(i + 1) +
        ". " +
        pos_to_alphanum(v[0]) +
        " " +
        pos_to_alphanum(v[1]) +
        " "

        for i, v in enumerate(list_inp)
    ]
    
    return "".join(temp)

def format_move_log(inp_move_log):
    '''converts from MoveHolder to tuple for printout'''
    out = [(x.pos0, x.pos1) for x in inp_move_log]
    out = moves_to_alphanum(out)
    return str(out)



def player_control_input(board, moves_player, log, **kwargs):
    
    msg = "Type your move. Or type 'hint' or 'out_log'..."
    msg += "\n"
    while(True):
        raw = raw_input(msg)    #example: >1,1 | 2,2
        ret, the_move = parse_player_input(raw, board)
        if ret == 0:
            #TODO - call common return function
            for _m in moves_player:
                if the_move == (_m.pos0, _m.pos1):
                    return Move(_m.pos0, _m.pos1, _m.code)
            else:
                print 'this move is not legal according to the game engine.'
        if ret == 1: 
            print moves_player
        if ret == 2:
            print format_move_log(log.get_log_move())
        if ret == -1:
            print 'could not recognize move ', str(raw), ". Try again:"