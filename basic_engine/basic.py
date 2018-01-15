import sys

BOARD_WIDTH = 8

class Board:
    
    def __init__(self):
        self.width = BOARD_WIDTH
        self.data = [[0] * self.width] * self.width

    def new_pos(self,row,col,**kwargs):
        self.data[row,col] = 1

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

    def __init__(self,b_white, pos, ):
        self.white = b_white
        self.alive = True
        self.pos = pos

    def get_available_moves(self,current_board):
        moves = []
        #b_blocking = False # for Knight only
        #check_if_moving_causes_check()
        return moves

class Pawn(Piece):
    
    def __init__(self,init_col):
        self.pos = (2,init_col)
        self.en_passant_vulnerable = False
        

class King(Piece):
    
    def __init__(self):
        self.pos = (1,5)
        self.king_can_castle = True


class Rook(Piece):
    
    def __init__(self,init_col,):
        self.pos = (1,init_col)
        self.rook_can_castle = True

#class Bishop(Piece):   
#class Queen(Piece):

board = Board()
board.print_board()
    

    