import time
from main import Game


#TODO's here:
#add in sqlite3 for logging
#add in git hashes, etc
#add in a plot to compare N to King_in_Check(N)

ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5"

def select_function(s_function):
    
    if s_function == "baseline":
        
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False)    
        
    if s_function == "naive_check":

        game = Game(s_instructions = ss)
        # game.play(king_in_check_on=False)    
        game.play()

    if s_function == "test_copy":
        
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_test_copy=True)

    if s_function == "test_copy_apply":
        
        game = Game(s_instructions = ss)
        game.play(king_in_check_on=False, king_in_check_test_copy_apply=True)

    if s_function == "example_return":
        
        game = Game(s_instructions = ss, b_log_turn_time = True )  
        game.play()

        return game.get_gamelog()

    if s_function == "example_return_2":
        
        game = Game(s_instructions = ss, b_log_turn_time = True
                        , b_log_num_available = True )  
        game.play()

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


def print_indv_turn_times(data):
    pass    


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

def print_test_results(results):

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

    #('Col Heading', chars_in_col, chars_spacer_right, char_round)
    dims_out = [
        ('Test Name:', 15, 5, 15)
        ,('Avg Time:', 15, 5, 7)
        ,('Diff from baseline:', 20, 5, 4)
        ,('n:', 5, 5, 4)
        ,('Total Time:', 15, 5, 5)
        ]

    #print col heading
    s_row = ""
    for col in dims_out:
        s_row += align_col(col[0], chars_=col[1] )
        s_row += align_col('', chars_ = col[2])
    print s_row

    #print data
    for row in temp:
        
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




def interpret_results(results):
    pass
    #need to not use index-0 on log_turn_time
    



def perf_test(s_tests
                ,n=10 
                ,b_by_trial=False
                ,b_num_available=False
                ,b_turn_time=False
                ):
    
    # Heirarchy------------------------------
    # result         - a set of tests
    #   test         - a set of full games
    #       trial    - one full game
    #           turn - one move in the game

    result = {}
    

    
    for i_test, s_test in enumerate(s_tests):
    
        trial_time = []
        trial_turn_time = []
        trial_num_available = []

        t0 = time.time()
        
        for trial_i in range(n):
            
            t0_trial = time.time()
            opt_game_log = select_function(s_test)  #call main
            t1_trial = time.time()

            #any data from each run of .play()
            if b_by_trial:    
                trial_time.append(t1_trial - t0_trial)
                    
            if b_turn_time:
                trial_turn_time.append( opt_game_log.get_log_turn_time() )
            
            if b_num_available:
                trial_num_available.append( opt_game_log.get_log_num_available() )
                    
        t1 = time.time() 

        #logging 
        test = {}
        
        test['test_name'] = s_test
        test['order'] = i_test      #to print out results in correct order
        test['n'] = n
        test['total_time'] = t1 - t0
        
        if b_turn_time:
            test['turn_time'] = trial_turn_time
        if b_num_available:
            test['num_available'] = trial_num_available
        # if b_each_turn:
        #     pass

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

results = perf_test(s_tests,n=10)
print_test_results(results)

#TEMP - For building new features
s_tests = [
    "example_return_2"
    ]
results = perf_test(s_tests,n=2, b_turn_time=True, b_num_available=True)
my_test = results["example_return_2"]
print my_test
my_metric = my_test["turn_time"]
print "\n".join([str(x)[:4] for x in my_metric[0]])
print '---------'
print "\n".join([str(x)[:4] for x in my_metric[1]])
my_metirc2 = my_test["num_available"]
print my_metirc2


# print "".join([ k +":\n" for k in results.keys()]

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
