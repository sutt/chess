import requests
import subprocess
import time
from utils import alphamove_to_posmove
from utils import pos_to_alphanum

def demo_request():
    r = requests.get("http://127.0.0.1:5000/")
    print r.text


class StockfishNetworking():
    ''' make http request to flask server in ../stockfish/api/ 
        need to:
            set_position/move1-move2-move3...-moveN
            best_move/defaults
    '''
    def __init__(self, b_launch_server = False, b_read_server_stdout = False):
        
        self.url_root = "http://127.0.0.1:5000/"
        
        self.serverProcess = None
        
        if b_launch_server:

            self.serverProcess = subprocess.Popen(
                            [
                            'c:/windows/sysnative/bash.exe'
                            ,'-c'
                            ,"printenv"
                            ,"&&"
                            ,"source"
                            , "~/.customprofile"
                            ,"&&"
                            ,"flask"
                            ,"run"
                            ]
                    # ,stdin=subprocess.PIPE
                    # ,stdout=subprocess.PIPE
                    )

            if b_read_server_stdout:
                
                #TODO - do a tmp file thing with threading/readline
                # This is going to be tough b/c stdout PIPE
                # doesnt work from wsl->win. Can do > tmp.txt

                print 'Setting up Stockfish Server...'
                b_idle = True
                while(b_idle):
                    line = self.serverProcess.stdout.readline()
                    if line.find("Running on http") > -1:
                        b_idle = False
                        #TODO - parse this line for ip/port
                        print 'Server setup!'
                        
            else:
                print 'Sleeping 4 seconds to launch stockfish server...'
                time.sleep(4)
                print 'Server initialized'

    def get_move(self, list_log_moves, available_moves):
        ''' Args:
              list_log_moves:   list of MoveCode's
              available_moves:  moves from play(), list of MoveCode's
            Returns:
              move: one MoveCode (or None on failed validation)
        '''

        str_log = self._movecodelist_to_movestr(list_log_moves)

        if str_log != "":                   #disregard for first ply
            if not(self._set_position(str_log)):
                print 'set_position http call failed'
                return None

        str_best_move = self._get_best_move()
        if str_best_move == "":
            print 'best_position http call failed'
            return None
            
        movetuple_best_move = self._movestr_to_movecode(str_best_move)
        
        for _m in available_moves:
            if movetuple_best_move == (_m.pos0, _m.pos1):
                return _m

        return None     #Error - movetuple is not in available_moves

    
    def _set_position(self, str_log):
        url = self.url_root
        url += "set_position/"
        url += str_log
        r = requests.get(url)
        if r.status_code == 200:
            return True
        else:
            return False


    def _get_position(self):
        pass


    def _get_best_move(self):
        url = self.url_root
        url += "best_move/default"
        r = requests.get(url)
        if r.status_code == 200:
            return r.content
        else:
            return ""

    @staticmethod
    def _movecodelist_to_movestr(list_log_moves):
        ''' input:  list_log_moves: list of MoveCode's
            output: string of alphanum's (or "" for empty list)
            example:
                [
                  MoveHolder(pos0=(6, 4), pos1=(4, 4), code=0)
                 ,MoveHolder(pos0=(1, 4), pos1=(4, 3), code=0)
                ]
              ->
                "e2e4-g7g5"
        '''
        temp = [
                str(pos_to_alphanum(elem.pos0)) + 
                str(pos_to_alphanum(elem.pos1))
                for elem in list_log_moves
                ]
        logstr = '-'.join(temp)
        return logstr

    @staticmethod
    def _movestr_to_movecode(str_move):
        ''' input: str of two alphanums corresponsding to pos0 and pos1
            output: 2-ple of 2-ple's corresponding int coords for pos0 and pos1
            example: "e2e4" -> ((6,4), (4,4))
        '''
        space_sep_move = str_move[:2] + " " + str_move[2:]
        return alphamove_to_posmove(space_sep_move)

    def __del__(self):
        if self.serverProcess is not None:
            print 'tearing down StockfishNetwork server'
            self.serverProcess.kill()
    


if __name__ == "__main__":
    pass    
    # sn = StockfishNetworking(b_launch_server=True)
    # print 'awaiting...'
    # time.sleep(5)
    # print 'done'

    
    #TODO - play stockfish right here




from datatypes import moveHolder, moveAHolder
Move = moveHolder()
MoveA = moveAHolder()

def test_sn_movecodelist_to_movestr():
    
    sn = StockfishNetworking    #note: no need to instantiate

    list_move_1 = [
         Move(pos0 = (6,4), pos1 = (4,4), code = 0)
        ,Move(pos0 = (1,4), pos1 = (3,4), code = 0)
    ]

    str_alpha_1 = sn._movecodelist_to_movestr(list_move_1)

    assert str_alpha_1 == "e2e4-e7e5"

    list_move_blank = []

    str_alpha_blank = sn._movecodelist_to_movestr(list_move_blank)

    assert str_alpha_blank == ""

    #TODO - convert alphanum moves to movecode
    #TODO - castling
    #TODO - enpassant


def test_sn_movestr_to_movecode():

    sn = StockfishNetworking
    assert sn._movestr_to_movecode("e2e4") == ((6,4), (4,4))
    assert sn._movestr_to_movecode("a2e8") == ((6,0), (0,4))

def test_sn_launch_server_1():
    ''' test that the module can launch the flask server inside WSL '''
    
    sn = StockfishNetworking(b_launch_server=True)

    r = requests.get("http://127.0.0.1:5000/")

    assert r.content == "Hello, Flask! <br> New Line?"

#TODO - test that it's in linux
#TODO - test that it's 


    
def test_sn_get_best_move_1():
    ''' basic example    '''
    
    #e4 e5 game
    list_log_moves = [
         Move(pos0 = (6,4), pos1 = (4,4), code = 0)
        ,Move(pos0 = (1,4), pos1 = (3,4), code = 0)
    ]

    #available moves for white; ply=3
    MoveHolder = moveHolder()
    available_moves = [MoveHolder(pos0=(7, 1), pos1=(5, 2), code=0), MoveHolder(pos0=(7, 1), pos1=(5, 0), code=0), MoveHolder(pos0=(7, 3), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 3), pos1=(5, 5), code=0), MoveHolder(pos0=(7, 3), pos1=(4, 6), code=0), MoveHolder(pos0=(7, 3), pos1=(3, 7), code=0), MoveHolder(pos0=(7, 4), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 5), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 5), pos1=(5, 3), code=0), MoveHolder(pos0=(7, 5), pos1=(4, 2), code=0), MoveHolder(pos0=(7, 5), pos1=(3, 1), code=0), MoveHolder(pos0=(7, 5), pos1=(2, 0), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 7), code=0), MoveHolder(pos0=(7, 6), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 0), pos1=(5, 0), code=0), MoveHolder(pos0=(6, 0), pos1=(4, 0), code=0), MoveHolder(pos0=(6, 1), pos1=(5, 1), code=0), MoveHolder(pos0=(6, 1), pos1=(4, 1), code=0), MoveHolder(pos0=(6, 2), pos1=(5, 2), code=0), MoveHolder(pos0=(6, 2), pos1=(4, 2), code=0), MoveHolder(pos0=(6, 3), pos1=(5, 3), code=0), MoveHolder(pos0=(6, 3), pos1=(4, 3), code=0), MoveHolder(pos0=(6, 5), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 5), pos1=(4, 5), code=0), MoveHolder(pos0=(6, 6), pos1=(5, 6), code=0), MoveHolder(pos0=(6, 6), pos1=(4, 6), code=0), MoveHolder(pos0=(6, 7), pos1=(5, 7), code=0), MoveHolder(pos0=(6, 7), pos1=(4, 7), code=0)]

    sn = StockfishNetworking(b_launch_server=True)
    best_move = sn.get_move(list_log_moves, available_moves )

    assert best_move == Move(pos0 = (6,3), pos1 = (4,3), code = 0)

# def test_demo_fail():
#     assert False

#TODO - a ply=1 game

#TODO - a get position example
