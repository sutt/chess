import sys, copy, time
from datatypes import moveAHolder

#Params and Enums ---------------------------

BOARD_WIDTH = 8
KING_COL = 4        #based on index0 and a White-POV

MOVE_CODE = {}
MOVE_CODE['regular'] = 0
MOVE_CODE['en_passant'] = 1
MOVE_CODE['castling'] = 2

MOVE_TYPE = {}
MOVE_TYPE['upacross'] = 0
MOVE_TYPE['diagonal'] = 1
MOVE_TYPE['twobyone'] = 2


#Helper Functions ---------------------------

MoveA = moveAHolder()

def move_tuple(b_append, move, move_type):
    ''' if b_append: build MoveA namedtuple from argument data.'''
    move_code = MOVE_CODE[move_type]
    out = MoveA(move, move_code) if b_append else move
    return out


def print2(data, arg1="", arg2="", arg3="",arg4=""):
    '''for VS-code debugging issue: https://github.com/Microsoft/vscode/issues/36630'''
    out = str(data) + str(arg1) + str(arg2) + str(arg3) + str(arg4)
    try:
        print data
    except:
        pass


class Board:
    
    ''' Store all turn-to-turn Game State here.
        This class also generates "on-board"-permissible moves given a:
            an atomic-move-type ('updown', 'diagonal', 'twobyone') 
            and a pos0 (r,c)
        But does not account for blocking pieces along those permissible moves.'''

    def __init__(self):
        self.width = BOARD_WIDTH
        data = [[0 for i in range(self.width)] for j in range(self.width)]
        self.data = copy.deepcopy(data)
        self.data_by_player = copy.deepcopy(data)   #TODO - refactor as data
        self.player_in_check = [False, False]
        self.rooks_can_castle = [[True, True], [True, True]]
        self.player_only_king_moves = [0,0]
        

        #Notes:
        # data: 0=blank, 1=piece(of any player)
        # player_data: 0=blank, 1=white-piece, 2=black-piece
        # annotate, misc are for printing out human readable displays or testing
        # player_in_check: ind 0=white 1=black
        # rooks_can_castle: ind-outer 0=white, ind-inner 0=left-rook, 1=right-rook
        # self.king_can_castle: is stored in the respective king pieces
    
    def set_data(self, data):
        self.data_by_player = data

    #Position Data

    def get_data_pos(self, pos):
        return self.data_by_player[pos[0]][pos[1]]

    #TODO - rename old_pos()
    def old_player_pos(self,pos):
        self.data_by_player[pos[0]][pos[1]] = 0

    #TODO - rename new_pos()
    def new_player_pos(self, player, pos, piece, b_two_advances = False):
        """ 0=blank, 1=generic-piece, 2=en-passant-vulnerable-pawn 3=king  
            multiplied-by: -1 for black +1 for white """
        piece_num = 1
        if piece.__class__.__name__ == "Pawn": 
            if b_two_advances:
                piece_num = 2
        if piece.__class__.__name__ == "King": piece_num = 3

        player_mult = 1 if player else -1

        self.data_by_player[pos[0]][pos[1]] = piece_num * player_mult

    #Castling

    #TODO - rewrite this piece of shit
    def modify_castling_property(self, player, piece, pos0):
        if piece.__class__.__name__ != "Rook":
            return 0
        if not(any(self.rooks_can_castle[1- int(player)])):
            return 0
        
        rook_col = pos0[1]
        
        rook_side = -1
        
        if rook_col == 0: rook_side = 0
        if rook_col == BOARD_WIDTH - 1: rook_side = 1
        
        if rook_side == -1:
            return 0
        
        self.rooks_can_castle[1- int(player)][rook_side] = False

    
    def get_rook_castle_move(self, player, left_side):
        row = self.width - 1 if player else 0
        col0 = 0 if left_side else self.width - 1
        col1 = KING_COL - 1 if left_side else KING_COL + 1
        return ((row,col0), (row,col1))

    def get_king_castle_move(self, player, left_side):
        row = self.width - 1 if player else 0
        col0 = KING_COL
        col1 = KING_COL - 2 if left_side else KING_COL + 2
        return ((row,col0), (row,col1))
    
    #TODO - add player_i(player) as function in 4 below:

    def get_rooks_castle(self,player):
        return self.rooks_can_castle[1 - int(player)][:]

    #Check

    def set_player_in_check(self, player, b_check):
        self.player_in_check[1 - int(player)] = b_check

    def set_player_not_in_check(self, player):
        self.player_in_check[1 - int(player)] = False
    
    def b_in_check(self,_player):
        return self.player_in_check[1 - int(_player)]

    #TODO - add to utils
    def player_name_from_bool(self, bool_player):
        if bool_player:
            return 'White'
        else:
            return 'Black'


    #Enpassant 

    @staticmethod
    def two_advances(pos0, pos1):
        return 2 == abs(pos0[0] - pos1[0])

    @staticmethod
    def en_passant_pos(pos1, _player):
        upwards = -1 if _player else 1
        return (pos1[0] - upwards, pos1[1])
    
    def clear_enpassant_vulnerability(self, _player):
        player_mult = 1 if _player else -1
        for i in range(BOARD_WIDTH):
            for j in range(BOARD_WIDTH):
                #TODO - get_pos / set_pos
                if self.data_by_player[i][j] == 2 * player_mult:
                    self.data_by_player[i][j] = player_mult
                
    def player_relative_pos(self, player, row, col):
        """ returns pos based on player-relative row e.g. white's "back row" is row 7"""
        _row =  (self.width-1)*player +  -1*row if player else row
        _col = col
        return _row, _col

    #Atomic Move Types

    def get_diagonals(self, pos, spaces = BOARD_WIDTH - 1, i_dir = range(4)):
        """ input: pos, [spaces (int > 0)] [only_direction (tuple)]
            returns: list of list of pos's, ordered closest from piece
                     starting pos to furthest"""

        _row, _col, _width = pos[0], pos[1], self.width
        
        #Tricky off-by-one stuff here, since range omits final value
        _maxup, _maxdown = _row + 1, _width - _row
        _maxleft, _maxright = _col + 1, _width - _col

        #1=NW 2=NE 3=SW 4=SE
        pos1 = [ (_row - i, _col - i) for i in range( 1, min(_maxup, _maxleft))]
        pos2 = [ (_row - i, _col + i) for i in range( 1, min(_maxup, _maxright))]
        pos3 = [ (_row + i, _col - i) for i in range( 1, min(_maxdown, _maxleft))]
        pos4 = [ (_row + i, _col + i) for i in range( 1 ,min(_maxdown, _maxright))]
        
        ret = [pos1[:spaces], pos2[:spaces], pos3[:spaces], pos4[:spaces]]

        return [ret[i] for i in range(len(ret)) if i in i_dir]

    
    def get_upacross(self, pos, spaces = BOARD_WIDTH - 1, i_dir = range(4)):
        """ input: pos, [spaces (int > 0)]
            returns: list of list of pos's, ordered closest from piece
                     starting pos to furthest"""
        
        _row, _col, _width = pos[0], pos[1], self.width
        
        #1=Up 2=Right 3=Down 4=Left
        pos1 = [ (i,_col) for i in range( _row - 1, -1, -1)]
        pos2 = [ (_row,i) for i in range( _col + 1, _width)]
        pos3 = [ (i,_col) for i in range( _row + 1, _width, 1)]
        pos4 = [ (_row,i) for i in range( _col - 1, -1, -1)]

        ret = [pos1[:spaces], pos2[:spaces], pos3[:spaces], pos4[:spaces]]
        
        return [ret[i] for i in range(len(ret)) if i in i_dir]
        


    def get_two_by_ones(self,pos):
        """ input: pos
            returns: list of list of pos-tuples.  inner list is always of len-1.
                     this function eliminates any "off the board" moves. """
        
        _row, _col, _width = pos[0], pos[1], self.width
        pos1 = []
        
        for _r, _c in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            for _d in [(1,2),(2,1)]:
                
                _pos = ( _row + _r*_d[0], _col + _c*_d[1] )

                if (0 <= _pos[0] < _width) and (0 <= _pos[1] < _width):
                    pos1.extend([[_pos]])     #each one in a list
        
        return pos1

    #TODO - used?
    def get_castle_interspaces(self,player):
        """ input: player (bool)
            returns: list of list of pos tuples """
        _row = 0 if not(player) else BOARD_WIDTH - 1
        pos1 = []
        pos1.append( [(_row, i) for i in range(1,KING_COL)] )
        pos1.append( [(_row, i) for i in range(KING_COL + 1,    BOARD_WIDTH - 1)] )
        return pos1



class Piece:

    ''' This serves as a template for each piece class. Init sets all
        move_types to false/0, and all propoerties to false. These are
        overwritten as needed during inheritance by the specific piece class.'''

    def __init__(self,b_white, pos, **kwargs):
        self.white = b_white
        self.alive = True
        self.pos = pos
        # int: these set what type of moves, and how far the piece can go
        self.upacross = 0
        self.diagonal = 0
        # bool: special move type
        self.twobyone = False
        self.pawn_move = False
        self.king_can_castle = False
        self.rook_can_castle = False    #TODO - remove

    def modify_castling_property(self,**kwargs):
        if self.__class__.__name__ == "King":
            self.king_can_castle = False
        # if self.__class__.__name__ == "Rook":
        #     self.rook_can_castle = False

    def filter_by_blocking_pieces(self,moves, board, b_pawn = False, **kwargs):
        
        """input: moves: (list of list of pos-tuples), each list-of-pos-tuples is 
                         an ordered "move-set".
                  board: contains data
        
            returns: list of pos-tuples that are valid moves 
                     or, bool, if check_flag=True indicating one of opponent's
                     pieces can capture king."""

        valids = []
        
        piece_enums = [1,2,3]
        mine_mult = 1 if self.white else -1
        yours_mult = -1 if self.white else 1
        
        mine = map(lambda v: v * mine_mult, piece_enums)
        yours = map(lambda v: v * yours_mult, piece_enums)
        
        yours_king = -3 if self.white else 3
        yours_enpassant_pawn = -2 if self.white else 2

        b_move_type = kwargs.get('move_type_flag', False)
        mirror_flag = kwargs.get('mirror_flag', False)
        
        if mirror_flag:
            b_pawn = False  #for now

        b_check = False
        mirrors = []

        b_king = True if self.__class__.__name__ == "King" else False
        
        if b_pawn:
            
            for move in moves[0]:  # advance, a list of len-1 or len-2
                
                #TODO - get_data_pos
                there = board.data_by_player[move[0]][move[1]]
                
                if there in  mine:
                    break
                if there in yours:
                    break
                if there == 0:
                    valids.append(move_tuple(b_move_type, move, 'regular'))
                
            for list_move in moves[1:]:   # a list of len-1 or len-2
                for move in list_move:  # attacks is a list of len-1

                    there = board.data_by_player[move[0]][move[1]]

                    upwards = -1 if self.white else 1
                    enpassant_there = board.data_by_player[move[0] - upwards][move[1]]
                    
                    if there in  mine:
                        break
                    if there in yours:
                        valids.append(move_tuple(b_move_type, move, 'regular'))
                        if mirror_flag: 
                            mirrors.append(move)
                        if there == yours_king:
                            b_check = True
                        break
                    if enpassant_there == yours_enpassant_pawn:
                        valids.append(move_tuple(b_move_type, move, 'en_passant'))
                    if there == 0:
                        break
            
            # return pawn moves
            return valids
        
        # Handling king castling here, check for clear back row, all other conditions satisfied
        if b_king:
            castling_moves = filter(lambda move_set: len(move_set) > 1, moves)
            if len(castling_moves) > 0:
                [moves.pop(moves.index(_x)) for _x in castling_moves]  #dont process them below
                
                #TODO - rewrite this tersely
                for move_set in castling_moves:
                    all_clear = True
                    for move in move_set:
                        there = board.data_by_player[move[0]][move[1]]
                        if there != 0: 
                            all_clear = False
                            break
                    if all_clear:
                        #TODO - eliminate this nasty move_set[1] hack. It allows us to
                        #       disambiguate castling from king simply moving 1 over
                        valids.append(move_tuple(b_move_type, move_set[1], 'castling'))
        
        # All non-pawn Pieces, and non-castling moves calcd here
        for move_set in moves:
            for move in move_set:
                
                there = board.data_by_player[move[0]][move[1]]

                if there in mine:
                    break
                elif there in yours:
                    valids.append(move_tuple(b_move_type, move, 'regular'))
                    if mirror_flag:
                        mirrors.append(move)
                    if there == yours_king:
                        b_check = True
                    break
                elif there == 0:
                    valids.append(move_tuple(b_move_type, move, 'regular'))

        
        if kwargs.get('check_flag', False):
            return b_check

        if kwargs.get('mirror_flag', False):
            return mirrors

        return valids
        

    def get_available_moves(self, board, move_type_flag=False, check_flag=False
                            ,mirror_flag=False):
        
        ''' input:board (obj) current board
                  move_type_flag (bool)  - appends MOVE_CODE to pos in temp2
                  check_flag (bool)      - outputs b_check as boolean
                  mirror_flag (bool)     - outputs mirrors instead of valids

            returns:[check=F, move=F] list of pos-tuples (or empty list)
                    [check=T]         bool for if opposing king-in-check
                    [check=F, move=T] list of (pos-tuple, MOVE_CODE) (or empty list) 
                                      representing spaces piece could move to.     
                    [mirror=T,move=T] list of (pos-tuple, MOVE_CODE) (or empty list) 
                                      representing pos of opponent piece which may
                                      threaten the king.
                    '''
        
        temp = []
        
        if self.upacross > 0:
            temp.extend( board.get_upacross(self.pos, spaces = self.upacross) )
        if self.diagonal > 0:
            temp.extend( board.get_diagonals(self.pos, spaces = self.diagonal) )
        if self.twobyone:
            temp.extend( board.get_two_by_ones(self.pos) )
        if self.pawn_move:
            upwards = ((0,),(0,1)) if self.white else ((2,),(2,3))
            home_pos = board.player_relative_pos(self.white, row = 1, col = self.pos[1])
            advances = 2 if home_pos == self.pos else 1
            temp.extend( board.get_upacross(self.pos, spaces = advances, i_dir = upwards[0]) )            
            temp.extend( board.get_diagonals(self.pos, spaces = 1, i_dir = upwards[1]) )

        if self.king_can_castle and not(board.b_in_check(self.white)):
            b_castle = board.get_rooks_castle(player = self.white)  #not using player, but piece-color attribute
            if any(b_castle):
                temp_castle = board.get_castle_interspaces(player = self.white)
                temp_castle = [temp_castle[i] for i in range(2) if b_castle[i]]
                temp.extend(temp_castle)


        temp2 = self.filter_by_blocking_pieces(temp
                                                ,board
                                                ,b_pawn = self.pawn_move
                                                ,check_flag = check_flag
                                                ,move_type_flag = move_type_flag
                                                ,mirror_flag = mirror_flag
                                                )
        
        if check_flag:
            if isinstance(temp2, bool) and temp2: 
                return True
            else:
                return False

        return temp2


class Pawn(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.en_passant_vulnerable = False      #TODO - remove as un-needed (?)
        self.pawn_move = True
        

class King(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.king_can_castle = True
        self.upacross = 1
        self.diagonal = 1


class Rook(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.rook_can_castle = True
        self.upacross = BOARD_WIDTH

class Knight(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.twobyone = True
        

class Bishop(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.diagonal = BOARD_WIDTH

class Queen(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.upacross = BOARD_WIDTH
        self.diagonal = BOARD_WIDTH

class SuperKing(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.upacross = BOARD_WIDTH
        self.diagonal = BOARD_WIDTH
        self.twobyone = True
        #self.pawn_move = True



#TODO - add to helper functions
def place_pieces(board, **kwargs):
    """ input: board [blank]
        returns: (board, pieces) """

    pieces = []
    
    for _player in (True,False):     # True=White, False= Black
        for _row in [0,1]:           # 0=BACK, 1=FRONT-PAWNS
            for _col in range(board.width):

                _pos = board.player_relative_pos(_player,_row,_col)

                if _row == 1:
                    
                    piece = Pawn(b_white = _player, pos = _pos  )
                
                else:
                    
                    if _col == 0 or _col == 7:
                        piece = Rook(b_white = _player, pos = _pos  )
                    
                    elif _col == 1 or _col == 6:
                        piece = Knight(b_white = _player, pos = _pos  )
                    
                    elif _col == 2 or _col == 5:
                        piece = Bishop(b_white = _player, pos = _pos  )
                    
                    else:
                        if _col == 3:
                            piece = Queen(b_white = _player, pos = _pos  )
                    
                        if _col == 4:
                            piece = King(b_white = _player, pos = _pos  )

                
                pieces.append(piece)
                
                board.new_player_pos( player = _player, pos = _pos, piece = piece)            
    
    return board, pieces


#TODO - move these a centralized test file

# def tests():    

#     board = Board()
#     board.print_board()
#     board, pieces = place_pieces(board)
#     board.print_board()

#     # for p in pieces:
#     #     print str(p.white) + " " + str(p.__class__.__name__) + " " + str(p.pos)

#     board.start_annotate()
#     for p in pieces:
#         board.mark_annotate(p)
#     board.print_board(b_annotate = True)



#     pawn = Pawn(True,(1,1))
#     print2(pawn.pos)
#     print2(pawn.en_passant_vulnerable)
#     print2(pawn.__class__.__name__)

#     blackbishop = pieces[2]
#     print2(str(blackbishop.__class__.__name__)  + " " + str(blackbishop.pos))
#     bishop_pos = blackbishop.pos
#     bishops_diags = board.get_diagonals(bishop_pos)
#     print2(bishops_diags)
#     board.start_misc()
#     for diags in bishops_diags:
#         for _pos in diags:
#             board.mark_misc(_pos)
#     board.print_board(b_misc = True)

#     board.start_misc()
#     diags = board.get_diagonals((4,4))
#     print2(diags)
#     board.mark_all_misc(diags)
#     board.print_board(b_misc = True)

#     blackrook = pieces[0]
#     print2(str(blackrook.__class__.__name__)  + " " + str(blackrook.pos))
#     rook_pos = blackrook.pos
#     rook_moves = board.get_upacross(rook_pos)
#     print2(rook_moves)
#     board.start_misc()
#     board.mark_all_misc(rook_moves)
#     board.print_board(b_misc = True)

#     POS = (3,4)
#     rook_moves = board.get_upacross(POS)
#     print2(rook_moves)
#     board.start_misc()
#     board.mark_all_misc(rook_moves)
#     board.print_board(b_misc = True)

#     POS = (3,3)
#     print2('Kngiht at: ', str(POS))
#     knight_moves = board.get_two_by_ones(POS)
#     print2(knight_moves)
#     board.start_misc()
#     board.mark_all_misc(knight_moves)
#     board.print_board(b_misc = True)

#     POS = (0,7)
#     print2('Kngiht at: ', str(POS))
#     knight_moves = board.get_two_by_ones(POS)
#     print2(knight_moves)
#     board.start_misc()
#     board.mark_all_misc(knight_moves)
#     board.print_board(b_misc = True)


#     print2('Unobstructed Bishop at 4,4')
#     board2 = Board()
#     bishop = Bishop(b_white = True,pos=(4,4))
#     board.data_by_player[4][4] = 0
#     moves = bishop.get_available_moves(board2)
#     print2(moves)
#     board.start_misc()
#     board.mark_list_misc(moves)
#     board.print_board(b_misc = True)

#     print2('Obstructed White Bishop at 4,4 inital pieces')
#     board2 = Board()
#     bishop = Bishop(b_white = True,pos=(4,4))
#     board2.data_by_player[4][4] = 1

#     board2.data_by_player[3][5] = 1
#     board2.data_by_player[2][2] = -2
#     board2.data_by_player[6][6] = 1
    
#     board2.print_board(b_player_data = True)
    
#     print2('Moves available to that bishop')
#     moves = bishop.get_available_moves(board2)
#     print2(moves)
#     board.start_misc()
#     board.mark_list_misc(moves)
#     board.mark_misc((4,4), val = "B")
#     board.print_board(b_misc = True)

    
#     board2 = Board()
#     print2('Obstructed White Pawn at inital position col 2')
#     POS = (6,2)
#     pawn = Pawn(b_white = True,pos=POS)
#     board2.data_by_player[6][2] = 1
#     board2.print_board(b_player_data = True)

#     print2('Pawns available moves')
#     moves = pawn.get_available_moves(board2)
#     print2(moves)
#     board2.start_misc()
#     board2.mark_list_misc(moves)
#     board2.mark_misc(POS, val = "P")
#     board2.print_board(b_misc = True)

#     board2.data_by_player[5][3] = -2
#     board2.data_by_player[5][1] = 1
#     board2.data_by_player[4][2] = -2

#     print2("Obstructed white pawn situation:")
#     board2.print_board(b_player_data = True)
#     print2("available moves to the pawn")
#     moves = pawn.get_available_moves(board2)
#     print moves
#     board2.start_misc()
#     board2.mark_list_misc(moves)
#     board2.mark_misc(POS, val = "P")
#     board2.print_board(b_misc = True)

#     # print2('opening moves available')
#     # board = Board()
#     # board, pieces = place_pieces(board)
#     # board.print_board(b_player_data = True)

#     # pawn_moves = []
#     # knight_moves = []
#     # other_moves = []
#     # for p in pieces:
#     #     if p.__class__.__name__ == "Pawn":
#     #         pawn_moves.extend(p.get_available_moves(board))
#     #     elif p.__class__.__name__ == "Knight":
#     #         knight_moves.extend(p.get_available_moves(board))
#     #     else:
#     #         other_moves.extend(p.get_available_moves(board))

#     # board.start_misc()
#     # board.mark_list_misc(pawn_moves, val = 1)
#     # board.mark_list_misc(knight_moves, val = 5)
#     # board.mark_list_misc(other_moves, val = 4)
#     # board.print_board(b_misc = True)
    
#     board = Board()
#     out = board.get_castle_interspaces(True)
#     print 'white castling moves'
#     print out
#     out = board.get_castle_interspaces(False)
#     print 'black castling moves'
#     print out

#     king = King(b_white = True,pos = (7,3))
#     moves = king.get_available_moves(board, move_type_flag = True)
#     print 'white king all moves'
#     print moves

#     print2(board.width)

#     board2 = Board()
#     print2('Obstructed White Pawn at inital position col 2')
#     POS = (6,2)
#     pawn = Pawn(b_white = True,pos=POS)
#     board2.data_by_player[6][2] = 1
#     board2.print_board(b_player_data = True)

#     #Test Castling
#     board = Board() #can_castle is init true
#     POS = (7,4)
#     white_king = King(b_white = True,pos=POS)
#     moves = white_king.get_available_moves(board,move_type_flag = True)
#     moves2 = white_king.get_available_moves(board,move_type_flag = False)
#     print moves

#     board.start_misc()
#     board.mark_list_misc(moves2)
#     board.mark_misc(POS, val = "K")
#     board.print_board(b_misc = True)


def test_bishop_moves():
    board = Board()
    board, pieces = place_pieces(board)
    blackbishop = pieces[2]
    bishop_pos = blackbishop.pos
    bishops_diags = board.get_diagonals(bishop_pos)
    assert bishops_diags == [[(6, 1), (5, 0)], [(6, 3), (5, 4), (4, 5), (3, 6), (2, 7)], [], []]

def test_rook_moves():
    board = Board()
    board, pieces = place_pieces(board)
    blackrook = pieces[0]
    rook_pos = blackrook.pos
    rook_moves = board.get_upacross(rook_pos)
    assert rook_moves == [[(6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0), (0, 0)], [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)], [], []]

def test_rook_moves2():
    board = Board()
    POS = (3,4)
    rook_moves = board.get_upacross(POS)
    assert rook_moves == [[(2, 4), (1, 4), (0, 4)], [(3, 5), (3, 6), (3, 7)], [(4, 4), (5, 4), (6, 4), (7, 4)], [(3, 3), (3, 2), (3, 1), (3, 0)]]

def test_knight_moves():
    board = Board()
    POS = (3,3)
    print2('Kngiht at: ', str(POS))
    knight_moves = board.get_two_by_ones(POS)
    assert knight_moves == [[(4, 5)], [(5, 4)], [(4, 1)], [(5, 2)], [(2, 5)], [(1, 4)], [(2, 1)], [(1, 2)]]

def test_knight_moves2():
    board = Board()
    POS = (0,7)
    print2('Kngiht at: ', str(POS))
    knight_moves = board.get_two_by_ones(POS)
    assert knight_moves == [[(1, 5)], [(2, 6)]]

def test_unobstructed1():
    board2 = Board()
    bishop = Bishop(b_white = True,pos=(4,4))
    moves = bishop.get_available_moves(board2)
    assert moves == [(3, 3), (2, 2), (1, 1), (0, 0), (3, 5), (2, 6), (1, 7), (5, 3), (6, 2), (7, 1), (5, 5), (6, 6), (7, 7)]

def test_obstructed():
    board2 = Board()
    bishop = Bishop(b_white = True,pos=(4,4))
    board2.data_by_player[4][4] = 1
    board2.data_by_player[3][5] = 1
    board2.data_by_player[2][2] = -1
    board2.data_by_player[6][6] = 1
    moves = bishop.get_available_moves(board2)
    assert moves == [(3, 3), (2, 2), (5, 3), (6, 2), (7, 1), (5, 5)]

def test_unobstruct_pawn():
    board2 = Board()
    POS = (6,2)
    pawn = Pawn(b_white = True,pos=POS)
    board2.data_by_player[6][2] = 1
    moves = pawn.get_available_moves(board2)
    assert moves == [(5, 2), (4, 2)]

def test_obstruct_pawn():
    board2 = Board()
    POS = (6,2)
    pawn = Pawn(b_white = True,pos=POS)
    board2.data_by_player[5][3] = -1
    board2.data_by_player[5][1] = 1
    board2.data_by_player[4][2] = -1
    moves = pawn.get_available_moves(board2)
    assert moves == [(5, 2), (5, 3)]

def test_checkflag():
    board2 = Board()
    POS = (0,0)
    bishop = Bishop(b_white = True,pos=POS)
    board2.data_by_player[7][7] = 3 #white king
    b_check = bishop.get_available_moves(board2, check_flag = True)
    assert b_check == False
    board2.data_by_player[6][6] = -3 #black king
    b_check = bishop.get_available_moves(board2, check_flag = True)
    assert b_check == True

def test_enpassant():
    board = Board()
    POS = (3,2)
    white_pawn = Pawn(b_white = True,pos=POS)
    moves = white_pawn.get_available_moves(board)
    assert moves == [(2,2)]
    
    board.data_by_player[3][1] = -2
    moves = white_pawn.get_available_moves(board)
    assert moves == [(2,2),(2,1)]

def test_move_type_flag():
    board = Board()
    POS = (3,2)
    white_pawn = Pawn(b_white = True,pos=POS)
    moves = white_pawn.get_available_moves(board,move_type_flag = True)
    assert moves == [((2,2),0)]
    
    board.data_by_player[3][1] = -2
    moves = white_pawn.get_available_moves(board, move_type_flag = True)
    assert moves == [((2,2),0),((2,1),1)]

def test_castling_allowed():
    board = Board() #can_castle is init true
    POS = (7,4)
    white_king = King(b_white = True,pos=POS)
    
    moves = white_king.get_available_moves(board,move_type_flag = True)
    assert moves == [((7, 2), 2), ((7, 6), 2), ((6, 4), 0), ((7, 5), 0), ((7, 3), 0), ((6, 3), 0), ((6, 5), 0)]

def test_castling_disallowed1():
    board = Board() #can_castle is init true
    POS = (7,4)
    white_king = King(b_white = True,pos=POS)
    white_king.king_can_castle = False

    moves = white_king.get_available_moves(board,move_type_flag = True)
    print moves
    assert moves == [((6, 4), 0), ((7, 5), 0), ((7, 3), 0), ((6, 3), 0), ((6, 5), 0)]

def test_castling_disallowed2():
    board = Board() #can_castle is init true
    POS = (7,4)
    white_king = King(b_white = True,pos=POS)
    
    board.rooks_can_castle[0][1] = False
    moves = white_king.get_available_moves(board,move_type_flag = True)
    print moves
    assert moves == [((7, 2), 2), ((6, 4), 0), ((7, 5), 0), ((7, 3), 0), ((6, 3), 0), ((6, 5), 0)]

    board.rooks_can_castle[0][0] = False
    moves = white_king.get_available_moves(board,move_type_flag = True)
    assert moves == [((6, 4), 0), ((7, 5), 0), ((7, 3), 0), ((6, 3), 0), ((6, 5), 0)]



if __name__ == "__main__":
   tests()

    