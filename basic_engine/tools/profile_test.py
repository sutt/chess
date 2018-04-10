import sys
import cProfile
import pstats
import argparse
sys.path.append('../')

from src.main import Game

DATA_DIR = '../data/profiles/'


fn = [
         'profile_baseline_no_filter_check'
        ,'profile_naive_filter_check'
        ,'profile_test_copy_opt'
        ,'profile_opt'
    ]

fn = [DATA_DIR + _fn for _fn in fn]


def run_profiles(s_instruct, file_names = fn):
    ''' output cProfile files for different filter_check algos '''
    
    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_opt=False, check_for_check=False)"""
    cProfile.runctx( cmd, globals(), locals(), fn[0])

    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_naive=True """
    cmd += """          ,filter_check_opt=False """
    cmd += """          ,check_for_check=False """
    cmd += """          )"""
    # cProfile.run( cmd, fn[1])
    cProfile.runctx( cmd, globals(), locals(), fn[1])
    
    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_test_copy_opt=True """
    cmd += """          ,filter_check_opt=False """
    cmd += """          ,check_for_check=False """
    cmd += """          )"""
    # cProfile.run(cmd, fn[2])
    cProfile.runctx( cmd, globals(), locals(), fn[2])

    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_opt=True, check_for_check=False) """
    # cProfile.run( cmd, fn[3])
    cProfile.runctx( cmd, globals(), locals(), fn[3])


def run_profiles_2(_s, fn):
    ''' output cProfile files with bypass on/off '''
    
    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_pgn_instructions = _s); """
    cmd += """game.play(bypass_irregular=True, check_for_check=False)"""
    cProfile.runctx( cmd, globals(), locals(), fn[0])

    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_pgn_instructions = _s); """
    cmd += """game.play(bypass_irregular=False, check_for_check=False)"""
    cProfile.runctx( cmd, globals(), locals(), fn[1])


def display_profiles(fn, amt=10, b_full=True):
    p = pstats.Stats(fn)
    p.strip_dirs()
    if b_full:
        p.sort_stats('cumulative')
        p.print_stats(amt)
    p.print_stats('basic', 'get_available_moves')


def return_ncalls( fn
                   ,sel_list = ('basic', 'get_available_moves')
                 ):
    ''' get a machine readable value of n calls '''
    p = pstats.Stats(fn)
    k_plus = p.get_print_list(sel_list)
    k = k_plus[1][0]
    d = p.stats
    stats = d[k]
    ncalls = stats[0]
    return ncalls
    
    

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    args = vars(ap.parse_args())
    
    s_instruct = "1. g1 h3"  

    run_profiles(s_instruct = s_instruct, file_names = fn)

    b_full = args["full"]
    display_profiles(fn[0], b_full=b_full)
    display_profiles(fn[1], b_full=b_full)
    display_profiles(fn[2], b_full=b_full)
    display_profiles(fn[3], b_full=b_full, amt = 15)


def test_opening_move_ncalls_get_available():
    ''' Test that each form of filter_check makes correct number calls to
        basic.get_available_moves(). Using opening move as baseline'''

    fn = [
         'profile_baseline_no_filter_check'
        ,'profile_naive_filter_check'
        ,'profile_test_copy_opt'
        ,'profile_opt'
    ]

    DATA_DIR = '../data/profiles/'
    fn = [DATA_DIR + _fn for _fn in fn]

    s_instruct = "1. g1 h3"  
    run_profiles(s_instruct = s_instruct, file_names = fn)

    assert 16 == return_ncalls(fn[0])   #baseline - no check_filter

    #There are 16 pieces white can use:
    #   16 =  calls once for each

    assert 336 == return_ncalls(fn[1])   #naive_check

    #There are 20 moves (for 16 pieces) white can make.
    #For each move, there are 16 pieces for black we need to examine.
    #   320 = 20 * 16
    #   336 = 320 + 16 (to populate white's moves in play)

    assert 36 == return_ncalls(fn[2])   #test_copy_opt

    #This is a test filter_check, but uses get_check_optimal,
    #So there should be no difference in calls to get_available_moves.

    assert 36 == return_ncalls(fn[3])   #filter_check_opt

    #First add the 16 calls to populate moves.
    #There are 20 moves for white, so for each of these, need to make
    #a get_available_moves on white's super_king piece. But never
    #need to make a call to black's pieces.
    #   36 = 16 + 20


def test_bypass_irregular_less_moves():
    ''' Test that bypass_irregular kwarg is having an effect by checking
        that there are less calls to get_check_optimal 
        or get_available_moves. '''

    #A game with castling, therefore we know it was an available move at some point
    s = '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7'

    fn_test = ['profile_bypass_on', 'profile_bypass_off']
    fn_test = [DATA_DIR + _fn for _fn in fn_test]
    run_profiles_2(_s = s, fn = fn_test)

    bypass_on_ncalls = return_ncalls(fn_test[0]
                            ,sel_list=('TurnStage', 'get_possible_check_optimal')
                            )
    bypass_off_ncalls = return_ncalls(fn_test[1]
                            ,sel_list=('TurnStage', 'get_possible_check_optimal')
                            )

    assert bypass_on_ncalls < bypass_off_ncalls


#4/10

# Tue Apr 10 14:24:18 2018    ../data/profiles/profile_baseline_no_filter_check
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        16    0.000    0.000    0.000    0.000 basic.py:406(get_available_moves)


# Tue Apr 10 14:24:18 2018    ../data/profiles/profile_naive_filter_check
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#       336    0.002    0.000    0.011    0.000 basic.py:406(get_available_moves)


# Tue Apr 10 14:24:18 2018    ../data/profiles/profile_test_copy_opt
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        36    0.000    0.000    0.002    0.000 basic.py:406(get_available_moves)


# Tue Apr 10 14:24:18 2018    ../data/profiles/profile_opt
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        36    0.000    0.000    0.002    0.000 basic.py:406(get_available_moves)

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