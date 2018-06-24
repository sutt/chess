import sys
from time import time
import json
import pprint
import copy

sys.path.append('../')

from src.main import Game
from utils import convert_pgn_to_a1

from schema_module import TimeAnalysisSchema
from schema_module import TurnAttributeSchema

from db_module import TasPerfDB


# Different Experiments --------------------------------------------------
#  

def game_init(s_instructions
                ,b_turn_log=False
                ,b_init_zero_move=False
                ,b_pgn_use=False
                ,b_pgn_convert=False
                ):
    ''' This consturcts the Game object so it doesnt get counted in timer. '''

    if b_pgn_use:
        s_instruct = ""
        s_pgn_instruct = s_instructions
    elif b_pgn_convert:
        s_instruct = convert_pgn_to_a1(s_instructions)
        s_pgn_instruct = ""
    else:
        s_instruct = s_instructions
        s_pgn_instruct = ""
    
    game = Game(s_instructions = s_instruct
                ,s_pgn_instructions = s_pgn_instruct
                ,b_log_turn_time = b_turn_log
                ,b_log_num_available=b_turn_log
                )
    
    if b_init_zero_move:
        game.initialize(init_to_save=True)
        
    return game

def select_function(s_function, game, b_init_load=False):
    ''' input:  s_function (string) - choses param's for play()
                game        (obj)   - a Game obj with insturction and initd already
                b_init_load (bool)  - pass in b_init_load as kwarg to play()
        output: a GameLog or None
         '''
    
    def run_play(kw_pass_in):
        if b_init_load:
            kw_pass_in['init_load'] = True
        game.play(**kw_pass_in)
    
    def _(*args, **kw):
        run_play(kw)
    
    def __(function_return_params):
        return function_return_params(s_function)

    @__
    def return_params(s_function):
        
        if s_function == "baseline_nk":
            
            return _(check_for_check=False, filter_check_opt=False)    

        if s_function == "baseline_yk":
            
            return _(check_for_check=True, filter_check_opt=False)    
            
        if s_function == "naive_nk":

            return _(check_for_check=False, filter_check_opt=False, filter_check_naive=True)

        if s_function == "naive_yk":

            return _(check_for_check=True, filter_check_opt=False, filter_check_naive=True)

        if s_function == "opt_nk":
        
            return _(check_for_check=False, filter_check_opt=True)

        if s_function == "opt_yk":
            
            return _(check_for_check=True, filter_check_opt=True)

        if s_function == "var0":
            
            return _(filter_check_opt=False, filter_check_test_copy=True)

        if s_function == "var1":
            
            return _(filter_check_opt=False, filter_check_test_copy_apply=True)

        if s_function == "var2":
                
            return _(filter_check_opt=False, filter_check_test_copy_apply_2=True)

        if s_function == "var3":
                
            return _(filter_check_opt=False, filter_check_test_copy_apply_3=True)

        if s_function == "var4":
                
            return _(filter_check_opt=False, filter_check_test_copy_opt=True)

    # the reference to this object hasnt changed
    return game



#Pretty Print Helper Functions ------------------

def align_col(s_line, chars_=10, r_align=True):
    
    len_line = len(s_line)

    if len_line < chars_:
        add_chars_left = chars_ - len_line
        out = (" " * add_chars_left)
        out += s_line
    elif len_line > chars_:
        out = s_line[:chars_]
    else:
        out = s_line

    return out

def char_round(s_line, chars_):
    return str(s_line)[:chars_]

def print_formatted_results(dims_out, data):
    
    #print col heading
    s_row = ""
    for col in dims_out:
        s_row += align_col(col[0], chars_=col[1] )
        s_row += align_col('', chars_ = col[2])
    print s_row

    #print data
    for row in data:
        
        s_row = ""

        for i_col, col in enumerate(row):
            
            _format = dims_out[i_col]
            _col_len = _format[1]
            _spacer_len = _format[2]
            _char_round = _format[3]

            s_col = str(col)
            s_col = char_round(s_col, _char_round)
            s_col = align_col(s_col, _col_len)

            s_row += s_col

            s_row += align_col('', chars_=_spacer_len)

        print s_row

#Interpret Functions (slice and calc on results) -------------------------

def interpret_basic_data(results):
    '''Build a five col printout for avg trial time of different tests'''
    temp = [0 for i in range(len(results.keys()))]
    for k in results.keys():
        d_test = results[k]
        test_name = str(k)
        order_test = d_test['order']
        n_test = d_test['n']
        totaltime_test = d_test['total_time']
        avgtime_test = float(totaltime_test) / float(n_test)

        test_info = [
                        test_name
                        ,avgtime_test
                        ,"n/a"          #placeholder for Multiplier
                        ,n_test
                        ,totaltime_test
                    ]

        temp[order_test] = test_info
    #Build X-diff column
    avgtime_col = 1
    xdiff_col = 2
    avgtime_baseline = temp[0][avgtime_col]
    for i in range(1,len(temp)):
        if avgtime_baseline == 0:
            xdiff = float(0)
        else:
            xdiff = float(temp[i][avgtime_col]) / float(avgtime_baseline)
        s_xdiff = str(xdiff)
        temp[i][xdiff_col] = s_xdiff
    return temp

def interpret_variation_data(results):
    '''Find Min/Max from the dataset'''
    temp = [0 for i in range(len(results.keys()))]
    for k in results.keys():
        d_test = results[k]
        test_name = str(k)
        order_test = d_test['order']
        n_test = d_test['n']
        totaltime_test = d_test['total_time']
        avgtime_test = float(totaltime_test) / float(n_test)

        list_trial_time = d_test['trial_time']
        min_test = min(list_trial_time)
        max_test = max(list_trial_time)

        test_info = [
                        test_name
                        ,avgtime_test
                        ,min_test        
                        ,max_test
                    ]

        temp[order_test] = test_info
    return temp

def interpret_turn_time_data(results):

    turn_time_data = [ [], [] ]

    for k in results.keys():
        
        data_test = results[k]

        test_name = str(k)

        n_test = data_test['n']

        # TODO - remove this section, plus its buggy
        order_test = data_test['order']
        if order_test == 0:
            print 'Test A: ', test_name
        else:
            print 'Test B: ', test_name
            print 'N tests: ', str(n_test), '\n'

        list_trial_times = data_test['turn_time']
        list_num_moves = data_test['num_available']
        
        #Sum each jth element
        n_j = len(list_trial_times[0])
        turn_times = []
        for j in range(n_j):
            _tmp = 0
            for _trial_time in list_trial_times:
                _tmp += _trial_time[j]
            turn_times.append(_tmp)

        n_test = data_test['n']

        turn_times_avg = [float(x) / float(n_test) for x in turn_times]
        turn_times_avg_ms = [x * float(1000) for x in turn_times_avg]

        turn_time_data[order_test].extend(turn_times_avg_ms)

        num_moves = list_num_moves[0]   #same for each trial

        turn_num = [i + 1 for i in range(len(num_moves))]

    temp = [
              [
                turn_num[i]
                ,num_moves[i]
                ,turn_time_data[0][i]    
                ,turn_time_data[1][i]    
              ]
                for i in range(len(num_moves))
            ]

    return temp


# Output Styles -----------------------------------------------------------

def print_results(results, **kwargs):
    ''' input: results (dict) b_interpret_Style (bool).
        output: This will first slice the results, generate calc'd fields
            based on an interpret_function. The print out based a dims_out
            list of formatting params.'''
    
    if kwargs.get('b_basic', False):
        
        data = interpret_basic_data(results)
        
        #('Col Heading', chars_in_col, chars_spacer_right, char_round)
        dims_out = [
            ('Test Name:', 15, 5, 15)
            ,('Avg Time:', 15, 5, 7)
            ,('Diff from baseline:', 20, 5, 4)
            ,('n:', 5, 5, 4)
            ,('Total Time:', 15, 5, 5)
            ]
        
        print_formatted_results(dims_out, data)

    if kwargs.get('b_basic_variation', False):
        
        data = interpret_variation_data(results)

        dims_out = [
            ('Test Name:', 15, 5, 15)
            ,('Avg Time:', 15, 5, 7)
            ,('Min Trial Time:', 15, 5, 7)
            ,('Max Trial Time:', 15, 5, 7)
            ]

        print_formatted_results(dims_out, data)

    if kwargs.get('b_turn_time', False):

        data = interpret_turn_time_data(results)

        dims_out = [
            ('Turn Num:', 10, 5, 10)
            ,('Num Moves:', 10, 5, 10)
            ,('Test A (ms):', 12, 5, 5)
            ,('Test B (ms):', 12, 5, 5)
            ]
        
        print_formatted_results(dims_out, data)



def perf_test(s_tests
                ,s_instructions
                ,n=10 
                ,b_trial_time=False
                ,b_num_available=False
                ,b_turn_time=False
                ,b_by_init_time=False
                ,b_time_init=False
                ,b_piece_init=False
                ,b_pgn_use=False
                ,b_pgn_convert=False
                ):

    '''main function to take a list of s_test, and log the time perf

        Output Terminology Heirarchy:
            result         - a set of tests, "diff algo styles"
                test         - a set of full games for one test
                    trial    - one full game
                        turn - one move in the game
        
        b_time_init - if true, time starting before Game() constructor call
                      if false, time after constructor, only counting play()
        b_piece_init - if true, call game.initialize() to set pieces
                        if false, initialize on play, first move. 

    '''

    result = {}

    for i_test, s_test in enumerate(s_tests):
        
        trial_time = []
        trial_turn_time = []
        trial_num_available = []

        t_trial_sum = float(0)
        t0 = time()
        
        for trial_i in range(n):
            
            t0_trial = time()
            
            _game = game_init(s_instructions
                              ,b_turn_time
                              ,b_piece_init
                              ,b_pgn_use
                              ,b_pgn_convert
                              )

            if not(b_time_init):
                t0_trial = time()

            game = select_function(s_test, _game, b_piece_init)  # MAIN FUNCTION
            
            t1_trial = time()
            t_trial_sum += (t1_trial - t0_trial)

            if b_turn_time:
              game_log = game.get_gamelog()


            if b_trial_time:    
                trial_time.append(t1_trial - t0_trial)        
            if b_turn_time:
                trial_turn_time.append( game_log.get_log_turn_time() )
            if b_num_available:
                trial_num_available.append( game_log.get_log_num_available() )
                    
        t1 = time() 
         
        test = {}

        if b_time_init:
            #including game_init in timing
            total_time = t1 - t0
        else:
            #removes timing on game_init
            total_time = t_trial_sum    

        if b_by_init_time:
            total_init_time = (t1 - t0) - t_trial_sum
        
        #by test
        test['test_name'] = s_test
        test['order'] = i_test      #to print out results in correct order
        test['n'] = n
        test['total_time'] = total_time
        
        #by trial
        if b_trial_time:
            test['trial_time'] = copy.copy(trial_time)
        
        #by turn
        if b_turn_time:
            test['turn_time'] = copy.copy(trial_turn_time)
        if b_num_available:
            test['num_available'] = copy.copy(trial_num_available)        

        #by init_time
        if b_by_init_time:
            test['init_time'] = total_init_time

        result[s_test] = test
    
    return result

# TestParameters ------------------------------------------------    

def data_all_algos():
    
    ''' These are all the algo styles available in play.
        'nk' is for check_for_check off; 'yk' means its on '''

    return [
            "opt_yk"
            ,"opt_nk"
            ,"baseline_nk"
            ,"baseline_yk"
            ,"naive_nk"
            ,"naive_yk"
            ,"var0"
            ,"var1"
            ,"var2"
            ,"var3"
            ,"var4"
            ]

def data_turntime_baseline_vs_naive():
    ''' examines turntimes for baseline vs naive '''
    return [
            "baseline_yk"
            ,"naive_yk"
            ]

def data_turntime_naive_vs_opt():
    return [
            "naive_yk"
            ,"opt_yk"
            ]
    

# Doc --------------------------------------------------------------

# Output Terminology Heirarchy:
#     result         - a set of tests
#         test         - a set of full games
#             trial    - one full game
#                 turn - one move in the game

# How a Main method works:
# First...
# perf_test() is called with s_test, a list of strings: 
#   which looks up in select_function and runs that implementation of Game(), play()
#   timing data for each full game is recorded here and written to test-dict
#   by calling with: b_trial_time, b_turn_time, b_num_available
#       you can add extra records to the test-dict data holder
#       for turntime styles, the indv turn timing data is observed in 
#       GameLog.add_turn_log() called from play().
#       This timing data is then copied from the log at the end of the play().
#   each s_test's, test-dict is record into results-dict, and returned.
# Second...
# print_results() are called with results-dict 
#   and a style operator:
#        b_basic, b_basic_variation, b_turn_time
#   depending on style operator, a different function is called:
#        interpret_basic_data, interpret_variation_data, interpret_turn_time_data
#       which slices the results-dict along different dimensions and returns
#       a tabular, list of list, called data
#   also depending on style operator, a dims_out list of tuple info on formatting:
#       ('Col Heading', chars_in_col, chars_spacer_right, char_round)
#   data and dims_out are fed into print_formatted_results() which prints aligned cols
# That's it.

# How arparse or callable function work

# Analysis Functions  ---------------------------------------------------

def analysis1(s_tests, s_instructions, b_return_results=False, **kwargs):
    ''' Type 1 - AlgoStlye by row, SummaryStats by col (Avg Min Max)'''
    
    results = perf_test(s_tests
                        ,s_instructions
                        ,n=kwargs.get('n', 10)
                        ,b_trial_time=True
                        ,b_time_init=kwargs.get('b_time_init', False)
                        ,b_piece_init=kwargs.get('b_piece_init', False)
                        ,b_pgn_use=kwargs.get('b_pgn_use', False)
                        ,b_pgn_convert=kwargs.get('b_pgn_convert', False)
                        )
    
    if b_return_results:
        return results
    
    print('')
    print_results(results, b_basic=True)
    
    if kwargs.get('b_just_basic', False):
        return None
    
    print('')
    print_results(results, b_basic_variation=True)
    print('')


def analysis2(s_tests, s_instructions, b_return_results=False, **kwargs):
    ''' Type 2 - TurnAttribute by row (NumAvailable Time), AlgoStyle by col '''
    
    results = perf_test(s_tests
                        ,s_instructions 
                        ,n=kwargs.get('n', 30)
                        ,b_turn_time=True
                        ,b_num_available=True
                        ,b_time_init=kwargs.get('b_time_init', False)
                        ,b_pgn_use=kwargs.get('b_pgn_use', False)
                        ,b_pgn_convert=kwargs.get('b_pgn_convert', False)
                        ,b_piece_init=kwargs.get('b_piece_init', False)
                        )
    
    if b_return_results:
        return results
    
    print_results(results, b_turn_time=True)

def analysis3(s_tests, s_instructions, **kwargs):
    ''' Type 3 - '''
    pass



# Batch Analysis -----------------------------------------------------


class BatchAnalysis:
    '''
    class to run stateful batch analysis on collection of games and 
    interface with db for input/output on these analysises.     
    '''
    
    def __init__(self
                    ,n=2
                    ,algo_style="opt_yk"
                    ,games_requested=range(1,6)
                    ,path_db=None
                    ):
        
        #Params
        self.n = n
        self.algo_style = algo_style
        self.gamesList = []
        self.analysis_tbl = "basic_tas"
        self.id_str = "GarryKasparovGames.txt-"

        #HoldingVars
        self.collected_batch = None
        self.results = {}
        self.instructions = None

        if path_db is None:
            self.db = TasPerfDB()
        else:
            self.db = TasPerfDB(data_dir = path_db)

    
    def setGames(self, games_requested):
        self.games_requested = games_requested
    
    def collect_batch(self):
        ''' 
        populate self.collected_batch:
                item: [0]: game_id (str), [1]: b_new (bool), [2]: tas [tas] optional
        '''
        self.gamesList = [self.id_str + str(i) for i in self.games_requested]

        temp_collected = []

        for _gameId in self.gamesList:
            
            _bExists = self.db.check_for_basic_record(_gameId)

            if _bExists:
                _item2 = self.db.get_tas_from_basic(_gameId)
            else:
                _item2 = self.db.get_instructions_from_games(_gameId)

            
            if _item2 is not None:

                _itemList = [ _gameId, not(_bExists), _item2 ]
                
                temp_collected.append( _itemList )
        
        self.collected_batch = temp_collected

    def setCollectedBatch(self, collected_batch):
        ''' so you can input instructions into the algo. E.g:
        [['dummy', True, "1. d4 e6 2. Nf3 Nf6"]]
         '''
        self.collected_batch = collected_batch
            

    def one_analysis(self, input_tas=None, instructions=None):
        ''' 
        returns: tas with a <trials> element  with an additional item
        input:   set either input_tas [tas]     - existing record, or,
                            instructions [str]  - new record
        This allows either a new TAS to be created, or an existing
        TAS-class to be appended onto <trials>
        '''
        
        if input_tas is None:

            tas = TimeAnalysisSchema()
            
            tas.set_meta_analysis(  
                                    algo_style = self.algo_style
                                    ,analysis_type = 'analysis2'
                                 )
            
            tas.set_log(
                          self.build_x(instructions)
                        )

        else:

            tas = input_tas
            
            instructions = tas.get_instructions()

        
        results = analysis2([self.algo_style]
                            ,instructions
                            ,n=self.n
                            ,b_return_results=True
                            ,b_pgn_convert=True
                            ,b_piece_init=True
                            )


        tas.set_trial_meta(N = self.n)
        tas.set_trial_data(results[self.algo_style])
        tas.add_trial()
        
        return tas


    @staticmethod
    def build_x(s_instructions):
        ''' Run a game and log attributes of the move/piece attributes at each turn'''
    
        turn_attributes = TurnAttributeSchema()
        turn_attributes.load_instructions(s_instructions, b_pgn=True)
        turn_attributes.create_data()
    
        return turn_attributes.get_data()
        

    def runBatch(self, b_write=False):
        ''' Run the items in collected_batch through one_analysis.'''

        for item in self.collected_batch:

            game_id = item[0]
            b_new = item[1]

            if b_new:
                s_instructions = str(item[2])
                tas_result = self.one_analysis(instructions=s_instructions)
            else:
                loaded_tas = item[2]
                tas_result = self.one_analysis(input_tas=loaded_tas)

            self.results[game_id] = tas_result
        
        if b_write:
            self.writeOut()

    
    def writeOut(self):
        
        d_collected = {}
        for triplet in self.collected_batch:
            d_collected[triplet[0]] = triplet[1]
        
        for _gameId in self.results:
            if d_collected[_gameId]:
                self.db.add_basic_record(_gameId
                                        ,self.results[_gameId].to_json(data_dir=None)
                                        )
            else:
                self.db.update_basic_record(_gameId
                                            ,self.results[_gameId].to_json(data_dir=None)
                                            )

    def getResults(self):
        return copy.deepcopy(self.results)

    def resetResults(self):
        self.results = {}

    def previewResults(self):
        #show games_requested
        #show batch_collect
        #show results preview
        #show historical summary
        #show historical records
        #show deviation from historical
        pass    
    
    def interactiveWrite(self):
        ''' wait until after runBatch and a print to verify writing '''
        input_return = input("'y' to save to db:" + str(self.db.conn) + ' >')
        if "y" in input_return:
            self.writeOut()
        #TODO - add an attribute-msg to the data record: e.g. "with netflix running"

    
    

# Cmds -------------------------------------------------------------

##### Show basic capabilities of this module
# > python perf_test.py --demo
# > python perf_test.py --singledemo
# > python perf_test.py --batchdemo

##### Show results around core concepts
# > python perf_test.py --multialgosummary
# > python perf_test.py --turntimenaivevsopt

##### Show contrived experiment printouts
# > python perf_test.py --gameinitdemo
# > python perf_test.py --pgndemo


##### DB loading cmd, copy data/GarryKasparovGames.txt -> data/perf/perf_db.db, "games" table
# > python perf_test.py --populategames

#### Run batch with options
# > python perf_test.py --batch --gamesrequested 2,3,4 --mockrun --verbose
# > python perf_test.py --batch --gamesrequested 2,3,4 --n 100


if __name__ == "__main__":
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--multialgosummary", action="store_true")
    ap.add_argument("--turntimenaivevsopt", action="store_true")
    ap.add_argument("--gameinitdemo", action="store_true")
    ap.add_argument("--pgndemo", action="store_true")
    
    ap.add_argument("--populategames", action="store_true")
    ap.add_argument("--singledemo", action="store_true")
    
    ap.add_argument("--batchdemo", action="store_true")
    ap.add_argument("--batch", action="store_true")
    
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--gamesrequested", type=str)
    ap.add_argument("--n", type=int)
    ap.add_argument("--mockrun", action="store_true")

    args = vars(ap.parse_args())


    if args["demo"]:
        
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"

        s_tests = data_all_algos()
        analysis1(s_tests, s_instructions, n=10)

        s_tests = data_turntime_baseline_vs_naive()
        analysis2(s_tests, s_instructions)


    if args["multialgosummary"]:
        
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"
        s_tests = data_all_algos()
        analysis1(s_tests, s_instructions)

    
    if args["turntimenaivevsopt"]:
        
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"
        s_tests = data_turntime_naive_vs_opt()
        analysis2(s_tests, s_instructions)

    if args["gameinitdemo"]:
        
        # s_instructions = "1. b1 c3"
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4"
        s_tests = ["baseline_nk", "opt_yk"]
        b_piece_init=True

        N = 250
        print '\n Just Play Timing \n'
        analysis1(s_tests, s_instructions, n=N, b_just_basic=True, b_piece_init=b_piece_init
                    ,b_time_init=False)
        print '\n With Consturctor Timing \n'
        analysis1(s_tests, s_instructions, n=N, b_just_basic=True, b_piece_init=b_piece_init
                    ,b_time_init=True)
        print '\n Just Play Timing (again) \n'
        analysis1(s_tests, s_instructions, n=N, b_just_basic=True, b_piece_init=b_piece_init
                    ,b_time_init=False)
        print '\n With Consturctor Timing (again) \n'
        analysis1(s_tests, s_instructions, n=N, b_just_basic=True, b_piece_init=b_piece_init
                    ,b_time_init=True)

        for N in (1, 250):
            
            s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"
            s_tests = ["baseline_nk", "opt_yk"]   #they dont call play(b_load)
            
            print '\n With Consturctor Timing \n'
            analysis2(s_tests, s_instructions, n=N, b_piece_init=False)
            
            print '\n Just Play Timing \n'
            analysis2(s_tests, s_instructions, n=N, b_piece_init=True)

    
    if args["pgndemo"]:
        
        s_tests = ["baseline_nk", "opt_yk"]
        s_instructions = "1. d4 e6 2. Nf3 Nf6 3. c4 Bb4+ 4. Nc3 b6 5. Qb3 Qe7 6. Bf4 d5 7. e3 Bb7 8. a3 Bxc3+ 9. Qxc3 O-O 10. Be2 dxc4 11. Qxc4 Rc8 12. O-O Ba6 13. Qc2 Bxe2 14. Qxe2 c5 15. Rac1 Nbd7 16. Qa6 h6 17. h3 Qe8 18. Bh2 cxd4 19. Nxd4 Nc5 20. Qe2 Qa4 21. Rc4 Qe8 22. Rfc1 a5 23. f3 a4 24. e4 Nfd7 25. Nb5 Qe7 26. Qe3 Qf6 27. e5 Qg6 28. Nd6 Rd8 29. Rg4 Qh7 30. Bf4 Kf8 31. Rd1 f5 32. exf6 Nxf6 33. Rh4 Nd5 34. Qe5 Nxf4 35. Rxf4+ Kg8 36. Rfd4 Rd7 37. Ne4 Rxd4 38. Rxd4 Qf5 39. Qxf5 exf5 40. Nxc5 bxc5 41. Rd5 Ra5 42. Rxf5 Rb5 43. Rf4 Rxb2 44. Rxa4 Ra2 45. h4 c4 46. Rxc4 Rxa3 47. Rc5 Ra4 48. h5 Ra2 49. Kh2 Rb2 50. Kh3 Rd2 51. g4 Rd1 52. Kg3 Rd4 53. Rc7 Ra4 54. Re7 Kf8 55. Re4 Ra5 56. Kf4 Kf7 57. Re5 Ra3 58. Ke4 Rb3 59. f4 Rb4+ 60. Kf5 Rb7 61. Rc5 Ra7 62. g5 hxg5 63. fxg5 g6+ 64. hxg6+ Kg7 65. Rc6 Ra5+ 66. Kg4 Ra1"
        N = 20
        B_PIECE_INIT = False

        sA = '\n Using PGN Instructions without conversion \n'
        sB = '\n Converting PGN before play \n'

        for i_trial in range(4):

            # Do two comparisons of testA vs testB to account for warm-up time.

            testType = "a" if i_trial % 2 == 0 else "b"

            if testType == "a":
                print sA
                testUsePgn, testConvertPgn = True, False
            elif testType == "b":
                print sB
                testUsePgn, testConvertPgn = False, True

            analysis1(s_tests
                        ,s_instructions
                        ,n=N
                        ,b_just_basic=True
                        ,b_piece_init=B_PIECE_INIT
                        ,b_time_init=False             # if this were true, no diff
                        ,b_pgn_use=testUsePgn          # changing var
                        ,b_pgn_convert=testConvertPgn  # changing var
                        )
    
        
    if args["populategames"]:
        db = TasPerfDB(data_dir = "../data/perf/perf_db.db", populate=True)
        db.closeConn()
        print 'done with populate'


    if args["singledemo"]:
        
        s_instructions = "1. d4 e6 2. Nf3 Nf6"
        collected_batch = [['dummy', True, s_instructions]]

        ba = BatchAnalysis(n=10)
        ba.setCollectedBatch(collected_batch)
        ba.runBatch(b_write=False)
        
        tas0 = ba.getResults()['dummy']
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(tas0.get_all())
        


    if args["batchdemo"]:
        
        ba = BatchAnalysis(path_db="../data/perf/perf_db.db")
        ba.setGames([1,12])
        ba.collect_batch()
        print 'Running analysis on games: '
        print "\n".join(map(lambda item: str(item[0]), copy.copy(ba.collected_batch)))

        print 'Running batch...'
        ba.runBatch(b_write=False)

        results = ba.getResults()
        gameIds = map(lambda item: str(item[0]), copy.copy(ba.collected_batch))
        tas0 = results[gameIds[0]]

        print 'Num Results: ', str(len(results.keys()))

        s_tas0 = str(tas0.get_all())
        print 'preview of TAS 0:'
        print s_tas0[:min(len(s_tas0), 1000)]

        print 'num_trials: ', str(len(tas0.get_all()['trials']))



    if args["batch"]:

        if args["gamesrequested"]:
            s_cmd = args["gamesrequested"]
            cmd_games_requested = map(int, s_cmd.split(","))
            #TODO - single game
            #TODO - range of games
        else:
            cmd_games_requested = range(1,11) #[1,2,3]

        if args["n"]:
            cmd_n = int(args["n"])
        else:
            cmd_n = 2

        if args["mockrun"]:
            cmd_pth_db = "../data/perf/staging_db.db"      #non-impact to production
            cmd_n = 2
        else:
            cmd_pth_db = "../data/perf/perf_db.db"         #Production
            cmd_n = cmd_n
        
        ba = BatchAnalysis(path_db=cmd_pth_db, n=cmd_n)
        ba.setGames(cmd_games_requested)
        ba.collect_batch()
        
        if args["verbose"]:
            print 'Running analysis on games: '
            print "\n".join(map(lambda item: str(item[0]), copy.copy(ba.collected_batch)))
            print 'Running batch...'
            t0 = time()
        
        ba.runBatch(b_write=True)

        results = ba.getResults()

        if args["verbose"]:
            print 'Total Time: ', str(time() - t0)
            print 'Num Results: ', str(len(results.keys()))
            for k in results.keys():
                print str(k), " trials: ", str(len(results[k].get_all()['trials']))

    print 'script done.'
        




# Scratchpad ---------------------------------------------------------

#5/29

# Using b_pgn_convert saves 10-20ms (= .04275 - .04055 to .29079 - 28030)
# for a ~130 ply game. So, 0.1 - 0.2 ms per turn to convert a pgn_move, 
# so roughly one 1/10 of one ply (~2ms) is rough total comp cost of conversion

# $ python perf_test.py --pgndemo

#  Using PGN Instructions without conversion


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#     baseline_nk             0.04275                      n/a        20               0.855
#          opt_yk             0.28005                     6.55        20               5.601
#  Converting PGN before play

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#     baseline_nk             0.04055                      n/a        20               0.811
#          opt_yk             0.28959                     7.14        20               5.791

#  Using PGN Instructions without conversion


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#     baseline_nk             0.04275                      n/a        20               0.855
#          opt_yk             0.29079                     6.80        20               5.815

#  Converting PGN before play


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#     baseline_nk             0.04090                      n/a        20               0.818
#          opt_yk             0.28030                     6.85        20               5.606



#5/28

# >python perf_test.py --gameinitdemo

# Game init is 0.30-0.45ms  = (.00225 - .00180) or (.00506 - .00474)

#  Just Play Timing


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#    base_nk_load             0.00188                      n/a       250               0.470
#     load_opt_yk             0.00474                     2.51       250               1.185

#  With Consturctor Timing


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#    base_nk_load             0.00225                      n/a       250               0.562
#     load_opt_yk             0.00506                     2.24       250               1.265

#  Just Play Timing (again)


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#    base_nk_load             0.00180                      n/a       250               0.452
#     load_opt_yk             0.00474                     2.62       250               1.187

#  With Consturctor Timing (again)


#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#    base_nk_load             0.00225                      n/a       250               0.562
#     load_opt_yk             0.00506                     2.24       250               1.265


# ###### You can see a slight increase in 1st move time with "just play" timing

#  With Consturctor Timing

# Test A:  baseline_nk
# Test B:  opt_yk
# N tests:  1

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20              0.0              0.0
#          2             20              0.0              0.0
#          3             22              0.0              0.0
#          4             21              0.0              0.0
#          5             28            15.99              0.0
#          6             22              0.0              0.0
#          7             25              0.0              0.0
#          8             21              0.0              0.0
#          9             35              0.0            17.00
#         10             22              0.0            3.999

#  Just Play Timing

# Test A:  base_nk_load
# Test B:  load_opt_yk
# N tests:  1

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20              0.0            3.999
#          2             20              0.0            3.999
#          3             22              0.0              0.0
#          4             21              0.0              0.0
#          5             28              0.0            3.999
#          6             22            4.000            3.999
#          7             25              0.0              0.0
#          8             21              0.0            4.000
#          9             35              0.0            3.999
#         10             22              0.0            7.999

#  With Consturctor Timing

# Test A:  baseline_nk
# Test B:  opt_yk
# N tests:  250

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20            0.548            1.640
#          2             20            0.460            1.459
#          3             22            0.324            1.427
#          4             21            0.527            1.264
#          5             28            0.335            1.751
#          6             22            0.463            1.315
#          7             25            0.428            2.223
#          8             21            0.347            1.383
#          9             35            0.600            3.039
#         10             22            0.251            3.112

#  Just Play Timing

# Test A:  base_nk_load
# Test B:  load_opt_yk
# N tests:  250

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20            0.412            1.536
#          2             20            0.567            1.791
#          3             22            0.239            1.675
#          4             21            0.351            0.360
#          5             28            0.684            2.244
#          6             22            0.156            1.820
#          7             25            0.496            1.199
#          8             21            0.395            1.735
#          9             35            0.364            3.280
#         10             22            0.427            2.828
# done.

# wsutt@DESKTOP-5VTC260 MINGW64 ~/Desktop/files/chess/basic_engine/tools (perf-test-1)

#5/27

# >python perf_test.py --demo

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#     baseline_nk             0.00469                      n/a        10               0.046
#     baseline_yk             0.00469                      1.0        10               0.046
#        naive_nk             0.30780                     65.4        10               3.078
#        naive_yk             0.29679                     63.1        10               2.967
#          opt_nk             0.02030                     4.31        10               0.203
#          opt_yk             0.02030                     4.31        10               0.203
#            var0             0.19839                     42.2        10               1.983
#            var1             0.20620                     43.8        10               2.062
#            var2             0.16559                     35.2        10               1.655
#            var3             0.00929                     1.97        10               0.092
#            var4             0.22030                     46.8        10               2.203

#      Test Name:           Avg Time:     Min Trial Time:     Max Trial Time:
#     baseline_nk             0.00469                 0.0             0.01600
#     baseline_yk             0.00469                 0.0             0.01600
#        naive_nk             0.30780             0.28200               0.375
#        naive_yk             0.29679             0.29600             0.29700
#          opt_nk             0.02030             0.01500             0.03199
#          opt_yk             0.02030             0.01500             0.03199
#            var0             0.19839             0.18700             0.20399
#            var1             0.20620             0.20299             0.21800
#            var2             0.16559             0.15599             0.17200
#            var3             0.00929                 0.0             0.01600
#            var4             0.22030             0.21799             0.23400

# Test B:  naive_long
# N tests:  30

# Test A:  baseline_long
#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20            2.066            22.86
#          2             20              0.0            23.96
#          3             22            2.100            26.00
#          4             21            1.533            24.53
#          5             28            2.066            33.30
#          6             22              0.0            26.09
#          7             25            4.199            30.70
#          8             21            1.533            23.86
#          9             35            1.566            41.23
#         10             22            4.166            26.99
# done.

# BASECAMP results on refactor

# $ python perf_test.py

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#   baseline_long             0.02230                      n/a        10               0.223
#      naive_long             0.32090                     14.3        10               3.209

#      Test Name:           Avg Time:     Min Trial Time:     Max Trial Time:
#   baseline_long             0.02230             0.01500             0.04099
#      naive_long             0.32090             0.31000             0.34599

# Test A:  optimal1_long
# Test B:  optimal2_long
# N tests:  30

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20            1.766            18.56
#          2             20            2.099            18.63
#          3             22            1.366            19.50
#          4             21            1.433            18.66
#          5             28            2.766            24.96
#          6             22            1.799            21.10
#          7             25            2.066            23.29
#          8             21            1.266            19.83
#          9             35            2.499            30.50
#         10             22            2.933            20.63



#2/9

# Note: there's a 3.5x penalty over baseline for a new optimaized method

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#        baseline             0.00479                      n/a        10               0.047
#     naive_check             0.26749                     55.7        10               2.674
#       test_copy             0.17340                     36.1        10               1.734
# test_copy_apply             0.17969                     37.4        10               1.796
#  test_c_apply_2             0.14619                     30.4        10               1.461
#  test_c_apply_3             0.00629                     1.31        10               0.062
#  test_c_apply_4             0.01740                     3.62        10               0.174
#   check_optimal             0.19670                     40.9        10               1.967

# Note Yuug! perf improvement 30x -> ~1.3x

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#        baseline             0.00470                      n/a        10               0.047
#     naive_check             0.28129                     59.8        10               2.812
#       test_copy             0.17569                     37.3        10               1.756
# test_copy_apply             0.18020                     38.3        10               1.802
#  test_c_apply_2             0.14609                     31.0        10               1.460
#  test_c_apply_3             0.00610                     1.29        10               0.061
#   check_optimal             0.19429                     41.3        10               1.942

# Note: test_c_apply uses Mutator to go from 25x to 20x slowdown

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#        baseline             0.00699                      n/a        10               0.069
#     naive_check             0.26970                     38.5        10               2.697
#       test_copy             0.17550                     25.0        10               1.755
# test_copy_apply             0.17949                     25.6        10               1.794
#  test_c_apply_2             0.14640                     20.9        10               1.464
#   check_optimal             0.19629                     28.0        10               1.962

# Note: Num Moves = 1, when king is in check

# Test A:  optimal1_long
# Test B:  optimal3_long
# N tests:  30

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20            17.33            16.66
#          2             20            17.23            16.69
#          3             20            16.83            16.53
#          4             21            17.63            17.73
#          5             23            19.46            19.06
#          6             20            16.26            16.30
#          7             21            17.20            16.93
#          8             21            18.03            17.26
#          9             31            24.39            25.09
#         10              1            20.16            19.80
#         11             39            31.43            31.79
#         12             26            21.76            21.89
#         13             35            28.19            27.33
#         14             25            20.26            20.70
#         15             39            31.09            31.03
#         16             28            22.93            23.10
#         17             38            29.89            29.96
#         18             29            24.13            24.26
#         19             44            35.23            35.63
#         20             29            23.10            23.59
#         21             48            37.43            37.06
#         22             30            24.99            25.73
#         23             56            41.63            43.13
#         24             33            27.73            27.33
#         25             49            36.16            37.20
#         26             30            25.33            25.56
#         27             47            34.83            35.30
#         28             28            24.06            24.66
#         29             43            32.06            32.46
#         30              2            29.13            30.13
#         31             40            29.79            30.83
#         32              2            27.50            28.30
#         33             26            19.73            20.13
#         34             37            27.46            26.93
#         35             30            22.43            22.43
#         36             35            24.96            25.86
#         37             34            23.73            23.49
#         38             34            23.66            23.76
#         39             34            24.60            24.56
#         40             37            26.33            25.86


# Note: Num Moves is incorrect below as its not doing check_filter in baseline

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#   baseline_long             0.01609                      n/a        10               0.160
#      naive_long             1.28770                     79.9        10               12.87

#      Test Name:           Avg Time:     Min Trial Time:     Max Trial Time:
#   baseline_long             0.01609             0.01499             0.02099
#      naive_long             1.28770             1.28099             1.29700

# Test B:  naive_long
# N tests:  30

# Test A:  baseline_long
#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20              0.0            22.90
#          2             20              0.0            19.33
#          3             20              0.0            22.36
#          4             21              0.0            23.46
#          5             23            4.166            24.46
#          6             20            2.600            22.16
#          7             21            2.099            19.30
#          8             21            1.566            25.59
#          9             31            3.633            31.19
#         10             24            0.499            19.79
#         11             39              0.0            41.63
#         12             27              0.0            28.16
#         13             35            0.533            36.46
#         14             26              0.0            26.56
#         15             39            0.533            40.10
#         16             29              0.0            31.19
#         17             38              0.0            37.06
#         18             30              0.0            31.19
#         19             44              0.0            43.26
#         20             30              0.0            30.20
#         21             48              0.0            46.89
#         22             33              0.0            33.80
#         23             56              0.0            56.83
#         24             36              0.0            33.33
#         25             49              0.0            46.86
#         26             33              0.0            31.20
#         27             47              0.0            46.93
#         28             31              0.0            30.20
#         29             43              0.0            40.63
#         30             38              0.0            29.26
#         31             40              0.0            38.99
#         32             36              0.0            28.09
#         33             27              0.0            21.90
#         34             37              0.0            38.06
#         35             31              0.0            27.09
#         36             35              0.0            33.79
#         37             34              0.0            29.66
#         38             34              0.0            30.23
#         39             35              0.0            30.79
#         40             37              0.0            33.26


# Test A:  baseline_tt
# Test B:  naive_check_tt
# N tests:  30

#  Turn Num:     Num Moves:     Test A (ms):     Test B (ms):
#          1             20            1.200            21.30
#          2             20            0.399            20.80
#          3             20            0.399            22.36
#          4             19            0.666            20.66
#          5             29            0.666            30.70
#          6             19            0.533            21.36
#          7             30            0.400            31.73
#          8             18            0.266            18.43
#          9             29            0.533            31.03
#         10             25            0.533            28.16


#      Test Name:           Avg Time:     Min Trial Time:     Max Trial Time:
#        baseline             0.00700             0.00399             0.01399
#     naive_check             0.25399                0.25             0.26600
#       test_copy             0.18280             0.15599             0.28100
# test_copy_apply             0.18129             0.17100             0.21799
#   check_optimal             0.19219             0.17199             0.21900
# check_optimal_2             0.19219             0.18699             0.21899
# check_optimal_3             0.19060             0.18700             0.21900


#2/8

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#        baseline             0.00469                      n/a        10               0.046
#     naive_check             0.25800                     54.8        10               2.580
#       test_copy             0.17039                     36.2        10               1.703
# test_copy_apply             0.17519                     37.2        10               1.751
#   check_optimal             0.19070                     40.5        10               1.907
# check_optimal_2             0.18949                     40.3        10               1.894
# check_optimal_3              0.1875                     39.8        10               1.875

#NOTE optimal_2, optimal_3 are little optimizations with little perf boost

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#        baseline             0.00469                      n/a        10               0.046
#     naive_check             0.25160                     53.5        10               2.516
#       test_copy             0.16719                     35.5        10               1.671
# test_copy_apply               0.175                     37.2        10                1.75
#   check_optimal             0.18910                     40.2        10               1.891

#NOTE: check_optimal is using a dummy version, but it looks helpful so far

#      Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#        baseline             0.00469                      n/a        10               0.046
#     naive_check             0.25490                     54.2        10               2.549
#       test_copy             0.16560                     35.2        10               1.656
# test_copy_apply             0.18129                     38.5        10               1.812

#NOTE: test_copy_apply also factors in apply_move(), thus the rest 54.2 - 38.5 is
#       time eaten up by get_possible_check() calls, which is where 
#       get_possible_check_optimal() can improve perf right now

#NOTE: "Avg Time:" is simply TotalTime/N and means avg time to run a full game, not do a move
#     test["turn_time"] and test["num_available"] are list of lists
#        outer index is trial_i
#        inner index is turn_j
#     Thus, we sum each j_th inner list element together, for all i in trials





#2/1

#  Test Name:           Avg Time:      Diff from baseline:        n:         Total Time:
#    baseline             0.00469                      n/a        10               0.046
# naive_check             0.24379                     51.8        10               2.437
#   test_copy             0.16719                     35.5        10               1.671



### 100x slower without filter king in check, 50x slower just with copying ###
### so half of the slowdown is copying, the other half is computation: ###
### if n ~ 20: O(20) * 20 = O(20^2) but this is 50x
### Adding apply_rule is .01 per round, but no_filter is only .005, 
### so it triples time there
# total time:  2.502
# per game:  0.25020
# total time:  0.046
# per game:  0.00469
# without apply_rule in test_copy
# total time:  1.657
# per game:  0.16570
# with apply_rule in test_copy
# total time:  1.734
# per game:  0.17340


# Unit Tests --------------------------------------------------------

import types
from db_module import DBDriver

def test_basic_perf_pattern():
    ''' Test invoking a Game and play '''

    SS_LONG = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"

    _game = game_init(s_instructions=SS_LONG)
    assert _game.__class__.__name__ == "Game"

    _game = select_function("baseline_nk",_game)
    assert _game.__class__.__name__ == "Game"

    _game = game_init(s_instructions=SS_LONG, b_turn_log=True)
    _game = select_function("opt_yk", _game)

    _gameLog = _game.get_gamelog()
    assert _gameLog.__class__.__name__ == "GameLog"

    _log_turn_time = _gameLog.get_log_turn_time()
    assert len(_log_turn_time) == 10                
    # WHY 10 and not 12? because this one is suppoed to fail on turn 11

def test_tas_aggregate_y():
    ''' testing TimeAnalysisSchema.aggregate_y which averages all turn times'''
    
    dummy_turn_times =  [
                             [ 0.1, 0.2, 0.1, 0.0]
                            ,[ 0.1, 0.2, 0.2, 0.2]
                        ]
    
    tas = TimeAnalysisSchema()
    
    aggregated_y = tas.aggregate_y(dummy_turn_times)
    rounded_aggregated_y = map(lambda x: round(x, 2), aggregated_y)
    #TODO - from numpy import double or import decimal *
    
    assert rounded_aggregated_y == [0.1, 0.2, 0.15, 0.1]

    dummy_turn_times =  [
                             [ 0.1, 0.2, 0.1, 0.0]
                            ,[ 0.1, 0.2, 0.1, 0.2, 0.2]      # wrong length
                        ]

    aggregated_y = tas.aggregate_y(dummy_turn_times)
    assert aggregated_y is None

def test_tas_load_1():
    ''' test loading the TAS from json'''
    import types

    tas = TimeAnalysisSchema()

    tas.from_json(path_fn="../data/perf/demo.tas")

    d_from_json = tas.get_all()

    assert type(d_from_json) == types.DictionaryType 
    
    assert d_from_json.get('trials', None) is not None
    assert d_from_json.get('meta_analysis', None) is not None    
    assert d_from_json.has_key('log')


def test_turn_attribute_1():
    ''' test using the class with example from main:test_log_schema_check_schedule_2()'''
    
    s_pgn = '1. Nf3 e6 2. c4 b6 3. g3 Bb7 4. Bg2 c5 5. O-O Nf6 6. Nc3 Be7 7. d4 cxd4 8. Qxd4 Nc6 9. Qf4 O-O 10. Rd1 Qb8 11. e4 d6 12. b3 a6 13. Bb2 Rd8 14. Qe3 Qa7 15. Ba3 Bf8 16. h3 b5 17. Qxa7 Nxa7 18. e5 dxe5 19. Bxf8 Kxf8 20. Nxe5 Bxg2 21. Kxg2 bxc4 22. bxc4 Ke8 23. Rab1 Rxd1 24. Nxd1 Ne4 25. Rb7 Nd6 26. Rc7 Nac8 27. c5 Ne4 28. Rxf7 Ra7 29. Rf4 Nf6 30. Ne3 Rc7 31. Rc4 Ne7 32. f4 Nc6 33. N3g4 Nd5 34. Nxc6 Rxc6 35. Kf3 Rc7 36. Ne5 Kd8 37. c6 Ke7 38. Ra4 Ra7 39. Kf2 Kd6 40. h4 a5 41. Kf3 Nc3 42. Rd4+ Nd5 43. Ke4 g6 44. g4 Kc7 45. Rd2 a4 46. f5 Nf6+ 47. Kf4 exf5 48. gxf5 Ra5 49. fxg6 hxg6 50. Rb2 Nd5+ 51. Ke4 Nb6 52. Rf2 a3 53. Rf7+ Kc8 54. Nxg6 Ra4+ 55. Ke5 Rb4 56. Ne7+ Kd8 57. c7+ Ke8 58. Rh7 Rc4 59. Nd5 Rc5 60. Rh8+ Kd7 61. Rd8+'

    tas = TurnAttributeSchema()
    tas.load_instructions(s_pgn)
    tas.create_data()
    d_data = tas.get_data()

    assert d_data['num_player_pieces'] == [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 14, 14, 13, 13, 12, 12, 11, 11, 10, 10, 10, 10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 8, 7, 7, 6, 7, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6, 4, 6]

def test_tas_weighted_avg_1():

    tas = TimeAnalysisSchema()

    list_n = [1,9]
    list_list_y = [
                     [0.1, 0.2, 0.4]
                    ,[0.2, 0.2, 0.1]
                ]

    weighted_y = tas.weighted_avg(list_n, list_list_y)

    rounded_weighted_y = map(lambda x: round(x, 3), weighted_y)

    assert rounded_weighted_y == [0.19, 0.2, 0.13]


def test_imported_dbdriver_errlog_1():
    ''' make sure the single instantiated DBErrLog at the module level
        doesnt bite us here with multiple instantiated DBDriver instances.
        Similiar to db_module:test_different_errlogs_respectively_1() '''

    from db_module import DBDriver
    
    db = DBDriver(data_dir="../data/perf/mock_db.db")
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    assert len(db.getErrLog()) == 2

    db2 = DBDriver(data_dir="../data/perf/mock_db.db")
    db2.execStr("select * from BAD_TABLE", b_fetch=True)
    
    assert len(db2.getErrLog()) == 1

    db = DBDriver(data_dir="../data/perf/mock_db.db")
    assert len(db.getErrLog()) == 0
    

def test_order_of_functions_1():
    ''' Testing Design Pattern: function can be called from above within class '''

    class MyClass:
        def __init__(self):
            self.data = 0
        def funcA(self):
            self.funcB()
        def funcB(self):
            self.data = 1
    mc = MyClass()
    mc.funcA()
    assert mc.data == 1


def test_batch_class_collect_batch_1():
    ''' Test BatchAnalysis loading a new TAS from games table '''
    
    #Make sure the these three records in basic_tas table in mock_db are blank
    db = DBDriver(data_dir = "../data/perf/mock_db.db")
    db.execStr("delete from basic_tas where id = ?",  ("GarryKasparovGames.txt-102",))
    db.execStr("delete from basic_tas where id = ?",  ("GarryKasparovGames.txt-103",))
    db.execStr("delete from basic_tas where id = ?",  ("GarryKasparovGames.txt-104",))
    print db.getErrLog()    # if test fails, dump errlog
    
    #Request games of the ones which are blank
    ba = BatchAnalysis(path_db="../data/perf/perf_db.db")
    ba.setGames(range(102,105))
    assert ba.games_requested[2] == 104
    
    #Analyze the triplet data structure of collected_batch list
    ba.collect_batch()
    _collected_batch = ba.collected_batch
    assert _collected_batch[0]== [ 
                                    "GarryKasparovGames.txt-102" 
                                    ,True
                                    ,"1. d4 Nf6 2. c4 e6 3. g3 d5 4. Bg2 dxc4 5. Nf3 c5 6. O-O Nc6 7. Ne5 Bd7 8. Na3 cxd4 9. Naxc4 Rc8 10. Qb3 Nxe5 11. Nxe5 Bc6 12. Nxc6 bxc6 13. Rd1 c5 14. e3 Bd6 15. exd4 c4 16. Qb5+ Qd7 17. a4 O-O 18. Be3 Rc7 19. d5 e5 20. Rdc1 Rfc8 21. Bf1 g6 22. Bxc4 Qxb5 23. Bxb5 Nxd5 24. Ba6 Rxc1+ 25. Rxc1 Rxc1+ 26. Bxc1 Bc5 27. Bc4 Nb6 28. Bb3 Kf8 29. a5 Nd7 30. Ba4 Nf6 31. Bd2 Nd5 32. Bb3 Nb4 33. Bc4 Ke7 34. Kg2 h5 35. f3 Nc6 36. Bd5 Nb4 \n"
                                     ]
    

def test_batch_class_collect_batch_2():
    ''' Test BatchAnalysis loading existing TAS from basic_tas '''

    #Make sure these three records are in basic_tas table
    # >python perf_test.py --batchdemodb --usemockdb

    #Request games which are in basic_tas
    ba = BatchAnalysis(path_db="../data/perf/mock_db.db")
    ba.setGames(range(1,4))
    ba.collect_batch()
    _collected_batch = ba.collected_batch

    #Assert 2nd item in triplet is False, indicating existing TAS
    assert _collected_batch[0][:2] == [ 
                                    "GarryKasparovGames.txt-1" 
                                    ,False
                                     ]
    
    #Make sure you loaded an existing TAS
    _tas = _collected_batch[0][2].get_all()
    assert type(_tas) == types.DictionaryType
    assert _tas['log']['s_instructions'] == '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7 \n'
    assert _tas['log']['num_available'] == [20, 20, 22, 22, 26, 23, 26, 24, 31, 28, 31, 36, 40, 35, 46, 35, 44, 35, 40, 36, 40, 35, 47, 35, 45, 37, 44, 35, 42, 35, 42, 38, 43, 33, 47, 32, 32, 32, 31, 32, 30]
    assert type(_tas['trials']) == types.ListType


def test_batch_analysis_run_1():
    ''' testing runBatch() without writing to db:  '''

    gameId = "GarryKasparovGames.txt-1"
    
    #establish num of trials in TAS in basic_tas
    db = TasPerfDB(data_dir = "../data/perf/mock_db.db")
    tas0 = TimeAnalysisSchema()
    db.c.execute("select * from basic_tas where id = ?",(gameId,))
    
    s_tas0 = db.c.fetchall()[0][1]
    # print db.getErrLog()
    # [0][1]
    print s_tas0
    db.closeConn()
    tas0.from_json(s_json=s_tas0,path_fn=None)
    tas0_num_trials = len(tas0.get_all()['trials'])
    assert tas0_num_trials > 0

    #Run batch analysis
    ba = BatchAnalysis()
    ba = BatchAnalysis(path_db="../data/perf/mock_db.db")
    ba.setGames([1])
    ba.collect_batch()
    ba.runBatch(b_write=False)
    results = ba.getResults()
    tas1 = results[gameId].get_all()
    tas1_num_trials = len(tas1['trials'])

    #there should be one more trial added to tas
    assert tas1_num_trials == tas0_num_trials + 1


def test_batch_analysis_run_write_1():
    ''' testing runBatch() by writing to db:  '''
    
    gameId = "GarryKasparovGames.txt-1"
    
    #establish num of trials in TAS in basic_tas
    db = TasPerfDB(data_dir = "../data/perf/mock_db.db")
    tas0 = TimeAnalysisSchema()
    db.c.execute("select * from basic_tas where id = ?",(gameId,))
    s_tas0 = db.c.fetchall()[0][1]
    db.closeConn()
    tas0.from_json(s_json=s_tas0,path_fn=None)
    tas0_num_trials = len(tas0.get_all()['trials'])
    assert tas0_num_trials > 0

    #Run batch analysis and write to db
    ba = BatchAnalysis(path_db="../data/perf/mock_db.db")
    ba.setGames([1])
    ba.collect_batch()
    ba.runBatch(b_write=True)
    
    #there should be one more trial added to tas
    db = TasPerfDB(data_dir = "../data/perf/mock_db.db")
    tas1 = TimeAnalysisSchema()
    db.c.execute("select * from basic_tas where id = ?",(gameId,))
    s_tas1 = db.c.fetchall()[0][1]
    db.closeConn()
    tas1.from_json(s_json=s_tas1, path_fn=None)
    tas1_num_trials = len(tas1.get_all()['trials'])
    assert tas1_num_trials == tas0_num_trials + 1

def test_batch_analysis_run_parameters_1():
    ''' testing parameters passed thru and changed from default  '''
    pass
