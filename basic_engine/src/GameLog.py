import time, copy, json
from utils import parse_pgn_instructions


class GameSchema:
    
    '''Holds, Loads, Converts records of games'''

    def __init__(self):
        
        self.pgn_instructions = None            #str
        self.pgn_parsed = None                  #parsed triplets
        
        self.pgn_check_schedule = None
        self.pgn_capture_schedule = None
        self.pgn_mate_turn = None               #as an i_turn
        self.pgn_player_last_move = None        #"who didnt resign" 0=white, 1=black
        
        self.pgn_s_outcome = None               #str from pgn file
        self.pgn_outcome_code = None
        
        self.doublet_instructions = None

    def to_json(self,**kwargs):
        
        data = {}

        data['pgn_instructions'] = self.pgn_instructions

        data['pgn_check_schedule'] = self.pgn_check_schedule
        data['pgn_capture_schedule'] = self.pgn_capture_schedule
        data['pgn_mate_turn'] = self.pgn_mate_turn
        data['pgn_player_last_move'] = self.pgn_player_last_move

        data['pgn_s_outcome'] = self.pgn_s_outcome
        
        return json.dumps(data)
        
    def from_json(self,json_data):
        
        k = 'pgn_instructions'
        if json_data.has_key(k):
            self.pgn_instructions = json_data[k]

        k = 'pgn_check_schedule'
        if json_data.has_key(k):
            self.pgn_check_schedule = json_data[k]

        k = 'pgn_capture_schedule'
        if json_data.has_key(k):
            self.pgn_capture_schedule = json_data[k]

        k = 'pgn_mate_turn'
        if json_data.has_key(k):
            self.pgn_mate_turn = json_data[k]

        k = 'pgn_player_last_move'
        if json_data.has_key(k):
            self.pgn_player_last_move = json_data[k]

        k = 'pgn_s_outcome'
        if json_data.has_key(k):
            self.pgn_s_outcome = json_data[k]
        
    
    def set_pgn_instructions(self, s_instructions):
        self.pgn_instructions = s_instructions

    def set_pgn_s_outcome(self, s_outcome):
        self.pgn_s_outcome = s_outcome

    def get_instructions(self):
        return str(self.pgn_instructions)   #convert from unicode

    def get_pgn_parsed(self):
        return copy.copy(self.pgn_parsed)

    def get_check_schedule(self):
        return copy.copy(self.pgn_check_schedule)
        
    def get_capture_schedule(self):
        return copy.copy(self.pgn_capture_schedule)

    def get_mate_turn(self):
        return self.pgn_mate_turn

    def get_s_outcome(self):
        return self.pgn_s_outcome

    def get_player_last_move(self):
        return self.pgn_player_last_move

    
    def parse_pgn_instructions(self
                                ,b_check_schedule=False
                                ,b_capture_schedule=False
                                ,b_mate_turn=False
                                ,b_player_last_move=False
                                ):

        #The main parsing: pgn triplets
        self.pgn_parsed = parse_pgn_instructions(self.pgn_instructions)
        
        #Secondary parsings
        if b_check_schedule:
            self.pgn_check_schedule = parse_pgn_instructions(
                                        self.pgn_instructions
                                        ,b_check_schedule=True
                                        )

        if b_capture_schedule:
            self.pgn_capture_schedule = parse_pgn_instructions(
                                        self.pgn_instructions
                                        ,b_capture_schedule=True
                                        )

        if b_mate_turn:
            self.pgn_mate_turn = parse_pgn_instructions(
                                        self.pgn_instructions
                                        ,b_mate_turn=True
                                        )
        if b_player_last_move:
            self.pgn_player_last_move = int(not(len(self.pgn_parsed) % 2))
    
    
    def all_parse_pgn_instructions(self):
        
        self.parse_pgn_instructions(b_check_schedule=True
                                    ,b_capture_schedule=True
                                    ,b_mate_turn=True
                                    ,b_player_last_move=True
                                    )

    @staticmethod
    def iturn_to_pgnturn(i_turn):
        ''' returns: (pgn_turn (int), player (int [0 or 1]) 
                                    player: 0=white,1=black
        '''
        player_int = int(not(i_turn % 2))
        pgn_turn = ((i_turn - 1) / 2) + 1
        return (pgn_turn, player_int)

    @staticmethod
    def pgnturn_to_iturn(pgn_turn, player_int):
        ''' returns: i_turn (int)
            input: pgn_turn (int), player_int (int) 0=white,1=black
        '''
        return (pgn_turn * 2) - int(not(bool(player_int)))
        

    #TODO - create pgn from game record

    def parse_full_pgn_markdown(self,**kwargs):
        pass

    def make_doublet_from_pgn(self):
        pass


def test_schema_turn_convert():
    
    gs = GameSchema()
    
    assert gs.pgnturn_to_iturn(4,1) == 8 
    assert gs.pgnturn_to_iturn(4,0) == 7
    assert gs.pgnturn_to_iturn(1,0) == 1

    assert gs.iturn_to_pgnturn(1) == (1,0)
    assert gs.iturn_to_pgnturn(2) == (1,1)
    assert gs.iturn_to_pgnturn(17) == (9,0)
    assert gs.iturn_to_pgnturn(16) == (8,1)
    
def test_schema_check_schedule():
    
    gs = GameSchema()
    
    s_pgn = '1. c4 Nf6 2. Nc3 g6'
    gs.set_pgn_instructions(s_pgn)
    gs.all_parse_pgn_instructions()
    assert gs.get_check_schedule() == [False, False, False, False]

    s_pgn = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'
    gs.set_pgn_instructions(s_pgn)
    gs.parse_pgn_instructions(b_check_schedule=True)

    base = [False] * (60*2 + 1)
    base[83 - 1] = True
    base[92 - 1] = True
    base[100 - 1] = True
    base[105 - 1] = True
    base[108 - 1] = True
    base[111 - 1] = True
    base[113 - 1] = True
    base[119 - 1] = True
    base[121 - 1] = True

    assert gs.get_check_schedule() == base

def test_schema_capture_schedule():
    
    gs = GameSchema()

    s_pgn = '5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4'
    gs.set_pgn_instructions(s_pgn)
    gs.all_parse_pgn_instructions()

    assert gs.get_capture_schedule() == [False, False, False, False, False, True, True]

def test_schema_mate_turn():
    pass

def test_schema_player_last_move():
    
    gs = GameSchema()

    s_pgn = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'
    gs.set_pgn_instructions(s_pgn)
    gs.all_parse_pgn_instructions()

    assert gs.get_player_last_move() == 0


class GameLog:

    ''' Holds all data collected within the game.
        Used as data-structure when returned from a test. '''

    def __init__(self,**kwargs):
        
        #TODO - remove these
        self.board_pre_turn = True
        self.board_pre_turn_oppoenent = kwargs.get('b_log_show_opponent', False)
        self.manual_control = kwargs.get('manual_control', ())
        
        self.b_check_schedule = kwargs.get('b_check_schedule', False)
        self.log_check_schedule = []
        
        self.b_log_move = kwargs.get('b_log_move', False)
        self.log_move = []
        
        self.b_num_available = kwargs.get('b_num_available',False)
        self.log_num_available = []
        
        self.b_turn_time = kwargs.get('b_turn_time',False)
        self.log_turn_time = []
        self.t0 = time.time()

    def set_t0(self):
        self.t0 = time.time()

    def add_turn_log(self
                     ,move
                     ,num_available = 0
                     ,b_check = False
                     ):
        
        '''each turn append a data element on to each of these logs'''

        if self.b_log_move:
            self.log_move.append(move)
        
        if self.b_num_available:
            self.log_num_available.append(num_available)

        if self.b_check_schedule:
            self.log_check_schedule.append(b_check)
        
        if self.b_turn_time:
            _time = time.time() - self.t0
            self.log_turn_time.append(_time)
            self.t0 = time.time()


    def get_log_move(self):
        return copy.deepcopy(self.log_move)

    def get_log_num_available(self):
        return copy.deepcopy(self.log_num_available)

    def get_log_turn_time(self):
        return copy.deepcopy(self.log_turn_time)

    def get_log_check_schedule(self):
        return copy.copy(self.log_check_schedule)

    
  
