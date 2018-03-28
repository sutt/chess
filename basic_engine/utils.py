import sys
from basic import *
from datatypes import moveHolder
from Display import Display
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
    
    s_last_move = s_space[::-1][0]
    if len(s_last_move) > 1:
        s_white_move = s_last_move[1]
        if len(s_last_move) > 2:
            s_black_move = s_last_move[2]
        else:
            s_black_move = ''
        s_moves.append( (s_white_move, s_black_move) )

    cntr = 0

    for _tuple_move in s_moves:
        for _s in _tuple_move:
            
            cntr += 1
            _player = bool(cntr % 2)

            _s = _s.lstrip()
            _s = _s.rstrip()

            if _s ==  '':
                continue
                #therefore move is never appended
                #TODO - exit entire loop
                #break? 

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

class PGN:
    
    ''' This handles figuring out the 'move' from PGN info'''

    def __init__(self):
        self.moves = None
        self.s_destination = None
        self.destination = None
        self.piece_class = None
        self.disambig_info = None
        self.pieces = None
        self.moves_destination = None
        self.moves_pc = None
        self.moves_final = None

    def set_moves(self, moves):
        self.moves = moves

    def set_pieces(self, pieces):
        self.pieces = pieces

    @staticmethod
    def pgn_to_pos(s_pgn):
        ''' example e2 -> (6,4) '''
        letters = 'abcdefgh'
        pgn_col = letters.index(s_pgn[0])
        pgn_row = 8 - int(s_pgn[1])
        return (pgn_row, pgn_col)

    def set_destination(self, destination):
        self.destination = self.pgn_to_pos(destination)

    def set_piece_class(self, piece_class):
        self.piece_class = piece_class
    
    def set_disambig_info(self, disambig_info):
        self.disambig_info = disambig_info


    @staticmethod
    def piece_class_from_pos(pieces, pos0):
        '''return first letter (Captialized) of piece name'''
        p = filter(lambda p: p.pos == pos0, pieces)[0]
        p_name = p.__class__.__name__
        p_symbol = p_name[0] if p_name != 'Knight' else "N"
        return p_symbol

    @staticmethod
    def disambig_meaning(_symbol):
        ''' examples: e -> (1, 4), 2 -> (0, 6)'''
        letters = 'abcdefgh'
        if str.isdigit(_symbol):
            row_col = 0     
            val = 8 - int(_symbol)
        else:
            row_col = 1
            val = letters.index(_symbol)
        return (row_col, val)


    def calc_destination(self):
        self.moves_destination = [m for m in self.moves 
                                    if m.pos1 == self.destination]
        
    def calc_piece_class(self):
        self.moves_pc = [m for m in self.moves_destination
                            if self.piece_class == 
                                self.piece_class_from_pos(self.pieces, m.pos0)
                        ]

    def calc_disambig_info(self):
        if self.disambig_info is None:
            self.moves_final = self.moves_pc
        else:
            row_col, val = self.disambig_meaning(self.disambig_info)
        
            self.moves_final = [m for m in self.moves_pc
                                    if m.pos0[row_col] == val]

    def deduce(self):
        ''' continually filter down availables moves - 'moves' - using the
            the three criteria in pgn-instruction-triplet. return as a list
            and verify outside this class. '''
        
        self.calc_destination()     # moves_destination <- moves
        self.calc_piece_class()     # moves_pc <- moves_destination
        self.calc_disambig_info()   # moves_final <- moves_pc

        return self.moves_final     #returning a list of Move


def pgn_deduction(board, pieces, moves, instructions, i_turn):
    
    '''We will build a Move from a pgn-triplet-string here '''

    # print instructions
    instruct = instructions.pop(0)

    pgn = PGN()    
    pgn.set_moves(moves)
    pgn.set_pieces(pieces)
    pgn.set_destination(instruct[0]) 
    pgn.set_piece_class(instruct[1]) 
    pgn.set_disambig_info(instruct[2]) 

    list_final_move = pgn.deduce()
    
    if len(list_final_move) == 1:
        return list_final_move[0]
    else:
        return None  # we couldnt figure out only 1 move from pgn instruct


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


def _find_blank(list_str, find_str):
    return list_str.find(find_str)

def _remove_spaces(list_str):
    return list_str.replace(" ","")

def printout_to_data(s_printout, b_king_can_castle = False):
    ''' output: board, pieces
        input: [multi-line] string of the printout
    converts a printout to a board and pieces data structure'''

    s_blank = "~"

    lines = s_printout.split("\n")
    lines = [_remove_spaces(x) for x in lines]

    #this doesnt work if all rows in leftmost col have pieces
    #or if there are stray blank marks within the string/graphic

    blank_ind = [_find_blank(x, s_blank) for x in lines]
    first_blank = filter(lambda ind: ind[1] >= 0, enumerate(blank_ind))
    top_line = first_blank[0][0]
    left_side = min(filter(lambda ind: ind >= 0, blank_ind))
    
    board_lines = lines[top_line:top_line + 8]
    
    s_board = [line[left_side:left_side + 8] for line in board_lines]
    
    pieces = []
    board = Board()    
    
    for row in range(8):
        for col in range(8):
            
            pos = (row,col)
            s_piece = s_board[row][col]

            if s_piece == "~":
                board.data_by_player[row][col] = 0
                continue
            else:
                
                b_white = s_piece.isupper()
                
                _piece_val = 1

                upper_piece = s_piece.upper()
                
                if upper_piece == "P":
                    _piece = Pawn(b_white = b_white, pos = pos)
                elif upper_piece == "N":
                    _piece = Knight(b_white = b_white, pos = pos)
                elif upper_piece == "B":
                    _piece = Bishop(b_white = b_white, pos = pos)
                elif upper_piece == "R":
                    _piece = Rook(b_white = b_white, pos = pos)
                elif upper_piece == "Q":
                    _piece = Queen(b_white = b_white, pos = pos)
                elif upper_piece == "K":
                    _piece = King(b_white = b_white
                                    ,pos = pos
                                    ,b_can_castle=b_king_can_castle
                                    )
                    _piece_val = 3
                else:
                    print 'could not determine piece in board.'
                    continue
                
                pieces.append(_piece)

                player_mult = 1 if b_white else -1
                by_player_val = player_mult * _piece_val

                board.data_by_player[row][col] = by_player_val

    return board, pieces


def test_printout_to_data_1():
    
    s_test = """
   1 2 3 4 5 6 7 8

A  ~ ~ ~ ~ ~ ~ Q ~
B  ~ ~ ~ ~ ~ ~ ~ ~
C  ~ ~ ~ R ~ ~ ~ B
D  ~ ~ ~ ~ P ~ k ~
E  ~ ~ ~ K ~ ~ ~ ~
F  P ~ ~ ~ ~ ~ ~ ~
G  ~ ~ ~ ~ ~ ~ ~ ~
H  ~ ~ ~ ~ ~ ~ ~ ~
"""
    
    board, pieces = printout_to_data(s_test)

    white_king = filter(lambda p: p.white == True and 
                        p.__class__.__name__ == "King", pieces)[0]
    assert white_king.pos == (4,3)
    
    display = Display()
    display.print_board_letters(pieces)

def test_printout_to_data_2():
    
    '''tests for indenting the printout'''

    s_test = """
    A  ~ ~ ~ ~ ~ ~ Q ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ ~ R ~ ~ ~ B
    D  ~ ~ ~ ~ P ~ k ~
    E  ~ ~ ~ K ~ ~ ~ ~
    F  P ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """
    
    board, pieces = printout_to_data(s_test)

    white_king = filter(lambda p: p.white == True and 
                        p.__class__.__name__ == "King", pieces)[0]
    assert white_king.pos == (4,3)
    
    display = Display()
    display.print_board_letters(pieces)

# def test_printout_to_data_2():
#     """test castline property"""

def test_pgn_parse():

    s = '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7'
    
    out = parse_pgn_instructions(s)

    assert out == [('c4', 'P', None), ('f6', 'N', None), ('c3', 'N', None), ('g6', 'P', None), ('g3', 'P', None), ('c5', 'P', None), ('g2', 'B', None), ('c6', 'N', None), ('f3', 'N', None), ('d6', 'P', None), ('d4', 'P', None), ('d4', 'P', 'c'), ('d4', 'N', None), ('d7', 'B', None), ('g1', 'K', None), ('g7', 'B', None), ('c6', 'N', None), ('c6', 'B', None), ('e4', 'P', None), ('g8', 'K', None), ('e3', 'B', None), ('a6', 'P', None), ('c1', 'R', None), ('d7', 'N', None), ('e2', 'Q', None), ('b5', 'P', None), ('b4', 'P', None), ('e5', 'N', None), ('b5', 'P', 'c'), ('b5', 'P', 'a'), ('b5', 'N', None), ('b5', 'B', None), ('b5', 'Q', None), ('b8', 'Q', None), ('a4', 'P', None), ('b5', 'Q', None), ('b5', 'P', 'a'), ('b8', 'R', 'f'), ('b6', 'P', None), ('g4', 'N', None), ('b7', 'P', None)]

if __name__ == "__main__":
    test_printout_to_data_2()