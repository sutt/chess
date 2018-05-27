import sys
from time import time
import copy
sys.path.append('../')

from src.main import Game




# s_insturction params -----------------------------------------------

SS = "1. b1 c3"
SS_LONG = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"


# Different Experiments --------------------------------------------------
#  an s_test string causes a different style of Game and play to happen

def select_function(s_function, s_instructions=SS_LONG):
    ''' input: s_function (string)
        output: [optional] usually a GameLog but really completely dynamic
        This string choses a way to:
             init Game(), param's for play(), pos_instructionsible return value.'''
    
    if s_function == "baseline_nk":
        
        # no check_for_check, no filter_check at all
        game = Game(s_instructions = s_instructions)
        game.play(check_for_check=False, filter_check_opt=False)    

    if s_function == "baseline_yk":
        
        # yes check_for_check, no filter_check at all
        game = Game(s_instructions = s_instructions)
        game.play(check_for_check=True, filter_check_opt=False)    
        
    if s_function == "naive_nk":

        #no check_for_check, filter_check
        game = Game(s_instructions = s_instructions)
        game.play(check_for_check=False, filter_check_opt=False, filter_check_naive=True)

    if s_function == "naive_yk":
    
        game = Game(s_instructions = s_instructions)
        game.play(check_for_check=True, filter_check_opt=False, filter_check_naive=True)

    if s_function == "opt_nk":
    
        game = Game(s_instructions = s_instructions)
        game.play(check_for_check=False, filter_check_opt=True)

    if s_function == "opt_yk":
        
        game = Game(s_instructions = s_instructions)
        game.play(check_for_check=True, filter_check_opt=True)

    
    #all vars below are yk - they do check_for_check

    if s_function == "var0":
        
        game = Game(s_instructions = s_instructions)
        game.play(filter_check_opt=False, filter_check_test_copy=True)

    if s_function == "var1":
        
        game = Game(s_instructions = s_instructions)
        game.play(filter_check_opt=False, filter_check_test_copy_apply=True)

    if s_function == "var2":
            
        game = Game(s_instructions = s_instructions)
        game.play(filter_check_opt=False, filter_check_test_copy_apply_2=True)

    if s_function == "var3":
            
        game = Game(s_instructions = s_instructions)
        game.play(filter_check_opt=False, filter_check_test_copy_apply_3=True)

    if s_function == "var4":
            
        game = Game(s_instructions = s_instructions)
        game.play(filter_check_opt=False, filter_check_test_copy_opt=True)


    if s_function == "tt_baseline":
            
        game = Game(s_instructions = s_instructions
                    ,b_log_turn_time = True
                    ,b_log_num_available = True 
                    )  
        game.play(filter_check_opt=False)    
        return game.get_gamelog()
    
    if s_function == "tt_naive":

        game = Game(s_instructions = s_instructions
            ,b_log_turn_time = True
            ,b_log_num_available = True 
            )  
        game.play(filter_check_naive=True, filter_check_opt=False)    
        return game.get_gamelog()

    if s_function == "tt_opt":
            
        game = Game(s_instructions = s_instructions
                    ,b_log_turn_time = True
                    ,b_log_num_available = True 
                    )  
        game.play()    
        return game.get_gamelog()
    
    return None     #to show that the function is no returning a test exit data


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
                ,s_instructions=SS_LONG
                ,n=10 
                ,b_trial_time=False
                ,b_num_available=False
                ,b_turn_time=False
                ):

    '''main function to take a list of s_test, and log the time perf

        Output Terminology Heirarchy:
            result         - a set of tests, "diff algo styles"
                test         - a set of full games for one test
                    trial    - one full game
                        turn - one move in the game
    '''

    result = {}

    for i_test, s_test in enumerate(s_tests):
        
        trial_time = []
        trial_turn_time = []
        trial_num_available = []

        t0 = time()
        
        for trial_i in range(n):
            
            t0_trial = time()
            game_log = select_function(s_test, s_instructions)  # MAIN FUNCTION
            t1_trial = time()

            if b_trial_time:    
                trial_time.append(t1_trial - t0_trial)        
            if b_turn_time:
                trial_turn_time.append( game_log.get_log_turn_time() )
            if b_num_available:
                trial_num_available.append( game_log.get_log_num_available() )
                    
        t1 = time() 
         
        test = {}

        #by test
        test['test_name'] = s_test
        test['order'] = i_test      #to print out results in correct order
        test['n'] = n
        test['total_time'] = t1 - t0
        
        #by trial
        if b_trial_time:
            test['trial_time'] = copy.copy(trial_time)
        
        #by turn
        if b_turn_time:
            test['turn_time'] = copy.copy(trial_turn_time)
        if b_num_available:
            test['num_available'] = copy.copy(trial_num_available)        

        result[s_test] = test
    
    return result

# TestParameters ------------------------------------------------    

def data_all_algos():
    
    ''' These are all the algo styles available in play.
        'nk' is for check_for_check off; 'yk' means its on '''

    return [
            "baseline_nk"
            ,"baseline_yk"
            ,"naive_nk"
            ,"naive_yk"
            ,"opt_nk"
            ,"opt_yk"
            ,"var0"
            ,"var1"
            ,"var2"
            ,"var3"
            ,"var4"
            ]

def data_turntime_baseline_vs_naive():
    ''' examines turntimes for baseline vs naive '''
    return [
            "tt_baseline"
            ,"tt_naive"
            ]

def data_turntime_naive_vs_opt():
    return [
            "tt_naive"
            ,"tt_opt"
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

# Main Functions  ---------------------------------------------------

def main1(s_tests, s_instructions):
    ''' Type 1 - AlgoStlye by row, SummaryStats by col (Avg Min Max)'''
    
    results = perf_test(s_tests
                        ,s_instructions
                        ,n=10
                        ,b_trial_time=True
                        )
    print('')
    print_results(results, b_basic=True)
    print('')
    print_results(results, b_basic_variation=True)
    print('')

def main2(s_tests, s_instructions):
    ''' Type 2 - TurnAttribute by row (NumAvailable Time), AlgoStyle by col '''
    
    results = perf_test(s_tests
                        ,s_instructions 
                        ,n=30 
                        ,b_turn_time=True
                        ,b_num_available=True
                        )
    
    print_results(results, b_turn_time=True)

# Cmds -------------------------------------------------------------

# > python perf_test.py --demo

# > python perf_test.py --multialgosummary
# > python perf_test.py --turntimenaivevsopt

if __name__ == "__main__":
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--verboseparams", action="store_true")
    ap.add_argument("--longgame", action="store_true")
    ap.add_argument("--shortgame", action="store_true")
    ap.add_argument("--multialgosummary", action="store_true")
    ap.add_argument("--turntimenaivevsopt", action="store_true")

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
        main1(s_tests, s_instructions)

        s_tests = data_turntime_baseline_vs_naive()
        main2(s_tests, s_instructions)


    if args["multialgosummary"]:
        
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"
        s_tests = data_all_algos()
        main1(s_tests, s_instructions)

    
    if args["turntimenaivevsopt"]:
        
        s_instructions = "1. b1 c3 2. b7 b5 3. d2 d4 4. b5 b4 5. c1 e3 6. b4 c3 7. d1 d3 8. c3 b2 9. h2 h4 10. b2 a1 11. e1 c1 12. h7 h5"

        s_tests = data_turntime_naive_vs_opt()
        main2(s_tests, s_instructions)

    
    print 'done.'
        




# Scratchpad ---------------------------------------------------------

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

