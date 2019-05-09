import os, sys, math
import requests
import subprocess
import time
from .utils import find_app_path_root
from .utils import alphamove_to_posmove
from .utils import pos_to_alphanum

def demo_request():
    r = requests.get("http://127.0.0.1:5000/")
    print(r.text)


class StockfishNetworking():
    ''' make http request to flask server in ../stockfish/api/ 
        need to:
            set_position/move1-move2-move3...-moveN
            best_move/defaults
    '''
    def __init__(self, b_launch_server = False, b_read_stderr = True):
        
        self.url_root = "http://127.0.0.1:5000/"
        
        self.TMP = "stderr.txt"
        
        self.serverProcess = None

        if b_launch_server:

            if b_read_stderr:
                if self._del_tmp_file():
                    _stderr = open(os.path.join(os.path.dirname(__file__), self.TMP), 'w')
                else:
                    b_read_stderr = False
                    _stderr = subprocess.PIPE
            else:
                _stderr = subprocess.PIPE

            bash_path = 'c:/windows/sysnative/bash.exe'
            if math.log(sys.maxsize) > 22:   # 32-bit~21.4; 64-bit~43.7
                bash_path = 'c:/windows/system32/bash.exe'
                
            self.serverProcess = subprocess.Popen(
                            [
                             bash_path
                            ,'-c'
                            ,"printenv"
                            ,"&&"
                            ,"source"
                            , "~/.customprofile"
                            ,"&&"
                            ,"flask"
                            ,"run"
                            ]
                    
                    ,stdin=subprocess.PIPE
                    ,stdout=subprocess.PIPE
                    ,stderr=_stderr
                    
                    ,cwd = os.path.join(
                                         find_app_path_root(__file__)
                                        ,'stockfish'
                                        ,'api'
                                        )
                    )

            if b_read_stderr:

                _stderr.close()
                
                t0 = time.time()

                while(True):
                    
                    with open(os.path.join(os.path.dirname(__file__)
                                            ,self.TMP)
                                ,'r') as f_stderr:
                        
                        try:    
                            if time.time() - t0 > 5:
                                break
                            
                            line = f_stderr.readline()
                            if line.find("Running on http") > -1:
                                self.url_root = self.parse_stderr_url(line)
                                break

                        except:
                            break
                
                if not(self._check_server_is_up()):
                    print('failed to validate the stockfish server is up.')
                else:
                    self._del_tmp_file()
                    print('  server setup in secs: %s\n' % str(time.time() - t0)[:4])

            else:
                print('Sleeping 4 seconds to launch stockfish server...')
                time.sleep(4)
                print('Server initialized')

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
                print('set_position http call failed')
                return None

        str_best_move = self._get_best_move()
        if str_best_move == "":
            print('best_position http call failed')
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
            content = r.content
            if sys.version_info.major == 3:
                content = content.decode()
            return content
        else:
            return ""

    @staticmethod
    def _parse_stderr_url(line):
        ''' take the stderr output by flask and find the relevant parts in the string'''
        ip_start =  line.find("//")
        ip_end =    line[ip_start:].find(":") + ip_start
        ip = line[ip_start+2:ip_end]

        port_start = ip_end + 1
        port_end =   port_start + line[port_start:].find("/")
        port = line[port_start:port_end]
        
        url_root = "http://" + ip + ":" + port + "/"
        return url_root


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

    def _check_server_is_up(self):
        ''' do a simple check if server is takign requests. Return True if it does '''
        try:
            r = requests.get(self.url_root + 'check_server_is_up/')
            content = r.content
            if sys.version_info.major == 3:
                content = content.decode()
            if content == 'ok':
                return True
        except:
            pass
        return False

    
    def _del_tmp_file(self):
        ''' remove the stderr.txt tmp file return true is succesful '''
        if self.TMP in os.listdir(os.path.dirname(__file__)):
            try:
                os.remove(os.path.join(os.path.dirname(__file__), self.TMP))
                return True
            except:
                return False
        else:
            return True

    def __del__(self):
        if self.serverProcess is not None:
            print('tearing down StockfishNetwork server')
            self.serverProcess.kill()
    


if __name__ == "__main__":
    pass    
    # sn = StockfishNetworking(b_launch_server=True)
    # print 'awaiting...'
    # time.sleep(5)
    # print 'done'



from .datatypes import moveHolder, moveAHolder
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


def test_parse_flask_stderr():

    line = """ * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)"""
    assert StockfishNetworking._parse_stderr_url(line) == "http://127.0.0.1:5000/"
     


def test_sn_launch_server_1():
    ''' test that the module can launch the flask server inside WSL '''
    
    sn = StockfishNetworking(b_launch_server=True)

    r = requests.get("http://127.0.0.1:5000/")

    content = r.content
    if sys.version_info.major == 3:
        content = content.decode()
    assert content == "Hello, Flask! <br> New Line?"


def test_sn_launch_server_2():
    ''' test that the module launches the server inside WSL '''
    
    sn = StockfishNetworking(b_launch_server=True)

    r = requests.get("http://127.0.0.1:5000/check_server_params/")

    content = r.content
    if sys.version_info.major == 3:
        content = content.decode()
    assert content == "posix|/mnt/c/Users/wsutt/Desktop/files/chess/stockfish/api|python2"
    
    
def test_sn_get_best_move_1():
    ''' basic example of bestmove on ply 3 '''
    
    #e4 e5 game
    list_log_moves = [
         Move(pos0 = (6,4), pos1 = (4,4), code = 0)
        ,Move(pos0 = (1,4), pos1 = (3,4), code = 0)
    ]

    #available moves for white; ply=3
    MoveHolder = moveHolder()
    available_moves = [MoveHolder(pos0=(7, 1), pos1=(5, 2), code=0), MoveHolder(pos0=(7, 1), pos1=(5, 0), code=0), MoveHolder(pos0=(7, 3), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 3), pos1=(5, 5), code=0), MoveHolder(pos0=(7, 3), pos1=(4, 6), code=0), MoveHolder(pos0=(7, 3), pos1=(3, 7), code=0), MoveHolder(pos0=(7, 4), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 5), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 5), pos1=(5, 3), code=0), MoveHolder(pos0=(7, 5), pos1=(4, 2), code=0), MoveHolder(pos0=(7, 5), pos1=(3, 1), code=0), MoveHolder(pos0=(7, 5), pos1=(2, 0), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 7), code=0), MoveHolder(pos0=(7, 6), pos1=(6, 4), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 0), pos1=(5, 0), code=0), MoveHolder(pos0=(6, 0), pos1=(4, 0), code=0), MoveHolder(pos0=(6, 1), pos1=(5, 1), code=0), MoveHolder(pos0=(6, 1), pos1=(4, 1), code=0), MoveHolder(pos0=(6, 2), pos1=(5, 2), code=0), MoveHolder(pos0=(6, 2), pos1=(4, 2), code=0), MoveHolder(pos0=(6, 3), pos1=(5, 3), code=0), MoveHolder(pos0=(6, 3), pos1=(4, 3), code=0), MoveHolder(pos0=(6, 5), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 5), pos1=(4, 5), code=0), MoveHolder(pos0=(6, 6), pos1=(5, 6), code=0), MoveHolder(pos0=(6, 6), pos1=(4, 6), code=0), MoveHolder(pos0=(6, 7), pos1=(5, 7), code=0), MoveHolder(pos0=(6, 7), pos1=(4, 7), code=0)]

    sn = StockfishNetworking(b_launch_server=True)
    best_move = sn.get_move(list_log_moves, available_moves)

    assert best_move == Move(pos0 = (6,3), pos1 = (4,3), code = 0)


def test_sn_best_move_2():
    ''' basic example of bestmove on ply 1 '''
    
    #start-position game
    list_log_moves = []

    #available moves for white; ply=1
    MoveHolder = moveHolder()
    available_moves = [MoveHolder(pos0=(7, 1), pos1=(5, 2), code=0), MoveHolder(pos0=(7, 1), pos1=(5, 0), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 7), code=0), MoveHolder(pos0=(7, 6), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 0), pos1=(5, 0), code=0), MoveHolder(pos0=(6, 0), pos1=(4, 0), code=0), MoveHolder(pos0=(6, 1), pos1=(5, 1), code=0), MoveHolder(pos0=(6, 1), pos1=(4, 1), code=0), MoveHolder(pos0=(6,2), pos1=(5, 2), code=0), MoveHolder(pos0=(6, 2), pos1=(4, 2), code=0), MoveHolder(pos0=(6, 3),pos1=(5, 3), code=0), MoveHolder(pos0=(6, 3), pos1=(4, 3), code=0), MoveHolder(pos0=(6, 4), pos1=(5, 4), code=0), MoveHolder(pos0=(6, 4), pos1=(4, 4), code=0), MoveHolder(pos0=(6, 5), pos1=(5, 5), code=0), MoveHolder(pos0=(6, 5), pos1=(4, 5), code=0), MoveHolder(pos0=(6, 6), pos1=(5, 6), code=0), MoveHolder(pos0=(6, 6), pos1=(4, 6), code=0), MoveHolder(pos0=(6, 7), pos1=(5, 7), code=0), MoveHolder(pos0=(6, 7), pos1=(4, 7), code=0)]

    sn = StockfishNetworking(b_launch_server=True)
    best_move = sn.get_move(list_log_moves, available_moves)

    assert best_move in [Move(pos0 = (6,4), pos1 = (4,4), code = 0),   # e4
                         Move(pos0 = (6,3), pos1 = (4,3), code = 0),   # d4
                        ]

#TODO - a get position example
