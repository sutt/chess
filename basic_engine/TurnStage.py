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

def get_possible_check(pieces, board, player):
    
    moves = []
    for p in pieces:
        if p.white == player:
            
            b_check = p.get_available_moves(board
                                            ,move_type_flag = True
                                            ,check_flag = True)
            
            if b_check:
                return True
    
    return False    #no checks found


def check_endgame(moves, pieces, board, player):
    
    check_code = 0
    outcome = None

    if len(moves) == 0:
    
        if board.b_in_check(player):
            outcome = (player, 'LOSS', 'CHECKMATE')
            check_code = -1
        else:    
            outcome = (player, 'STALEMATE', 'NOMOVES')
            check_code = -2
    
    elif board.player_only_king_moves[1 - int(player)] == 50:   #TODO - player_i(player)
        outcome = (player, 'WIN', '50MOVES')
        check_code = -3

    elif len(pieces) <= 3:
        
        if len(pieces) == 2:
            
            outcome = (player, 'STALEMATE', 'KINGVKING')
            check_code = -4

        else:
            
            white_pieces = filter(lambda p: p.white,  pieces)
            black_pieces = filter(lambda p: not(p.white),  pieces)
            
            b_white_more = len(white_pieces) > len(black_pieces)

            more_pieces = white_pieces if b_white_more else black_pieces
            
            more_piece_names = map(lambda p: p.__class__.__name__, more_pieces)

            alive_pieces =  ("Pawn", "Queen", "Rook")
            
            alives_in_more = map(lambda ap: ap in more_piece_names, alive_pieces)

            if not(any(alives_in_more)):
                outcome = (player, 'STALEMATE', 'NOQUEENPAWNROOK')

            # king versus king
            # king and bishop versus king
            # king and knight versus king
            
            # TODO - # king and bishop versus king and bishop with the bishops on the same colour.
            
    
    return check_code, outcome
    


def apply_move(move, board, pieces, _player):
    
    '''This mutates board and pieces based on move. 
        Mutator Class can handle half-turn ahead board/piece mutations on 
        regular move codes, but this function can handle the exotic moves:
        enpassant, castling, promotion. And also sets/clears the permission
        properties to allow these moves.'''

    move_code = move.code
    move = (move.pos0, move.pos1)

    b_enpassant = (move_code == MOVE_CODE['en_passant'])
    b_castling = (move_code == MOVE_CODE['castling'])
                
    pos0, pos1 = move[0], move[1]

    #TODO - add helper func: piece_from_pos( index_=True)
    piece_i = filter(lambda _p: _p[1].pos == pos0, enumerate(pieces))[0][0]
    #TODO - piece = pieces[piece_i]

    kill_flag = False   # before the move, check if opp's piece is there
    if (board.get_data_pos(pos1) != 0 or b_enpassant) and not(b_castling):
        kill_flag = True

    #Turn-Reset: clear previous before the move is applied
    board.clear_enpassant_vulnerability(_player)

    if not(b_castling):
        
        board.old_player_pos(pos0)
        
        b_two_advances = board.two_advances(pos0,pos1)   #bool: will it be enpassant_vuln?
        
        board.new_player_pos(_player, pos1, pieces[piece_i], b_two_advances)
        
        pieces[piece_i].pos = pos1
    
    else:

        # is it a left castle or a right castle, from POV of white
        castle_absolute_left = True if (KING_COL > pos1[1]) else False
        
        r_pos0, r_pos1 = board.get_rook_castle_move(_player 
                                    ,left_side = castle_absolute_left)

        k_pos0, k_pos1 = board.get_king_castle_move(_player
                                    ,left_side = castle_absolute_left)
        
        #TODO - helper func
        rook_i = filter(lambda _p: _p[1].pos == r_pos0, enumerate(pieces))[0][0]

        pieces[rook_i].pos = r_pos1   
        pieces[piece_i].pos = k_pos1   #piece_i already king
        
        board.new_player_pos(_player, k_pos1, pieces[piece_i])
        board.new_player_pos(_player, r_pos1, pieces[rook_i])

        board.old_player_pos(k_pos0)
        board.old_player_pos(r_pos0)


    #Fallout from Move
    pieces[piece_i].modify_castling_property()
    board.modify_castling_property( _player, pieces[piece_i], pos0)

    if kill_flag:
        
        kill_pos = pos1 if not(b_enpassant) else board.en_passant_pos(pos1, _player)
        
        #TODO - helper func
        killed_piece_i = filter(lambda _p: (_p[1].pos == kill_pos) and 
                                            not(_p[1].white == _player)
                                ,enumerate(pieces))
        killed_piece_i = killed_piece_i[0][0]

        #TODO - don't pop piece in hypothetical_pieces=True
        # pieces[killed_piece_i].alive = False
        killed_piece = pieces.pop(killed_piece_i)
        board.modify_castling_property( not(_player), killed_piece, killed_piece.pos)
        
        if (b_enpassant):
            board.old_player_pos(kill_pos)    
            #otherwise, you already overwrote it's position on board
                
    #TODO - any promotions here    

    # Unnec as it sets and acted upon at beginning of turn, 
    # still nice to have it always being reset here.
    board.set_player_not_in_check(_player)   #based on previous validations

    return board, pieces

    
class Mirror():

    '''This handles the data and calculation of check from 
    superking.available_moves. It builds an increasingly large
    and informative tuples within a list entered. 
    run_calc() answers the question is the piece at init_pos
    threatened by capture of any other piece '''

    def __init__(self):
        self.init_pos = None
        self.moves = None
        self.pieces = None

        self.move_types = None
        self.piece_classes = None        
        self.move_spaces = None
        self.class_move_types = None

        self.outcome = None

    def set_init_pos(self, init_pos):
        self.init_pos = init_pos

    def set_moves(self, moves):
        self.moves = moves
        # move_code enpassant and castling not applicable here, only regular captures

    def set_pieces(self, pieces):
        self.pieces = pieces
        # does this create a problem with byref for pieces list?

    @staticmethod
    def get_piece_class(pieces, pos):
        piece = filter(lambda piece: piece.pos == pos, pieces)[0]
        return piece.__class__.__name__

    def infer_move_type(self, move):
        # none of the three atomic move types overlap, thus deduce the
        # move-type from the (pos0, pos1).

        pos0 = self.init_pos
        pos1 = move
        
        row0, row1 = pos0[0], pos1[0]
        col0, col1 = pos0[1], pos1[1]
        
        if (row0 == row1) or (col0 == col1):
            return MOVE_TYPE['upacross']
        elif abs(row0 - row1) == abs(col0 - col1):
            return MOVE_TYPE['diagonal']
        else:
            return MOVE_TYPE['twobyone']

    @staticmethod
    def chess_squares(pos0, pos1):
        return max(abs(pos0[0] - pos1[0]), abs(pos0[1] - pos1[1]))
        # meaningless but relevant to knight downstream

    @staticmethod
    def class_movements(_class):
        #or make this reflective?
        #TODO - remove hard coded 8's
        if _class == "Pawn":
            return [(MOVE_TYPE['diagonal'], 1)]
        if _class == "King":
            return [(MOVE_TYPE['diagonal'], 1), (MOVE_TYPE['upacross'], 1)]
        if _class == "Queen":
            return [(MOVE_TYPE['diagonal'], 8), (MOVE_TYPE['upacross'], 8)]
        if _class == "Bishop":
            return [(MOVE_TYPE['diagonal'], 8)]
        if _class == "Rook":
            return [(MOVE_TYPE['upacross'], 8)]
        if _class == "Knight":
            return [(MOVE_TYPE['twobyone'], 2)] #2 needed to satisfy max_spaces in match()

    def calc_move_type(self):
        self.move_types = [self.infer_move_type(x) for x in self.moves]

    def calc_classes(self):
        #using pos to find piece
        #right now it uses pieces, later it may have to use board
        self.piece_classes = [self.get_piece_class(self.pieces, x) for x in self.moves]

    def calc_move_spaces(self):
        self.move_spaces = [self.chess_squares(self.init_pos, x) for x in self.moves]

    def calc_class_move_types(self):
        self.class_move_types = [self.class_movements(x) for x in self.piece_classes]

    
    @staticmethod
    def match(class_move_type, move_type, move_space):
        
        temp_class_move_type = map(lambda x: x[0], class_move_type)

        if move_type in temp_class_move_type:  

            max_spaces_ind = temp_class_move_type.index(move_type)
            
            max_spaces = class_move_type[max_spaces_ind][1]
            
            if move_space <= max_spaces:                
                return True
            
            # need this below if max_spaces for knight is not hard-coded to 2
            # if move_type == MOVE_TYPE['twobyone']:
            #     return True

        return False
        

    def calc_match(self):
        self.outcome = [self.match(self.class_move_types[i]
                                   ,self.move_types[i]
                                   ,self.move_spaces[i]
                                   )
                        for i in range(len(self.moves))
                        ]

    def run_calc(self):

        self.calc_move_spaces()
        self.calc_classes()
        self.calc_class_move_types()
        self.calc_move_type()       

        self.calc_match()
        return any(self.outcome)



def get_possible_check_optimal(pieces, board, move, player):
    
    ''' An optimized substitute for get_possible_check() (the niave func).
        It uses the SuperKing.get_available_moves(mirror_flag = True) 
        to see if any other piece possibly move in a way to caputre it.
        Then Mirror class to see if any of those threats is capable.'''

    #Helper func: piece_by_class_player
    player_king = filter(lambda p: p.white == player and p.__class__.__name__ == "King" , pieces)
    
    player_king_pos = player_king[0].pos 

    if move is not None:    #when calling at beginning of turn
        if player_king_pos == move.pos0:
            player_king_pos = move.pos1

    player_king_code = 3 if player else -3

    hypo_king = SuperKing(b_white = player,pos = player_king_pos )

    opp_kill_moves = hypo_king.get_available_moves(board
                                                  ,move_type_flag=True
                                                  ,check_flag=False
                                                  ,mirror_flag=True
                                                  )
                                                  
    if len(opp_kill_moves) == 0:
        return False        #optimization, bypass next section

    mirror = Mirror()   
    
    mirror.set_init_pos(player_king_pos)
    mirror.set_moves(opp_kill_moves)
    mirror.set_pieces(pieces)
    
    b_check = mirror.run_calc()

    return b_check



def filter_king_check_optimal_2(board, pieces, moves, player):
    
    out = []
    
    for _move in moves:

        #cant these just move outside the loop?
        #The problem is apply_move mutates state piece, right?
        _board = copy.deepcopy(board)   
        _pieces = copy.deepcopy(pieces)

        board2, pieces2 = apply_move(_move, _board, _pieces, player)

        b_check = get_possible_check_optimal(pieces2, board2, _move, player)
        
        if not(b_check):
            out.append(_move)

    return out


def filter_king_check_optimal(board, pieces, moves, player):
    
    out = []
    
    for _move in moves:

        #cant these just move outside the loop?
        #The problem is apply_move mutates state piece, right?
        _board = copy.deepcopy(board)   
        _pieces = copy.deepcopy(pieces)

        board2, pieces2 = apply_move(_move, _board, _pieces, player)

        b_check = get_possible_check_optimal(pieces2, board2, _move, player)
        
        if not(b_check):
            out.append(_move)

    return out

def filter_king_check(board, pieces, moves, player):
    
    out = []
    
    for _move in moves:

        _board = copy.deepcopy(board)   # .copy?
        _pieces = copy.deepcopy(pieces)

        board2, pieces2 = apply_move(_move, _board, _pieces, player)

        player2 = not(player)

        b_check = get_possible_check(pieces2, board2, player2)
        
        if not(b_check):
            out.append(_move)

    return out

def filter_king_check_test_copy(board, pieces, moves, player):
    
    out = []
    
    for _move in moves:

        _board = copy.deepcopy(board)   # .copy?
        _pieces = copy.deepcopy(pieces)

        #board2, pieces2 = apply_move(_move, _board, _pieces, player)    

        out.append(_move)

    return out

def filter_king_check_test_copy_apply(board, pieces, moves, player):
    
    out = []
    
    for _move in moves:

        _board = copy.deepcopy(board)   # .copy?
        _pieces = copy.deepcopy(pieces)

        board2, pieces2 = apply_move(_move, _board, _pieces, player)    

        out.append(_move)

    return out

class Mutator():
    
    '''Helper Class for preserving board state without deepcopying.'''

    # Do not use this for move_code = enpassant, castling.
    # move_code = promotion should be fine b/c your new piece class is irrelevant

    # mutate() consists of 
    #   (pos0, pos0-val) - always going to be 0 as new value
    #   (pos1, pos1-val) - either 0 or opponents enum
    
    def __init__(self):
        self.old_mutation = None
        self.new_mutation = None
        self.mutation_king_piece = None

    def mutate_board(self, board, move):

        '''apply new board state and save the changes to class data'''

        #can use methods on .data_by_player ?
        #this might need adjusting under promotion
        #no need to account for enpassant
        
        r,c = move.pos0[0], move.pos0[1]
        old_piece_enum = board.data_by_player[r][c]       
        
        #mutation
        self.old_mutation = ((r,c), old_piece_enum)
        
        #set new
        board.data_by_player[r][c] = 0                     #always leaving

        new_val = old_piece_enum              #save this as well overwrite
        r,c = move.pos1[0], move.pos1[1]
        old_piece_enum = board.data_by_player[r][c]

        #mutation
        self.new_mutation = ((r,c), old_piece_enum)
        
        #set_new
        board.data_by_player[r][c] = new_val   #use saved value from leaving square

        return board

    def demutate_board(self,board):
        
        '''pull changes from class data, and apply them to board state'''
        
        pos = self.old_mutation[0]
        r, c = pos[0], pos[1]
        val = self.old_mutation[1]
        board.data_by_player[r][c] = val

        pos = self.new_mutation[0]
        r, c = pos[0], pos[1]
        val = self.new_mutation[1]
        board.data_by_player[r][c] = val

        return board

    def mutate_pieces(self, pieces, player):
            
        ''' [possibly] apply spot changes to property of a piece[s] in pieces
            and save those changes to class data. '''
        
        #get_possible_check_optimal(): uses King's POS, otherwise does
        #                              not use pieces.
        #get_possible_check_naive(): uses opponent's pieces, 
        #                            so you must eliminate captured piece.
        
        self.mutation_king_piece = None
        
        moving_piece_enum = self.old_mutation[1]
        if (moving_piece_enum) == 3:
            
            player_king = filter(lambda p: p.white == player and p.__class__.__name__ == "King" , pieces)[0]
            old_pos = player_king.pos
            new_pos = self.new_mutation[0]

            self.mutation_king_piece = (old_pos, new_pos)
            
            player_king.pos = new_pos

        #TODO - have not set alive = False anywhere here

        return pieces

    def demutate_pieces(self, pieces, player):
        
        ''' [possibly] pull saved piece-change-data from class data and apply those
            to correct piece in pieces; resetting pieces to original state. '''
        
        if self.mutation_king_piece is None:
            return pieces
        else:
            #TODO - helper func
            player_king = filter(lambda p: p.white == player and p.__class__.__name__ == "King" , pieces)[0]
            old_pos = self.mutation_king_piece[0]
            player_king.pos = old_pos
            return pieces


def filter_king_check_test_copy_apply_2(board, pieces, moves, player):
    
    '''Analyze the computational cost of mutating board instead of
        copying it.'''
    
    #We'll need to set this as the default and run pytest to see if
    # it's working

    out = []

    mutator = Mutator()
    
    for _move in moves:

        b_regular =  (_move.code == MOVE_CODE['regular'])

        if b_regular:
            _board = mutator.mutate_board(board, _move)
        else:
            #continue   #dont process these for computational testing
            _board = copy.deepcopy(board)
            

        _pieces = copy.deepcopy(pieces)

        if not(b_regular):
            board2, pieces2 = apply_move(_move, _board, _pieces, player)    

        #Call Here: get_possible_check_optimal()

        if b_regular:
            board = mutator.demutate_board(board)
        
        out.append(_move)

    return out

def filter_king_check_test_copy_apply_3(board, pieces, moves, player):
    
    '''Analyze the computational cost of mutating board instead of
        copying it.'''
    
    #We'll need to set this as the default and run pytest to see if
    # it's working

    out = []

    mutator = Mutator()
    
    for _move in moves:

        b_regular =  (_move.code == MOVE_CODE['regular'])

        if b_regular:
            _board = mutator.mutate_board(board, _move)
            #TODO - in other routines, account for piece.alive
            #       this only includes get_possible_check, 
            #       also get_possible_optimal need king_pos altered
            _pieces = mutator.mutate_pieces(pieces, player)
        else:
            # continue   #dont process these for computational testing
            _board = copy.deepcopy(board)
            _pieces = copy.deepcopy(pieces)


        if not(b_regular):
            board2, pieces2 = apply_move(_move, _board, _pieces, player)    

        #Call Here: get_possible_check_optimal()

        if b_regular:
            board = mutator.demutate_board(_board)
            pieces = mutator.demutate_pieces(_pieces, player)
        
        out.append(_move)

    return out

def filter_king_check_test_copy_apply_4(board, pieces, moves, player):
    
    '''Rough draft of fully optimized filter_check()'''

    out = []

    mutator = Mutator()
    
    for _move in moves:

        b_regular =  (_move.code == MOVE_CODE['regular'])

        if b_regular:
            _board = mutator.mutate_board(board, _move)
            _pieces = mutator.mutate_pieces(pieces, player)
        else:
            #Non-Standard Board/Piece Mutation
            _board = copy.deepcopy(board)
            _pieces = copy.deepcopy(pieces)
            _board, _pieces = apply_move(_move, _board, _pieces, player)

        b_check = get_possible_check_optimal(_pieces, _board, _move, player)
        
        if not(b_check):
            out.append(_move)

        if b_regular:
            board = mutator.demutate_board(_board)
            pieces = mutator.demutate_pieces(_pieces, player)

    return out

def is_king_in_check(board, pieces, player):

    '''return a boolean for if current player is in check'''

    # It's ultimately O(n+1) not O(n*2) , because it's not called
    # for each available_move once but for all of them, at start of the turn.

    #TODO - here construct cache_pos0_king_check_calc_needed list
    #       for downstream consumption by filter_king_check()

        # 1st, if opp_kill_move == [], then only need to check king_moves
        # 2nd , if 1st doesnt apply then check cache to see if calc_needed

    return get_possible_check_optimal(pieces, board, None, player)

    
    
