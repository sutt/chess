
class Board:
    
    def __init__():
        self.data = None

    def get_diagonals(pos, spaces = 7):
        """order them by closest to furthest,
           so that you can filter based on blockers"""
        diagonals = []
        return diagonals

    def get_ups_and_acrosses(pos):
        pass
        
    def get_two_by_ones(pos):
        pass

class Piece:

    def __init__(b_white, pos, ):
        self.white = b_white
        self.alive = True
        self.pos = pos

    def get_available_moves():
        
        moves = []
        #b_blocking = False # for Knight only
        #check_if_moving_causes_check()
        return moves

class Pawn(Piece):
    
    def __init__(init_col):
        self.pos = (2,init_col)
        self.en_passant_vulnerable = False
        

class King(Piece):
    
    def __init__():
        self.pos = (1,5)
        self.king_can_castle = True


class Rook(Piece):
    
    def __init__(init_col,):
        self.pos = (1,init_col)
        self.rook_can_castle = True

class Bishop(Piece):
    
class Queen(Piece):
    
    