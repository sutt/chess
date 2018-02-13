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
                ,**kwargs
                ):
        
        self.b_show_opponent = b_show_opponent
        
        self.board_pre_turn_oppoenent = b_show_opponent
        self.board_pre_turn = False

        self.annotate = None

        #TODO - eliminate misc and methods
        self.misc = None

        self.width = 8

    
    def start_annotate(self,**kwargs):
        self.annotate = [["~" for i in range(self.width)] for j in range(self.width)]

    def start_misc(self,**kwargs):
        self.misc = [[0 for i in range(self.width)] for j in range(self.width)]

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

    def mark_misc(self,pos,**kwargs):
        self.misc[pos[0]][pos[1]] = kwargs.get('val',1)

    def mark_all_misc(self,list_list_pos,**kwargs):
        for list_pos in list_list_pos:
            for pos in list_pos:
                self.misc[pos[0]][pos[1]] = 1
                
    def mark_list_misc(self,list_pos,**kwargs):
        for pos in list_pos:
            self.misc[pos[0]][pos[1]] = kwargs.get('val',1)
    


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

    
    def print_board_letters(self, board, pieces, b_lower_black = False):
        
        self.start_annotate()
        
        for p in pieces:
            self.mark_annotate(p, disambiguate = True, b_lower_case = b_lower_black)
        
        self.print_board(b_annotate = True, b_show_grid = True)    


    def print_turn(self, board, pieces, player, **kwargs):

        #TODO - add these conditionals
        # if (self.board_pre_turn and 
        #     ((player in self.manual_control) or 
        #         self.board_pre_turn_oppoenent)):
        
        if True:

            self.print_board_letters(board, pieces, True)
