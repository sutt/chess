import sys
import cProfile
import pstats
import argparse
import copy
sys.path.append('../')
# sys.path.append('../src/')

from src.main import Game
# from main import Game

DATA_DIR = '../data/profiles/'


#TODO - get rid of this stuff
#TODO - add DATA_DIR into classes
fn = [
         'profile_filter_check_none'
        ,'profile_naive_filter_check'
        ,'profile_test_copy_opt'
        ,'profile_opt'
    ]

fn = [DATA_DIR + _fn for _fn in fn]

# -----------------------------------------------------------------------------
#   Helper Functions to run Batch cProfiles
#------------------------------------------------------------------------------


def pretty_print(d):
    out = ""
    for k in d.keys():
        out += str(k)
        out += " : "
        out += str(d[k])
        out += "\n"
    print out


def build_code_str(s_instruct, d_params, b_import=True):
    
    ''' Build the str of commands fed into runctx. 
        input:   d_params (dict) 
        returns: cmd (str) 
        '''

    # TODO - add b_pgn for non A1-instructions
    
    cmd = ""
    
    if b_import:
        cmd += "from src.main import Game; "

    temp_cmd = 'game = Game(s_instructions="' + s_instruct + '"); '
    cmd += temp_cmd

    cmd += "game.play("

    args_cmd = ""
    comma_sw = False
    for k in d_params:
        arg_cmd = ""
        if comma_sw: 
            arg_cmd = ","
        arg_cmd += k
        arg_cmd += "="
        arg_cmd += str(d_params[k])
        args_cmd += arg_cmd
        comma_sw = True

    cmd += args_cmd
    cmd += ");"

    return cmd


def run_profiles(s_instruct):
    ''' Modularized function for running '''
    #TODO - output to file optional
    cProfile.runctx( s_cmd, globals(), locals(), file_names[0])


def display_profiles(fn, amt=10, b_full=False):
    #TODO - add sel_list optional arg for non-get_available functions
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


# ------------------------------------------------------------------------
#   Build Batch Experiments Instances
# -----------------------------------------------------------------------


class TestArgs:
    
    ''' Holds the kwargs for Game.play() each cProfile run:
            set_base_arg makes each test element have those values.
            add_test adds a test element, with one different arg / arg-value.
    '''
    
    def __init__(self):
        self.base_args = {}
        self.test_data = {}

    def set_base_arg(self, tuple_param):
        k, v = tuple_param[0], tuple_param[1]
        self.base_args[k] = v

    def get_test_data(self):
        return copy.copy(self.test_data)

    def add_test(self, inp):
        ''' input: (test_name [str], (arg_key [str], arg_val [bool]))'''
        
        test_name = inp[0]
        args = copy.copy(self.base_args)
        
        if inp[1] is not None:
            arg_key, arg_val = inp[1][0], inp[1][1]    
            args[arg_key] = arg_val

        self.test_data[test_name] = args


if __name__ == "__main__":


    #different filter_check algos
    d_params = TestArgs()
    d_params.set_base_arg(('check_for_check', False))
    d_params.set_base_arg(('filter_check_opt', False))

    d_params.add_test(('filter_check_none',         None)) 
    d_params.add_test(('filter_check_naive',        ('filter_check_naive', True)))
    d_params.add_test(('filter_check_test_copy',    ('filter_check_test_copy_opt', True)))
    d_params.add_test(('filter_check_opt',          ('filter_check_opt', True)))

    # pretty_print(d_params.get_test_data())
    
    #bypass on/off with filter_check_opt
    d_params = TestArgs()
    d_params.set_base_arg( ('check_for_check', False))
    d_params.set_base_arg( ('filter_check_opt', True))

    d_params.add_test(('bypass_on',     ('bypass_irregular', True)))
    d_params.add_test(('bypass_off',    ('bypass_irregular', False)))

    # pretty_print(d_params.get_test_data())

    #bypass on with filter_check_opt / filter_check_naive
    d_params = TestArgs()
    d_params.set_base_arg( ('check_for_check', False))
    d_params.set_base_arg( ('filter_check_opt', False))
    d_params.set_base_arg( ('bypass_irregular', True))

    d_params.add_test(('bypass_naive',        ('filter_check_naive', True)))
    d_params.add_test(('bypass_opt',          ('filter_check_opt', True)))

    # pretty_print(d_params.get_test_data())


# ---------------------------------------------------------------------
#       Main Section - for calling this utility directly
#----------------------------------------------------------------------


if __name__ == "__main__":
    
    print 'into main section'

    ap = argparse.ArgumentParser()
    ap.add_argument("--current", action="store_true")
    args = vars(ap.parse_args())

    if args["current"]:
        
        print '\nShowing current profile on long game, with params:'
        print 'TODO - parameters here \n'
        
        s_instruct = '1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 O-O 8. h3 Bb7 9. d3 d6 10. a3 Na5 11. Ba2 c5 12. Nc3 Nc6 13. Bg5 Qd7 14. Nh2 Ne8 15. Bd2 Nc7 16. Nf1 Kh8 17. Ng3 Nd4 18. Nce2 Nde6 19. b4 d5 20. bxc5 Bxc5 21. Bb4 Rfe8 22. Bxc5 Nxc5 23. Nc3 Rad8 24. Qh5 f6 25. d4 exd4 26. Nxd5 Re5 27. Qh4 Nxd5 28. exd5 Bxd5 29. Rxe5 fxe5 30. Bxd5 Qxd5 31. Re1 Ne6 32. Nf5 Nf4 33. Qg5 Rd7 34. Nh4 h6 35. Qg4 g5 36. Nf3 e4 37. Rxe4 Qxe4 38. Qxd7 d3 39. cxd3 Qxd3 40. Qc8+ Kg7 41. Qb7+ Kg8 42. Qxa6 Ne2+ 43. Kh2 Qe4 44. Qf6 Qf4+ 45. Qxf4 gxf4 46. g4 fxg3+ 47. fxg3 Nc3 48. Nd4 h5 49. h4 Kf7 50. Kh3 Kf6 51. g4 hxg4+ 52. Kxg4 Kg6 53. h5+ Kh7 54. Kh4 Kg8 55. h6 Kh7 56. Kh5 Ne4 57. Nxb5 Nf6+ 58. Kg5 Ne4+ 59. Kf5 Nc5 60. Ke5 Kxh6 61. Kd4 Na6 62. Kd5 Kg6 63. Nd4 Kf6 64. Kd6 Kf7 65. Ne6 '
        run_profiles(s_instruct = s_instruct, file_names = fn)
        
        display_profiles(fn[3], b_full=True, amt=30)


    else:
        
        print '\nShowing the difference between filter_check algos'
        print 'using only the opening move.'

        s_instruct = "1. g1 h3"  
        run_profiles(s_instruct = s_instruct, file_names = fn)

        print 
        display_profiles(fn[0])
        display_profiles(fn[1])
        display_profiles(fn[2])
        display_profiles(fn[3], amt = 15)


# --------------------------------------------------------------------
#       Profile Tests - assessing ncalls based on different algos
# --------------------------------------------------------------------

# def test_opening_move_ncalls_get_available():
#     ''' Test that each form of filter_check makes correct number calls to
#         basic.get_available_moves(). Using opening move as baseline'''

#     fn = [
#          'profile_baseline_no_filter_check'
#         ,'profile_naive_filter_check'
#         ,'profile_test_copy_opt'
#         ,'profile_opt'
#     ]

#     DATA_DIR = '../data/profiles/'
#     fn = [DATA_DIR + _fn for _fn in fn]

#     s_instruct = "1. g1 h3"  
#     run_profiles(s_instruct = s_instruct, file_names = fn)

#     assert 16 == return_ncalls(fn[0])   #baseline - no check_filter

#     #There are 16 pieces white can use:
#     #   16 =  calls once for each

#     assert 336 == return_ncalls(fn[1])   #naive_check

#     #There are 20 moves (for 16 pieces) white can make.
#     #For each move, there are 16 pieces for black we need to examine.
#     #   320 = 20 * 16
#     #   336 = 320 + 16 (to populate white's moves in play)

#     assert 36 == return_ncalls(fn[2])   #test_copy_opt

#     #This is a test filter_check, but uses get_check_optimal,
#     #So there should be no difference in calls to get_available_moves.

#     assert 36 == return_ncalls(fn[3])   #filter_check_opt

#     #First add the 16 calls to populate moves.
#     #There are 20 moves for white, so for each of these, need to make
#     #a get_available_moves on white's super_king piece. But never
#     #need to make a call to black's pieces.
#     #   36 = 16 + 20


# def test_bypass_irregular_less_moves():
#     ''' Test that bypass_irregular kwarg is having an effect by checking
#         that there are less calls to get_check_optimal 
#         or get_available_moves. '''

#     #A game with castling, therefore we know it was an available move at some point
#     s = '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7'

#     fn_test = ['profile_bypass_on', 'profile_bypass_off']
#     fn_test = [DATA_DIR + _fn for _fn in fn_test]
#     run_profiles_2(_s = s, fn = fn_test)

#     bypass_on_ncalls = return_ncalls(fn_test[0]
#                             ,sel_list=('TurnStage', 'get_possible_check_optimal')
#                             )
#     bypass_off_ncalls = return_ncalls(fn_test[1]
#                             ,sel_list=('TurnStage', 'get_possible_check_optimal')
#                             )

#     assert bypass_on_ncalls < bypass_off_ncalls


# ----------------------------------------------------------------------
#       Legacy Deprecated Functions
# ----------------------------------------------------------------------


def run_profiles(s_instruct, file_names):
    ''' output cProfile files for different filter_check algos '''
    
    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_opt=False, check_for_check=False)"""
    cProfile.runctx( cmd, globals(), locals(), file_names[0])

    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_naive=True """
    cmd += """          ,filter_check_opt=False """
    cmd += """          ,check_for_check=False """
    cmd += """          )"""
    # cProfile.run( cmd, fn[1])
    cProfile.runctx( cmd, globals(), locals(), file_names[1])
    
    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_test_copy_opt=True """
    cmd += """          ,filter_check_opt=False """
    cmd += """          ,check_for_check=False """
    cmd += """          )"""
    # cProfile.run(cmd, fn[2])
    cProfile.runctx( cmd, globals(), locals(), file_names[2])

    cmd = """from src.main import Game; """
    cmd +=  """game = Game(s_instructions = s_instruct); """
    cmd += """game.play(filter_check_opt=True, check_for_check=False) """
    # cProfile.run( cmd, fn[3])
    cProfile.runctx( cmd, globals(), locals(), file_names[3])


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



# --------------------------------------------------------
#      Unit Tests for the helper functions
#---------------------------------------------------------

def test_pyconcept_pass_by_ref_dict():
    
    ''' Testing neccesity of copy() for dicts. '''

    d0 = {}
    d0['one'] = 1
    ref0 = d0
    ref0['two'] = 2
    ref0['one'] = 17

    d1 = {}
    d1['one'] = 1
    ref1 = copy.copy(d0)
    ref1['two'] = 2
    ref1['one'] = 17

    print 'd0: ',   str(d0)
    print 'ref0: ', str(ref0)
    print 'd1: ',   str(d1)
    print 'ref1: ', str(ref1)

    assert  ref0 == d0      #without copy, you overide
    assert not(ref1 == d1)  #with copy.copy you're OK.


def test_testargs_class_1():
    
    ''' Testing methods of TestArgs class'''

    testArgs = TestArgs()
    testArgs.set_base_arg(('base1', True))
    testArgs.set_base_arg(('base2', False))
    testArgs.add_test(('test_1',('test_arg1', True)))   # only this one
    testArgs.add_test(('test_2',('base1', False)))      # overwrite

    data = testArgs.get_test_data()

    # verify test records exist
    test_1 = data.get('test_1', None)
    assert test_1 is not None
    test_2 = data.get('test_2', None)
    assert test_2 is not None

    #verify base and test args exist
    assert test_2.get('base1', None) is not None
    assert test_2.get('base2', None) is not None
    
    assert test_2.get('test_arg1', None) is None
    assert test_1.get('test_arg1', None) is not None    # only this one
    
    # verify base1 is overwritten correctly
    assert test_1.get('base1', None) == True
    assert test_2.get('base1', None) == False           # overwrite

    #verify no pass by ref between test_data records
    test_1['base2'] = 99
    assert test_2['base2'] == False
    data2 = testArgs.get_test_data()
    test_3 = data2.get('test_2', None)
    assert test_3.get('base2', None) is not None
    assert test_3.get('base2', None) == False           # overwrite
    # print 'done.'


def test_build_code_str():
    
    '''Test build_code_str'''
    
    d_params = TestArgs()
    d_params.set_base_arg( ('check_for_check', False))
    d_params.set_base_arg( ('filter_check_opt', True))
    d_params.add_test(('bypass_on',     ('bypass_irregular', True)))
    d_params.add_test(('bypass_off',    ('bypass_irregular', False)))

    test_data = d_params.get_test_data()

    list_s_cmd = []
    
    for test_key in test_data.keys():
        
        test_name = str(test_key)
        test_params = test_data[test_key]
        test_s_instruct = "1. g1 h3"  
        
        s_cmd = build_code_str(
                                s_instruct = test_s_instruct
                                ,d_params = test_params
                                ,b_import = True
                                )
        
        list_s_cmd.append(s_cmd)

    #Now test the strings:
    assert list_s_cmd[0] == """from src.main import Game; game = Game(s_instructions="1. g1 h3"); game.play(filter_check_opt=True,check_for_check=False,bypass_irregular=True);"""
    assert list_s_cmd[1] == """from src.main import Game; game = Game(s_instructions="1. g1 h3"); game.play(filter_check_opt=True,check_for_check=False,bypass_irregular=False);"""


# --------------------------------------------------------------------
#       Data Scratchpad
# --------------------------------------------------------------------



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