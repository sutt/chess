import sys, copy

BOARD_WIDTH = 8

class Board:
    
    def __init__(self):
        self.width = BOARD_WIDTH
        self.data = [[0 for i in range(self.width)] for j in range(self.width)]
        self.annotate = None

    def new_pos(self,row,col,**kwargs):
        self.data[row][col] = 1

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

    def init_pos(self,player,row,col):
        _row =  (self.width-1)*player +  -1*row if player else row
        _col = col
        return _row, _col


    def get_diagonals(self,pos, spaces = 7):
        """ordered closest to furthest"""

        _row, _col, _width = pos[0], pos[1], self.width
        
        #Tricky off-by-one stuff here, since range omits final value
        _maxup, _maxdown = _row + 1, _width - _row
        _maxleft, _maxright = _col + 1, _width - _col

        #1=NW 2=NE 3=SW 4=SE
        pos1 = [ (_row - i, _col - i) for i in range( 1, min(_maxup, _maxleft))]
        pos2 = [ (_row - i, _col + i) for i in range( 1, min(_maxup, _maxright))]
        pos3 = [ (_row + i, _col - i) for i in range( 1, min(_maxdown, _maxleft))]
        pos4 = [ (_row + i, _col + i) for i in range( 1 ,min(_maxdown, _maxright))]
        
        return (pos1, pos2, pos3, pos4)
    
    def get_upacross(self,pos):
        
        _row, _col, _width = pos[0], pos[1], self.width
        
        #1=Up 2=Down 3=Right 4=Left
        pos1 = [ (i,_col) for i in range( _row + 1, _width, 1)]
        pos2 = [ (i,_col) for i in range( _row - 1, -1, -1)]
        pos3 = [ (_row,i) for i in range( _col + 1, _width)]
        pos4 = [ (_row,i) for i in range( _col - 1, -1, -1)]

        return (pos1, pos2, pos3, pos4)

    def get_two_by_ones(self,pos):
        pass

    def print_board(self,b_annotate = False ,b_misc = False):
        p_data = self.data
        if b_annotate: p_data = self.annotate
        if b_misc: p_data = self.misc
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

    def get_available_moves(self,current_board):
        moves = []
        #b_blocking = False # for Knight only
        #check_if_moving_causes_check()
        return moves

class Pawn(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.en_passant_vulnerable = False
        

class King(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.typ = 'King'
        self.king_can_castle = True


class Rook(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)
        self.rook_can_castle = True

class Knight(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)

class Bishop(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)

class Queen(Piece):
    
    def __init__(self,b_white,pos):
        Piece.__init__(self,b_white,pos)

#class Bishop(Piece):   
#class Queen(Piece):

board = Board()
board.print_board()

pieces = []

#Place Pieces
for _player in (True,False):
    for _row in [0,1]:  # 0=BACK, 1=FRONT-PAWNS
        for _col in range(board.width):

            _pos = board.init_pos(_player,_row,_col)

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

            try:
                pieces.append(piece)
            except:
                print _player, _row, _col
            
            board.new_pos(row = _pos[0] ,col = _pos[1] )            

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

#POS = (1,1)
#piece = Piece(b_white = True, pos = POS )
#board.new_pos(row = POS[0] ,col = POS[1] )
#board.print_board()

print board.width







    