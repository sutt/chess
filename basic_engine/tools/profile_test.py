import cProfile
import pstats

from main import Game

ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5"
ss_long = '1. g1 e1 2. b1 d1 3. g2 e2 4. b3 d3 5. e2 d3 6. b6 d6 7. g5 e5 8. a2 c3 9. h4 d8 10. b7 c7 11. h6 c1 12. a1 c1 13. h1 f1 14. a6 c8 15. h7 f6 16. b2 d2 17. h3 g2 18. a5 a6 19. e1 d2 20. c8 d7 21. d8 c7 22. d7 e6 23. h5 h7 24. b8 c8 25. g3 e3 26. e6 b3 27. g7 e7 28. c3 e4 29. c7 b7 30. a6 a5 31. b7 c7 32. c1 c7 33. d2 c2 34. b4 d4 35. f6 e4 36. d6 e5 37. h2 f3 38. c8 d8 39. f1 d1 40. c7 c4 '

#os.chdir("c:/users/wsutt/desktop/files/exercises/chess/basic_engine/")


def run_profiles():
    
    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(king_in_check_on=False)"""
    cProfile.run( cmd, 'output_profile_1')

    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(king_in_check_on=False """
    cmd += """          ,king_in_check_test_copy_apply=True """
    cmd += """          )"""
    cProfile.run( cmd, 'output_profile_2')
    
    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(king_in_check_on=True)"""
    cProfile.run(cmd, 'output_profile_3')

    cmd =  """game = Game(s_instructions = ss); """
    cmd += """game.play(king_in_check_on=False """
    cmd += """          ,king_in_check_optimal=True """
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