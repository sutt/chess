import sys
import cProfile
import pstats
sys.path.append('../')

from src.main import Game

ss = "1. g1 h3 2. a7 a6 3. e2 e4 4. b7 b6 5. f1 d3 6. c7 c6 7. e1 f1 8. d7 d6 9. f1 e1 10. e7 e6"


#os.chdir("c:/users/wsutt/desktop/files/exercises/chess/basic_engine/")


def run_profiles():
    
    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(filter_check_naive=False)"""
    cProfile.run( cmd, 'output_profile_1')

    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(filter_check_naive=False """
    cmd += """          ,filter_check_test_copy_apply=True """
    cmd += """          )"""
    cProfile.run( cmd, 'output_profile_2')
    
    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(filter_check_naive=True)"""
    cProfile.run(cmd, 'output_profile_3')

    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(filter_check_naive=False """
    cmd += """          ,filter_check_test_copy_opt=True """
    cmd += """          )"""
    cProfile.run( cmd, 'output_profile_4')

def display_profiles(fn, amt=10):
    p = pstats.Stats(fn)
    p.strip_dirs()
    p.sort_stats('cumulative')
    p.print_stats(amt)
    p.print_stats('basic', 'get_available_moves')

if __name__ == "__main__":
    run_profiles()
    display_profiles('output_profile_1')
    display_profiles('output_profile_2')
    display_profiles('output_profile_3')
    display_profiles('output_profile_4', amt = 15)


   
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