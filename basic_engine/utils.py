import sys
from basic import *
from datatypes import moveHolder
Move = moveHolder()

# example
# 1. e4 d5 2. d3 e5 3. Nf3 dxe4 4. dxe4 Qxd1+ 5. Kxd1 b6 6. Nxe5 Nf6 7. Bb5+ Bd7
# 8. a4 Bxb5 9. axb5 Bd6 10. Nc4 Nh5 11. e5 Kd7 12. exd6 Rg8 *


# 1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7 


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

def move_to_pgn_a1(move):
    
    move_row, move_col = move[0], move[1]

    letters = 'abcdefgh'
    pgn_a1 = letters[move_col] + str((7 - move_row) + 1)
    return pgn_a1


local_board = Board()

def parse_pgn_instructions(s):
    
    ''' input: s, a string 
        return: a list of tuples( destination
                                 ,piece_class
                                 ,disambig_symbol [or None]
                                 )'''
    
    #TODO 
    #   add in appendix
    #   this cuts off the final move
    
    moves = []

    if len(s) == 0:
        return moves

    s_dot = s.split('.')
    s_space = [x.split(' ') for x in s_dot[1:]]
    s_moves = [(x[1], x[2]) for x in s_space[:-1]]    

    cntr = 0

    for _tuple_move in s_moves:
        for _s in _tuple_move:
            
            cntr += 1
            _player = bool(cntr % 2)

            _s = _s.lstrip()
            _s = _s.rstrip()

            #Castling
            if _s[0] == 'O':
                if _s == 'O-O':
                    m = local_board.get_king_castle_move(_player, left_side=False)
                    triplet = (move_to_pgn_a1(m[1]), 'K', None)
                    moves.append(triplet)
                if _s == 'O-O-O':
                    m = local_board.get_king_castle_move(_player, left_side=True)
                    triplet = (move_to_pgn_a1(m[1]),'K', None)
                    moves.append(m)
                continue
            

            #first digit backwards
            i_first_digit = map(lambda s: str.isdigit(s), _s[::-1] ).index(True)
            i_first_digit =  len(_s) - i_first_digit

            destination_a1 = _s[i_first_digit - 2: i_first_digit ]

            #Verify destination
            if (len(destination_a1) != 2 ):
                print 'Not 2!'

            #Piece 
            piece_letter = _s[0] if str.isupper(_s[0]) else "P"

            #Disambiguating Info
            disambig_info = None
            
            if i_first_digit - 3 >= 0:
                if str.islower(_s[i_first_digit - 3]):
                    
                    if _s[i_first_digit - 3] != "x":
                    
                        disambig_info = _s[i_first_digit - 3]
                    
                    else:
                        
                        if i_first_digit - 4 >= 0:
                            if str.islower(_s[i_first_digit - 4]):
                                
                                disambig_info = _s[i_first_digit - 4]

            triplet = (destination_a1, piece_letter, disambig_info)
            
            moves.append(triplet)

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
        if input_type == 'alphanum':
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

def pgn_deduction(board, moves, instructions, i_turn):
    pass
    # #----------------------------
    # pgn.set_moves(moves)
    # pgn.set_destination(instruct[0]) 
    # pgn.set_piece_class(instruct[1]) 
    # pgn.set_disambig_info(instruct[2]) 

    # filtered_move = pgn.deduce()
    # moves_destination = filter(lambda m: m.pos1 == pos_destination)

    # moves_piece = filter(lambda m: piece_from_pos(m) == piece_class, moves_destination)

    # if disambig_info is not None:
    #     moves_disambig = filter(lambda: x, pos_to_alphanum )
    # else:
    #     moves_disambig = moves_piece
    # #---------------------------------------
        
    # if len(filtered_move) == 1:
        
    #     the_move = filtered_move[0]
    #     for _m in moves:
    #         if the_move == (_m.pos0, _m.pos1):
    #             return Move(_m.pos0, _m.pos1, _m.code)
    #     return None  # to demonstrate an error in instruction input
    # else:
    #     return None  # to demonstrate an error in instruction input


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


def test_pgn_parse():

    s = '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7'
    
    out = parse_pgn_instructions(s)

    assert out == [('c4', 'P', None), ('f6', 'N', None), ('c3', 'N', None), ('g6', 'P', None), ('g3', 'P', None), ('c5', 'P', None), ('g2', 'B', None), ('c6', 'N', None), ('f3', 'N', None), ('d6', 'P', None), ('d4', 'P', None), ('d4', 'P', 'c'), ('d4', 'N', None), ('d7', 'B', None), ('g1', 'K', None), ('g7', 'B', None), ('c6', 'N', None), ('c6', 'B', None), ('e4', 'P', None), ('g8', 'K', None), ('e3', 'B', None), ('a6', 'P', None), ('c1', 'R', None), ('d7', 'N', None), ('e2', 'Q', None), ('b5', 'P', None), ('b4', 'P', None), ('e5', 'N', None), ('b5', 'P', 'c'), ('b5', 'P', 'a'), ('b5', 'N', None), ('b5', 'B', None), ('b5', 'Q', None), ('b8', 'Q', None), ('a4', 'P', None), ('b5', 'Q', None), ('b5', 'P', 'a'), ('b8', 'R', 'f'), ('b6', 'P', None), ('g4', 'N', None)]