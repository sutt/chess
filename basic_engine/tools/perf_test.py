import sys
from time import time
import copy
sys.path.append('../')

from src.main import Game
from utils import convert_pgn_to_a1

from schema_module import TimeAnalysisSchema
from schema_module import TurnAttributeSchema

from db_module import DBDriver



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

import json
import pprint


def one_analysis(   s_instructions
                    ,b_pgn=True
                    ,algo_style="opt_yk"
                    ,n=2
                    ,b_noisy=False
                    ,b_return_tas=False
                    ,b_write_out=False
                    ,b_build_x=True
                    ):
    
    ''' run analysis2 to create Y-data, run create_data() to create X-data()'''

    analysis_schema = TimeAnalysisSchema()

    #Set Y-meta_analysis
    analysis_schema.set_meta_analysis(   algo_style = algo_style
                                        ,analysis_type = 'analysis2'
                                        )
    
    
    if b_build_x:
        
        #Build X
        turn_attributes = TurnAttributeSchema()
        turn_attributes.load_instructions(s_instructions, b_pgn=b_pgn)
        turn_attributes.create_data()

        #Set X
        analysis_schema.set_log(turn_attributes.get_data())

    #Set Y-(trial)-meta
    analysis_schema.set_trial_meta(N = n)

    #Build Y-data
    results = analysis2([algo_style]
                        ,s_instructions
                        ,n=n
                        ,b_return_results=True
                        ,b_pgn_convert=True
                        ,b_piece_init=True
                        )
    
    #Set Y-data
    analysis_schema.set_trial_data(results[algo_style])

    #Append trial to trials
    analysis_schema.add_trial()
    
    #FileSystem Save / Return data-structure
    if b_write_out:
        analysis_schema.to_json(data_dir='../data/perf/')

    #Output to console
    if b_noisy:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(analysis_schema.get_all())

    if b_return_tas:
        return analysis_schema


def batch_analyze(   input_fn="GarryKasparovGames.txt"
                    ,output_fn="demo_batch.tas"
                    ,max_lines=None
                    ,n=2
                    ,algo_style="opt_yk"
                    ,b_noisy=False
                    ,b_write_out=False
                    ):
    
    ''' analyze mulitple games and log them '''

    
    #PARAMS
    b_input_filesystem = True
    b_output_filesystem = False
    b_input_db = False
    b_output_db = True

    INPUT_DATA_DIR = "../data/"
    OUTPUT_DATA_DIR = "../data/perf/"
    
    db = None
    if (output_fn is None) or (input_fn is None):
        db = DBDriver()

    b_insert = True if input_fn is not None else False  #insert or update

    if input_fn is not None:
        input_data = INPUT_DATA_DIR + input_fn
    if output_fn is not None:
        output_data = OUTPUT_DATA_DIR + output_fn
    
    #Read in Data
    with open(input_data, "r") as f:
        lines = f.readlines()
    num_lines = len(lines) if max_lines is None else min(len(lines), max_lines)
    games = lines[:num_lines]

    #Hold the data
    results = {}
    
    #Loop
    for i, s_instruct in enumerate(games):
        
        ret = one_analysis(  s_instructions = s_instruct
                            ,b_pgn=True
                            ,algo_style=algo_style
                            ,n=n
                            ,b_noisy=False
                            ,b_return_tas=True
                            ,b_write_out=False
                            ,b_build_x=b_insert
                            )

        key_name = input_fn + "-" + str(i+1)
        
        if output_fn is not None:
            results[key_name] = ret.get_all()
        else:
            results[key_name] = ret.to_json()

        if b_noisy:
            print '\n'+ key_name + '\n'
    
    if b_noisy:
        print results
        print 'done with batch_analyze'

    if b_write_out:
        
        if output_fn is not None:
            with open(output_data, "w") as f:
                json.dump(results, f)

        if output_fn is None:
            for _k in results.keys():
                db.add_basic_record(s_tas = results[_k] ,tas_id = _k)

            
    if db is not None:
        db.closeConn()
            


        
    
    
    

# Cmds -------------------------------------------------------------

# > python perf_test.py --demo
# > python perf_test.py --multialgosummary
# > python perf_test.py --turntimenaivevsopt
# > python perf_test.py --gameinitdemo
# > python perf_test.py --batchdemo
# > python perf_test.py --batchdemosave
# > python perf_test.py --batchdemodb
# > python perf_test.py --singledemo

if __name__ == "__main__":
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--verboseparams", action="store_true")
    ap.add_argument("--longgame", action="store_true")
    ap.add_argument("--shortgame", action="store_true")
    ap.add_argument("--multialgosummary", action="store_true")
    ap.add_argument("--turntimenaivevsopt", action="store_true")
    ap.add_argument("--gameinitdemo", action="store_true")
    ap.add_argument("--pgndemo", action="store_true")
    ap.add_argument("--batchdemo", action="store_true")
    ap.add_argument("--batchdemosave", action="store_true")
    ap.add_argument("--batchdemodb", action="store_true")
    ap.add_argument("--demodb", action="store_true")
    ap.add_argument("--singledemo", action="store_true")

    args = vars(ap.parse_args())

    
    if args["verboseparams"] or args["demo"]:
        pass
            
    if args["longgame"]:
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"

    if args["shortgame"]:
        s_instructions = "1. b1 c3"

    
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

    if args["batchdemo"]:
        batch_analyze(max_lines=5, n=5, b_noisy=True, b_write_out=False)

    if args["batchdemosave"]:
        batch_analyze(max_lines=2, n=2, b_noisy=False, b_write_out=True)

    if args["demodb"]:
        
        db = DBDriver()

    
    if args["batchdemodb"]:
        
        #setup db stage
        db = DBDriver()
        db.drop_table_basic_tas()
        db.closeConn()

        #run batch with output to db
        batch_analyze(max_lines=2, n=2, b_noisy=False, b_write_out=True
                        ,output_fn=None)
        
        #verify db results
        db = DBDriver()
        ret = db.select_all_basic()
        print ret

    if args["singledemo"]:
        s_instructions = "1. d4 e6 2. Nf3 Nf6"
        # s_instructions = "1. d4 e6 2. Nf3 Nf6 3. c4 Bb4+ 4. Nc3 b6 5. Qb3 Qe7 6. Bf4 d5 7. e3 Bb7 8. a3 Bxc3+ 9. Qxc3 O-O 10. Be2 dxc4 11. Qxc4 Rc8 12. O-O Ba6 13. Qc2 Bxe2 14. Qxe2 c5 15. Rac1 Nbd7 16. Qa6 h6 17. h3 Qe8 18. Bh2 cxd4 19. Nxd4 Nc5 20. Qe2 Qa4 21. Rc4 Qe8 22. Rfc1 a5 23. f3 a4 24. e4 Nfd7 25. Nb5 Qe7 26. Qe3 Qf6 27. e5 Qg6 28. Nd6 Rd8 29. Rg4 Qh7 30. Bf4 Kf8 31. Rd1 f5 32. exf6 Nxf6 33. Rh4 Nd5 34. Qe5 Nxf4 35. Rxf4+ Kg8 36. Rfd4 Rd7 37. Ne4 Rxd4 38. Rxd4 Qf5 39. Qxf5 exf5 40. Nxc5 bxc5 41. Rd5 Ra5 42. Rxf5 Rb5 43. Rf4 Rxb2 44. Rxa4 Ra2 45. h4 c4 46. Rxc4 Rxa3 47. Rc5 Ra4 48. h5 Ra2 49. Kh2 Rb2 50. Kh3 Rd2 51. g4 Rd1 52. Kg3 Rd4 53. Rc7 Ra4 54. Re7 Kf8 55. Re4 Ra5 56. Kf4 Kf7 57. Re5 Ra3 58. Ke4 Rb3 59. f4 Rb4+ 60. Kf5 Rb7 61. Rc5 Ra7 62. g5 hxg5 63. fxg5 g6+ 64. hxg6+ Kg7 65. Rc6 Ra5+ 66. Kg4 Ra1"
        one_analysis(s_instructions, b_noisy=True)
        


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
    
