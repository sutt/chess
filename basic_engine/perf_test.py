from time import time
from main import Game
import copy


#TODO's here:
#add in sqlite3 for logging
#add in git hashes, etc
#add in a plot to compare N to King_in_Check(N)

ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5"

def select_function(s_function):
    ''' input: s_function (string)
        output: [optional] usually a GameLog but really completely dynamic
        This string choses a way to:
             init Game(), param's for play(), possible return value.'''
    
    if s_function == "baseline":
        
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False)    
        
    if s_function == "naive_check":

        game = Game(s_instructions = ss)
        game.play()

    if s_function == "test_copy":
        
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_test_copy=True)

    if s_function == "test_copy_apply":
        
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_test_copy_apply=True)
    
    if s_function == "baseline_tt":
        
        game = Game(s_instructions = ss
                    ,b_log_turn_time = True
                    ,b_log_num_available = True 
                    )  
        game.play(king_in_check_on=False)    
        return game.get_gamelog()
    
    if s_function == "naive_check_tt":

        game = Game(s_instructions = ss
            ,b_log_turn_time = True
            ,b_log_num_available = True 
            )  
        game.play(king_in_check_on=True)    
        return game.get_gamelog()

    if s_function == "check_optimal":
            
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_optimal=True)

    if s_function == "check_optimal_2":
            
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_optimal_2=True)

    if s_function == "check_optimal_3":
            
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_optimal_3=True)

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
                ,n=10 
                ,b_trial_time=False
                ,b_num_available=False
                ,b_turn_time=False
                ):

    '''main function to take a list of s_test, and log the time perf

        Output Terminology Heirarchy:
            result         - a set of tests
                test         - a set of full games
                    trial    - one full game
                        turn - one move in the game
    '''

    result = {}
    xx = 0

    for i_test, s_test in enumerate(s_tests):
        xx += 1
        trial_time = []
        trial_turn_time = []
        trial_num_available = []

        t0 = time()
        
        for trial_i in range(n):
            
            t0_trial = time()
            opt_game_log = select_function(s_test)  # Main
            t1_trial = time()

            if b_trial_time:    
                trial_time.append(t1_trial - t0_trial)        
            if b_turn_time:
                trial_turn_time.append( opt_game_log.get_log_turn_time() )
            if b_num_available:
                trial_num_available.append( opt_game_log.get_log_num_available() )
                    
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
    

s_tests = [
    "baseline"
    ,"naive_check"
    ,"test_copy"
    ,"test_copy_apply"
    ,"check_optimal"
    ,"check_optimal_2"
    ,"check_optimal_3"
    ]

results = perf_test(s_tests, n=10, b_trial_time=True)

print('')
print_results(results, b_basic=True)
print('')
print_results(results, b_basic_variation=True)
print('')

s_tests = [
    "baseline_tt"
    ,"naive_check_tt"
    ]
results = perf_test(s_tests, n=30, b_turn_time=True, b_num_available=True)

print_results(results, b_turn_time=True)


#2/9

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