import sys, time, json, os
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

def parse_pgn_instructions( s
                            ,b_check_schedule=False
                            ,b_capture_schedule=False
                            ,b_mate_turn=False
                            ):
    
    ''' input: s (str)
        return: (list) of tuples( destination
                                 ,piece_class
                                 ,disambig_symbol [or None]
                                 )
        b_check_schedule - returns (list) of bool if opposing player in check
        b_capture_Schedule - returns (list) of bool if capture occurs that move
        b_mate_turn - returns (int) i_turn of checkmate marker 
        [only one b_flag can be set to true at once]
    '''
    
    moves = []
    appendix = []
    mate_i_turn = None

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
                #TODO - exit entire loop, break?
          
            #Appendix
            if b_check_schedule:
                b_check = (_s.find('+') > 0)
                appendix.append(b_check)
                
            if b_capture_schedule:
                b_capture = (_s.find('x') > 0)
                appendix.append(b_capture)

            if b_mate_turn:
                mate_i_turn = cntr
            

            #Castling
            if _s[0] == 'O':
                if _s == 'O-O':
                    m = local_board.get_king_castle_move(_player, left_side=False)
                    triplet = (move_to_pgn_a1(m[1]), 'K', None)
                    moves.append(triplet)
                if _s == 'O-O-O':
                    m = local_board.get_king_castle_move(_player, left_side=True)
                    triplet = (move_to_pgn_a1(m[1]),'K', None)
                    moves.append(triplet)
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
               
                #Disambig is Digit
                if str.isdigit(_s[i_first_digit - 3]):    
                    disambig_info = _s[i_first_digit - 3]
                else:
                    if i_first_digit - 4 >= 0:
                        if str.isdigit(_s[i_first_digit - 4]):
                            disambig_info = _s[i_first_digit - 4]
                
                #Disambig is letter (but not x which is used for capture)
                if str.islower(_s[i_first_digit - 3]):
                    if _s[i_first_digit - 3] != "x":
                        disambig_info = _s[i_first_digit - 3]
                    else:
                        if i_first_digit - 4 >= 0:
                            if str.islower(_s[i_first_digit - 4]):                
                                disambig_info = _s[i_first_digit - 4]

            triplet = (destination_a1, piece_letter, disambig_info)
            
            moves.append(triplet)

    #Return Appendix or Moves
    if b_check_schedule or b_capture_schedule:
        return appendix

    if b_mate_turn:
        return mate_i_turn

    return moves





def alphanum_to_pos(inp):
    col_letters = 'ABCDEFGH'
    #row = int(inp[1]) - 1
    row = 8 - int(inp[1])
    col = col_letters.index(str.upper(inp[0]))
    return (row, col)

def pos_to_alphanum(inp):
    letter_data = 'abcdefgh'
    # number_data = [i+1 for i in range(8)]
    number_data = [i for i in range(8,0,-1)]
    s1 = letter_data[inp[1]]
    s2 = str(number_data[inp[0]])
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
        # if input_type == 'alphanum_legacy':
        #     out = alphamove_to_posmove(raw, b_legacy=True)
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
    
    ''' This handles figuring out the 'move' from PGN info
    
    https://en.wikipedia.org/wiki/Portable_Game_Notation

    Notes
        castling king side: O-O
        castling queen side: O-O-O

        First letter (Capitalized): Piece Class, (ommitted = Pawn)
        [optinal second letter (lower case)]:
        row(letter)column(number)
        Appendix:

            +: checking
            #: checkmating 
            =: promotion [Q / B / N / R]

            ; / {} :comments
    '''

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
    ret, the_move = parse_player_input(instructions[i_turn - 1], board, 'alphanum')
    if ret == 0:
        #TODO - call common return function
        for _m in moves:
            if the_move == (_m.pos0, _m.pos1):
                return Move(_m.pos0, _m.pos1, _m.code)
        return None  # to demonstrate an error in instruction input
    else:
        return None  # to demonstrate an error in instruction input

def moves_to_alphanum(list_inp):
    
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
        ret, the_move = parse_player_input(raw, board, 'alphanum')
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

#Hack for now to avoid circular import reference
from GameLog import GameSchema

def pgn_to_xpgn(pgn_fn
                ,xpgn_fn
                ,pgn_path = '../data/'
                ,xpgn_path = '../data/'
                ,b_silent = False
                ,max_lines = None
                ):
    
    """

    .pgn -> .xpgn { meta-data:
                    {
                        parse-time
                    }
                    data:
                        [
                            { source-id, GameSchema-json {} }
                            { source-id, GameSchema-json {} }
                            ...
                        ]
                    }

    """

    game_schemas = []
    source_keys = []
    
    with open(pgn_path + pgn_fn, 'r') as f:
        lines = f.readlines()

    if max_lines is not None:
        lines = lines[:max_lines]

    #Load data from .pgn
    for i, line in enumerate(lines):
        
        if line[:2] != '1.':
            continue

        #Found an instruction line   
        instr_ind = i
        game_schema = GameSchema()
        game_schema.set_pgn_instructions(line)

        #Find Results line
        try:
            b_result_found = False
            result_ind = i - 2
            result_line = lines[result_ind]
            s_find_result = '[Result'
            if result_line[:len(s_find_result)] == s_find_result:
                quote_inds = [_i for _i,s in enumerate(result_line) if s == '"']
                if len(quote_inds) == 2:
                    b_result_found = True
            
            if b_result_found:
                s_outcome = result_line[quote_inds[0] + 1: quote_inds[1]]
                game_schema.set_pgn_s_outcome(s_outcome)
        except:
            pass

        #Apply ETL on the game_schema, implemented within that class
        game_schema.all_parse_pgn_instructions()
        
        #Load the game_schema into the list
        game_schemas.append(game_schema)

        #Build a source key to identify duplicates
        source_key = pgn_fn + "-" + str(i)
        source_keys.append(source_key)


    #Build up full array of data
    data_list = []
    
    assert len(source_keys) == len(game_schemas)

    for i, gameSchema in enumerate(game_schemas):
            
        data_elem = {}

        data_elem['source-key'] = source_keys[i]
        
        game_schema_dict = json.loads(gameSchema.to_json())
        data_elem['game-schema'] = game_schema_dict
        
        data_list.append(data_elem)

    
    #Top Level Hierachy for xpgn.json
    xpgn_dict = {}

    xpgn_dict['data'] = data_list

    #meta data for parsing here, e.g. commit version
    xpgn_meta = {}
    xpgn_meta['parse-time'] = str(time.time())
    xpgn_dict['meta-data'] = xpgn_meta


    #Writeout
    if not(b_silent):
        with open(xpgn_path + xpgn_fn, 'w') as f:
            json.dump(xpgn_dict, f)

    
    #Return for non filesystem testing
    if b_silent:
        return xpgn_dict

    return None


def test_pgn_to_xpgn_1():
    
    '''verify the output xpgn creation tool'''
    
    #path changed so pytest is called froom root
    
    s_json = pgn_to_xpgn(pgn_fn = 'GarryKasparov.pgn'
                            ,xpgn_fn = 'output1.xpgn'
                            ,pgn_path = 'data/'     
                            ,xpgn_path = 'data/'
                            ,max_lines = 100
                            ,b_silent = True)

    assert s_json.has_key('data')

    assert s_json['data'][0].has_key('source-key')
    
    assert len(s_json['data']) == 6


def test_pgn_to_xpgn_2():
    
    '''Verify file-system transaction here '''

    # test_dir = '../data/tests/' #if run from src/
    test_dir = 'data/tests/'

    target_fn = 'test_dummy_1.xpgn'
    
    fns_before = os.listdir(test_dir)
    
    if target_fn in fns_before:
        print 'first removing file...' + str(target_fn)
        os.remove(test_dir + target_fn)
        assert not(target_fn in os.listdir(test_dir))
    
    ret = pgn_to_xpgn( pgn_fn = 'test_pgn_1.pgn'
                        ,xpgn_fn = target_fn
                        ,pgn_path = test_dir     
                        ,xpgn_path = test_dir                            
                        ,max_lines = 100
                        )

    #Test it got created
    assert target_fn in os.listdir(test_dir)

    #Test the output makes some sense in it
    with open(test_dir + target_fn, 'r') as f:
        lines = f.readlines()

    xpgn_json = json.loads(lines[0])

    assert xpgn_json.has_key('data')

    assert len(xpgn_json['data']) > 0
    

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

def test_pgn_parse_2():
    
    '''This pgn insturction set includes a digit disambig in turn 33'''

    s = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'
    
    out = parse_pgn_instructions(s)

    print out

    assert out == [('f3', 'N', None), ('e6', 'P', None), ('c4', 'P', None), ('b6', 'P', None), ('g3', 'P', None), ('b7', 'B', None), ('g2', 'B', None), ('c5', 'P', None), ('g1', 'K', None), ('f6', 'N', None), ('c3', 'N', None), ('e7', 'B', None), ('d4', 'P', None), ('d4', 'P', 'c'), ('d4', 'Q', None), ('c6', 'N', None), ('f4', 'Q', None), ('g8', 'K', None), ('d1', 'R', None), ('b8', 'Q', None), ('e4', 'P', None), ('d6', 'P', None), ('b3', 'P', None), ('a6', 'P', None), ('b2', 'B', None), ('d8', 'R', None), ('e3', 'Q', None), ('a7', 'Q', None), ('a3', 'B', None), ('f8', 'B', None), ('h3', 'P', None), ('b5', 'P', None), ('a7', 'Q', None), ('a7', 'N', None), ('e5', 'P', None), ('e5', 'P', 'd'), ('f8', 'B', None), ('f8', 'K', None), ('e5', 'N', None), ('g2', 'B', None), ('g2', 'K', None), ('c4', 'P', 'b'), ('c4', 'P', 'b'), ('e8', 'K', None), ('b1', 'R', 'a'), ('d1', 'R', None), ('d1', 'N', None), ('e4', 'N', None), ('b7', 'R', None), ('d6', 'N', None), ('c7', 'R', None), ('c8', 'N', 'a'), ('c5', 'P', None), ('e4', 'N', None), ('f7', 'R', None), ('a7', 'R', None), ('f4', 'R', None), ('f6', 'N', None), ('e3', 'N', None), ('c7', 'R', None), ('c4', 'R', None), ('e7', 'N', None), ('f4', 'P', None), ('c6', 'N', None), ('g4', 'N', '3'), ('d5', 'N', None), ('c6', 'N', None), ('c6', 'R', None), ('f3', 'K', None), ('c7', 'R', None), ('e5', 'N', None), ('d8', 'K', None), ('c6', 'P', None), ('e7', 'K', None), ('a4', 'R', None), ('a7', 'R', None), ('f2', 'K', None), ('d6', 'K', None), ('h4', 'P', None), ('a5', 'P', None), ('f3', 'K', None), ('c3', 'N', None), ('d4', 'R', None), ('d5', 'N', None), ('e4', 'K', None), ('g6', 'P', None), ('g4', 'P', None), ('c7', 'K', None), ('d2', 'R', None), ('a4', 'P', None), ('f5', 'P', None), ('f6', 'N', None), ('f4', 'K', None), ('f5', 'P', 'e'), ('f5', 'P', 'g'), ('a5', 'R', None), ('g6', 'P', 'f'), ('g6', 'P', 'h'), ('b2', 'R', None), ('d5', 'N', None), ('e4', 'K', None), ('b6', 'N', None), ('f2', 'R', None), ('a3', 'P', None), ('f7', 'R', None), ('c8', 'K', None), ('g6', 'N', None), ('a4', 'R', None), ('e5', 'K', None), ('b4', 'R', None), ('e7', 'N', None), ('d8', 'K', None), ('c7', 'P', None), ('e8', 'K', None), ('h7', 'R', None), ('c4', 'R', None), ('d5', 'N', None), ('c5', 'R', None), ('h8', 'R', None), ('d7', 'K', None), ('d8', 'R', None)]

def test_alphanum_legacy_conversion_1():
    
    # assert (6,0) == alphanum_to_pos('g1', b_legacy = True)
    assert (0,6) == alphanum_to_pos('g1')

    # assert (0,4) == alphanum_to_pos('a5', b_legacy = True)
    assert (4,0) == alphanum_to_pos('a5')

    # assert 'd6' == pos_to_alphanum((3,5), b_legacy=True)
    assert 'f4' == pos_to_alphanum((3,5))

    # assert 'h8' == pos_to_alphanum((7,7), b_legacy=True)
    assert 'h8' == pos_to_alphanum((7,7))

def test_alphanum_legacy_conversion_2():
    
    pass
    

if __name__ == "__main__":
    test_printout_to_data_2()