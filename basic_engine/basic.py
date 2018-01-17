import sys, copy

BOARD_WIDTH = 8

class Board:
    
    def __init__(self):
        self.width = BOARD_WIDTH
        self.data = [[0 for i in range(self.width)] for j in range(self.width)]
        self.data_by_player = [[0 for i in range(self.width)] for j in range(self.width)]
        self.annotate = None
        self.misc = None

        #Notes:
        # data: 0=blank, 1=piece(of any player)
        # player_data: 0=blank, 1=white-piece, 2=black-piece
        # annotate, misc are for printing out human readable displays or testing

    def new_pos(self,row,col):
        self.data[row][col] = 1

    def new_player_pos(self, player, pos):
        """ 2=black-piece, 1=white-piece, 0=blank """
        self.data_by_player[pos[0]][pos[1]] = 2 - int(player)

    def start_annotate(self,**kwargs):
        self.annotate = copy.copy(self.data)

    def start_misc(self,**kwargs):
        self.misc = [[0 for i in range(self.width)] for j in range(self.width)]

    def mark_annotate(self,piece,**kwargs):
        _pos = piece.pos
        _symbol = str.upper(str(piece.__class__.__name__)[0])
        self.annotate[_pos[0]][_pos[1]] = _symbol

    def mark_misc(self,pos,**kwargs):
        self.misc[pos[0]][pos[1]] = 1

    def mark_all_misc(self,list_list_pos,**kwargs):
        for list_pos in list_list_pos:
            for pos in list_pos:
                self.misc[pos[0]][pos[1]] = 1

    def player_relative_pos(self,player,row,col):
        """ returns pos based on player-relative row e.g. white's "back row" is row 7"""
        _row =  (self.width-1)*player +  -1*row if player else row
        _col = col
        return _row, _col


    def get_diagonals(self,pos, spaces = 7):
        """ input: pos, [spaces (int > 0)]
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
        
        return [pos1, pos2, pos3, pos4]
    
    def get_upacross(self,pos):
        """ input: pos, [spaces (int > 0)]
            returns: list of list of pos's, ordered closest from piece
                     starting pos to furthest"""
        
        _row, _col, _width = pos[0], pos[1], self.width
        
        #1=Up 2=Down 3=Right 4=Left
        pos1 = [ (i,_col) for i in range( _row + 1, _width, 1)]
        pos2 = [ (i,_col) for i in range( _row - 1, -1, -1)]
        pos3 = [ (_row,i) for i in range( _col + 1, _width)]
        pos4 = [ (_row,i) for i in range( _col - 1, -1, -1)]

        return [pos1, pos2, pos3, pos4]


    def get_two_by_ones(self,pos):
        
        _row, _col, _width = pos[0], pos[1], self.width
        pos1 = []
        
        for _r, _c in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            for _d in [(1,2),(2,1)]:
                
                _pos = ( _row + _r*_d[0], _col + _c*_d[1] )

                if (0 <= _pos[0] < _width) and (0 <= _pos[1] < _width):
                    pos1.extend([[_pos]])     #each one in a list
        
        return pos1

    def print_board(self,b_annotate = False ,b_misc = False
                        ,b_player_data = False):

        p_data = self.data
        if b_annotate: p_data = self.annotate
        if b_misc: p_data = self.misc
        if b_player_data: p_data = self.data_by_player
        
        out = ""
        for row in p_data:
            s_row = map(str,row)
            out += " ".join(s_row)
            out += "\n"        
        print out

class Piece:

    def __init__(self,b_white, pos, **kwargs):
        self.white = b_white
        self.alive = True
        self.pos = pos
        # int: these set what type of moves, and how far the piece can go
        self.upacorss = 0
        self.diagonal = 0
        # bool: special move type
        self.twobyone = False
        self.pawn_move = False

    def filter_by_blocking_pieces(a1, a2):
        pass

    def get_available_moves(self,board):
        moves = []
        if self.upacross > 0:
            temp = board.get_upacross(self.pos, spaces = self.upacorss)
            temp2 = filter_by_blocking_pieces(temp, board )
            #need to flatten temp2
            moves.extend( temp2 )
        if self.diagonal > 0:
            temp = board.get_diagonals(self.pos, spaces = self.diagonal)
            temp2 = filter_by_blocking_pieces(temp, board )
            #need to flatten temp2
            moves.extend( temp2)

        
        
        #check_if_moving_causes_check()
        return moves

class Pawn(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.en_passant_vulnerable = False
        self.pawn_move = True
        

class King(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.king_can_castle = True
        self.upacorss = 1
        self.diagonal = 1


class Rook(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.rook_can_castle = True
        self.upacorss = BOARD_WIDTH

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
        self.upacorss = BOARD_WIDTH
        self.diagonal = BOARD_WIDTH




def place_pieces(board,**kwargs):
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
                
                board.new_pos(row = _pos[0] ,col = _pos[1] )
                board.new_player_pos( player = _player, pos = _pos)            
    
    return board, pieces


def main():    

    board = Board()
    board.print_board()
    board, pieces = place_pieces(board)
    board.print_board()

    # for p in pieces:
    #     print str(p.white) + " " + str(p.__class__.__name__) + " " + str(p.pos)

    board.start_annotate()
    for p in pieces:
        board.mark_annotate(p)
    board.print_board(b_annotate = True)



    pawn = Pawn(True,(1,1))
    print pawn.pos
    print pawn.en_passant_vulnerable
    print pawn.__class__.__name__

    blackbishop = pieces[2]
    print str(blackbishop.__class__.__name__)  + " " + str(blackbishop.pos)
    bishop_pos = blackbishop.pos
    bishops_diags = board.get_diagonals(bishop_pos)
    print bishops_diags
    board.start_misc()
    for diags in bishops_diags:
        for _pos in diags:
            board.mark_misc(_pos)
    board.print_board(b_misc = True)

    board.start_misc()
    diags = board.get_diagonals((4,4))
    print diags
    board.mark_all_misc(diags)
    board.print_board(b_misc = True)

    blackrook = pieces[0]
    print str(blackrook.__class__.__name__)  + " " + str(blackrook.pos)
    rook_pos = blackrook.pos
    rook_moves = board.get_upacross(rook_pos)
    print rook_moves
    board.start_misc()
    board.mark_all_misc(rook_moves)
    board.print_board(b_misc = True)

    POS = (3,4)
    rook_moves = board.get_upacross(POS)
    print rook_moves
    board.start_misc()
    board.mark_all_misc(rook_moves)
    board.print_board(b_misc = True)

    POS = (3,3)
    knight_moves = board.get_two_by_ones(POS)
    print knight_moves
    board.start_misc()
    board.mark_all_misc(knight_moves)
    board.print_board(b_misc = True)

    POS = (0,7)
    knight_moves = board.get_two_by_ones(POS)
    print knight_moves
    board.start_misc()
    board.mark_all_misc(knight_moves)
    board.print_board(b_misc = True)

    #POS = (1,1)
    #piece = Piece(b_white = True, pos = POS )
    #board.new_pos(row = POS[0] ,col = POS[1] )
    #board.print_board()

    print board.width


if __name__ == "__main__":
    main()

#3850
#FGN

    