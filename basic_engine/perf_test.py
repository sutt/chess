from time import time
from main import Game
import copy


#TODO's here:
#add in sqlite3 for logging
#add in git hashes, etc
#add in a plot to compare N to King_in_Check(N)

ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5"

# mm_long = [((6, 0), (4, 0)), ((1, 0), (3, 0)), ((6, 1), (4, 1)), ((1, 2), (3, 2)), ((4, 1), (3, 2)), ((1, 5), (3, 5)), ((6, 4), (4, 4)), ((0, 1), (2, 2)), ((7, 3), (3, 7)), ((1, 6), (2, 6)), ((7, 5), (2, 0)), ((0, 0), (2, 0)), ((7, 0), (5, 0)), ((0, 5), (2, 7)), ((7, 6), (5, 5)), ((1, 1), (3, 1)), ((7, 2), (6, 1)), ((0, 4), (0, 5)), ((4, 0), (3, 1)), ((2, 7), (3, 6)), ((3, 7), (2, 6)), ((3, 6), (4, 5)), ((7, 4), (7, 6)), ((1, 7), (2, 7)), ((6, 2), (4, 2)), ((4, 5), (1, 2)), ((6, 6), (4, 6)), ((2, 2), (4, 3)), ((2, 6), (1, 6)), ((0, 5), (0, 4)), ((1, 6), (2, 6)), ((2, 0), (2, 6)), ((3, 1), (2, 1)), ((1, 3), (3, 3)), ((5, 5), (4, 3)), ((3, 5), (4, 4)), ((7, 1), (5, 2)), ((2, 7), (3, 7)), ((5, 0), (3, 0)), ((2, 6), (2, 3))]
ss_long = '1. g1 e1 2. b1 d1 3. g2 e2 4. b3 d3 5. e2 d3 6. b6 d6 7. g5 e5 8. a2 c3 9. h4 d8 10. b7 c7 11. h6 c1 12. a1 c1 13. h1 f1 14. a6 c8 15. h7 f6 16. b2 d2 17. h3 g2 18. a5 a6 19. e1 d2 20. c8 d7 21. d8 c7 22. d7 e6 23. h5 h7 24. b8 c8 25. g3 e3 26. e6 b3 27. g7 e7 28. c3 e4 29. c7 b7 30. a6 a5 31. b7 c7 32. c1 c7 33. d2 c2 34. b4 d4 35. f6 e4 36. d6 e5 37. h2 f3 38. c8 d8 39. f1 d1 40. c7 c4 '

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

    if s_function == "test_c_apply_2":
            
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_test_copy_apply_2=True)

    if s_function == "test_c_apply_3":
            
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_test_copy_apply_3=True)
    
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

    if s_function == "baseline_long":
            
        game = Game(s_instructions = ss_long
                    ,b_log_turn_time = True
                    ,b_log_num_available = True 
                    )  
        game.play(king_in_check_on=False)    
        return game.get_gamelog()
    
    if s_function == "naive_long":

        game = Game(s_instructions = ss_long
            ,b_log_turn_time = True
            ,b_log_num_available = True 
            )  
        game.play(king_in_check_on=True)    
        return game.get_gamelog()

    if s_function == "optimal1_long":
            
        game = Game(s_instructions = ss_long
                    ,b_log_turn_time = True
                    ,b_log_num_available = True 
                    )  
        game.play(king_in_check_on=False, king_in_check_optimal = True)    
        return game.get_gamelog()
    
    if s_function == "optimal3_long":

        game = Game(s_instructions = ss_long
            ,b_log_turn_time = True
            ,b_log_num_available = True 
            )  
        game.play(king_in_check_on=False, king_in_check_optimal_3 = True)    
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
    ,"test_c_apply_2"
    ,"test_c_apply_3"
    ,"check_optimal"
    ,"check_optimal_2"
    ,"check_optimal_3"
    ]

# s_tests = [
#     "baseline_long"
#     ,"naive_long"
#     ]

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

s_tests = [
    "baseline_long"
    ,"naive_long"
    ]

s_tests = [
    "optimal1_long"
    ,"optimal3_long"
    ]

# results = perf_test(s_tests, n=30, b_turn_time=True, b_num_available=True)
# print_results(results, b_turn_time=True)


#2/9

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
