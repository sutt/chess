import sys, copy

BOARD_WIDTH = 8

class Board:
    
    def __init__(self):
        self.width = BOARD_WIDTH
        self.data = [[0 for i in range(self.width)] for j in range(self.width)]
        

    def new_pos(self,row,col,**kwargs):
        self.data[row][col] = 1

    def mark_annotate(self,**kwargs):
        pass

    def init_pos(self,player,row,col):
        _row =  (self.width-1)*player +  -1*row if player else row
        _col = col
        return _row, _col

    def get_diagonals(self,pos, spaces = 7):
        """order them by closest to furthest,
           so that you can filter based on blockers"""
        diagonals = []
        return diagonals

    def get_ups_and_acrosses(self,pos):
        pass
        
    def get_two_by_ones(self,pos):
        pass

    def print_board(self):
        out = ""
        for row in self.data:
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

for p in pieces:
    print str(p.white) + " " + str(p.__class__.__name__) + " " + str(p.pos)



pawn = Pawn(True,(1,1))
print pawn.pos
print pawn.en_passant_vulnerable
print pawn.__class__.__name__

#POS = (1,1)
#piece = Piece(b_white = True, pos = POS )
#board.new_pos(row = POS[0] ,col = POS[1] )
#board.print_board()









    