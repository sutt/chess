import sys
import cProfile
import pstats
import argparse
sys.path.append('../')

from src.main import Game

DATA_DIR = '../data/profiles/'

ap = argparse.ArgumentParser()
ap.add_argument("--full", action="store_true")
args = vars(ap.parse_args())


# s_instruct = "1. g1 h3 2. a7 a6 3. e2 e4 4. b7 b6 5. f1 d3 6. c7 c6 7. e1 f1 8. d7 d6 9. f1 e1 10. e7 e6"


fn = [
         'profile_baseline_no_filter_check'
        ,'profile_naive_filter_check'
        ,'profile_test_copy_opt'
        ,'profile_test_copy_opt'
    ]

fn = [DATA_DIR + _fn for _fn in fn]


def run_profiles(s_inp_instruct, file_names = fn):
    ''' output cProfile files for different filter_check algos '''
    
    s2 = s_inp_instruct
    cmd =  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_opt=False, check_for_check=False)"""
    cProfile.run( cmd, fn[0])

    cmd =  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_naive=True """
    cmd += """          ,filter_check_opt=True """
    cmd += """          , check_for_check=False """
    cmd += """          )"""
    cProfile.run( cmd, fn[1])
    
    cmd =  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_test_copy_opt=True, check_for_check=False)"""
    cProfile.run(cmd, fn[2])

    cmd =  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_opt=True, check_for_check=False) """
    cProfile.run( cmd, fn[3])


def display_profiles(fn, amt=10, b_full=True):
    p = pstats.Stats(fn)
    p.strip_dirs()
    if b_full:
        p.sort_stats('cumulative')
        p.print_stats(amt)
    p.print_stats('basic', 'get_available_moves')


if __name__ == "__main__":

    # s_instruct = "1. g1 h3 2. a7 a6 3. e2 e4 4. b7 b6 5. f1 d3 6. c7 c6 7. e1 f1 8. d7 d6 9. f1 e1 10. e7 e6"  
    # run_profiles(s_inp_instruct = s_instruct, file_names = fn)
    s_instruct = "1. g1 h3"  
    run_profiles(s_inp_instruct = s_instruct, file_names = fn)
    
    #TODO - need to turn off is_king_in_check() for accurate 
    #       assessment of get_available_moves on one turn

    b_full = args["full"]
    display_profiles(fn[0], b_full=b_full)
    display_profiles(fn[1], b_full=b_full)
    display_profiles(fn[2], b_full=b_full)
    display_profiles(fn[3], b_full=b_full, amt = 15)

# 4/9

# C:\Users\wsutt\Desktop\files\chess\basic_engine\tools>python profile_test.py
# Mon Apr 09 13:50:42 2018    ../data/profiles/profile_baseline_no_filter_check

#          5830 function calls (4749 primitive calls) in 0.005 seconds

#    Random listing order was used
#    List reduced from 86 to 31 due to restriction <'basic'>
#    List reduced from 31 to 1 due to restriction <'get_available_moves'>

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        16    0.000    0.000    0.001    0.000 basic.py:406(get_available_moves)


# Mon Apr 09 13:50:42 2018    ../data/profiles/profile_naive_filter_check

#          103127 function calls (83626 primitive calls) in 0.061 seconds

#    Random listing order was used
#    List reduced from 98 to 32 due to restriction <'basic'>
#    List reduced from 32 to 1 due to restriction <'get_available_moves'>

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#       356    0.003    0.000    0.015    0.000 basic.py:406(get_available_moves)


# Mon Apr 09 13:50:43 2018    ../data/profiles/profile_test_copy_opt

#          7646 function calls (6565 primitive calls) in 0.009 seconds

#    Random listing order was used
#    List reduced from 95 to 32 due to restriction <'basic'>
#    List reduced from 32 to 1 due to restriction <'get_available_moves'>

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        36    0.000    0.000    0.003    0.000 basic.py:406(get_available_moves)


# Mon Apr 09 13:50:43 2018    ../data/profiles/profile_test_copy_opt

#          7646 function calls (6565 primitive calls) in 0.009 seconds

#    Random listing order was used
#    List reduced from 95 to 32 due to restriction <'basic'>
#    List reduced from 32 to 1 due to restriction <'get_available_moves'>

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        36    0.000    0.000    0.003    0.000 basic.py:406(get_available_moves)

   
# 2/9

# NOTE: naive_check uses ~20x ncalls and ~20x time 160 * ~20 -> 3820.
#       This is because you take each turn where there's roughly 20 moves.
#       But, optimal_check uses ~2x (2X + 1) the ncalls and ~3x the time,
#       because the mirror.get_available is a "super piece" with ~3x the moves
#       of a normal piece: upacross, diag, and twobyone vs. only one of these.

# NOTE: TurnStage:get_available_moves is a step within game(), not a computing step.

#    profile1 - no check_filter

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#       160    0.001    0.000    0.004    0.000 basic.py:400(get_available_moves)

#    profile3 - naive check_filter

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#      3820    0.020    0.000    0.111    0.000 basic.py:400(get_available_moves)

#    profile4 - optimal check_filter

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#       389    0.002    0.000    0.017    0.000 basic.py:400(get_available_moves)