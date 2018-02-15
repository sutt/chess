import sys

def print2(data, arg1="", arg2="", arg3="",arg4=""):
    '''for VS-code debugging issue: https://github.com/Microsoft/vscode/issues/36630'''
    out = str(data) + str(arg1) + str(arg2) + str(arg3) + str(arg4)
    try:
        print data
    except:
        pass

class Display:
    
    def __init__(self
                ,b_show_opponent = False
                ,b_never_print = False
                ,b_always_print = False
                ,manual_control = ()
                ,**kwargs
                ):
        
        self.b_show_opponent = b_show_opponent
        self.b_never_print = b_never_print
        self.b_always_print = b_always_print
        self.manual_control = manual_control

        self.annotate = None
        self.width = 8

    
    def start_annotate(self,**kwargs):
        self.annotate = [["~" for i in range(self.width)] for j in range(self.width)]

    def mark_annotate(self, piece, **kwargs):
        _pos = piece.pos
        _symbol = str.upper(str(piece.__class__.__name__)[0])
        
        if kwargs.get('disambiguate', False): 
            if str(piece.__class__.__name__) == "Knight":
                _symbol = "N"
        
        if kwargs.get('b_lower_case', False):
            if not(piece.white):
                _symbol = str.lower(_symbol)
        
        self.annotate[_pos[0]][_pos[1]] = _symbol


    def print_board(self,b_annotate = False ,b_misc = False
                        ,b_player_data = False, b_show_grid = False
                        ,b_abs = False):

        if b_annotate: 
            p_data = self.annotate
        
        out = ""
        
        if b_show_grid:
            out += "   " + " ".join(map(lambda i: str(i), range(1,9)))
            out += "\n"
            out += "\n"
            row_grid = "ABCDEFGH"

        for i,row in enumerate(p_data):
            if b_abs:
                s_row = map(lambda int_i: str(abs(int_i)),row)
            else:
                s_row = map(lambda int_i: str(int_i),row)
            if b_show_grid:
                out += row_grid[i]
                out += "  "
            out += " ".join(s_row)
            out += "\n"        
        print2(out)

    
    def print_board_letters(self, pieces, b_lower_black = False):
        ''' Use pieces to display a graphical display to console.
            [b_lower_black]: black pieces in lower case.'''

        self.start_annotate()
        
        for p in pieces:
            self.mark_annotate(p, disambiguate = True, b_lower_case = b_lower_black)
        
        self.print_board(b_annotate = True, b_show_grid = True)    


    def print_turn(self, pieces, player, **kwargs):
        ''' Called from play(), decides when to print board to console.'''
        if ((self.b_always_print) or
            ((player in self.manual_control) or self.b_show_opponent)
            ) and not(self.b_never_print):
            
        
            self.print_board_letters(pieces, True)
