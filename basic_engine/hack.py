from main import Game
from utils import test_pgn_parse_2
from main import *


batchtest_multi_pgn_games_1(naive_check=False, max_games = 500)

# game_i = 13
# data_path = 'data/GarryKasparovGames.txt'
# f = open(data_path, 'r')
# lines = f.readlines()
# f.close()
# s_game = lines[game_i]

# # print s_game
# game = Game(s_pgn_instructions = s_game)
# ret = game.play(king_in_check_on = True, king_in_check_test_copy_apply_4 = False)
# # ret = game.play()
# print ret

# line_i:  1   secs:  0
# Move Incompatibility | line_i:  14
# game.i_turn:  9
# On PGN turn:  5  Player:  White
# Move Incompatibility | line_i:  17
# game.i_turn:  13
# On PGN turn:  7  Player:  White
# Error in play() | line_i:  20
# expected a string or other character buffer object
# line_i:  21   secs:  3
# Error in play() | line_i:  24
# expected a string or other character buffer object
# line_i:  41   secs:  3
# Error in play() | line_i:  43
# expected a string or other character buffer object
# Error in play() | line_i:  49
# expected a string or other character buffer object
# Error in play() | line_i:  52
# expected a string or other character buffer object
# Error in play() | line_i:  59
# expected a string or other character buffer object

# test_pgn_parse_2()
# test_pgn_parse()
# test_multi_pgn_games_1()
# test_checkmate_returncode_1()
# test_checkmate_simple_1()
# test_cant_castle_into_check_1()
# test_pawn_check_true_positive_1()

#PGN Setup

#a kasparov game
# ss_pgn = '1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7 '

# My game witha  promotion on turn ~95, breaks turn 97?
ss_pgn = "1. e4 Nh6 2. d4 c5 3. c3 g6 4. Nf3 Ng4 5. h3 d5 6. hxg4 dxe4 7. Nfd2 e3 8. fxe3 cxd4 9. cxd4 Bxg4 10. Qxg4 f6 11. Qe4 Qd6 12. Qxb7 Qg3+ 13. Kd1 a5 14. Qxa8 Bg7 15. Ne4 Qc7 16. Bb5+ Kf7 17. Nbc3 Qb6 18. Qd5+ Qe6 19. Bc4 Qxd5 20. Bxd5+ e6 21. Nd6+ Ke7 22. Nde4 g5 23. Bb3 Kf8 24. Rf1 Nc6 25. Nxf6 Nb4 26. Nxh7+ Ke8 27. Nxg5 e5 28. Bf7+ Kd7 29. dxe5 Rh2 30. e6+ Kd8 31. a3 Bxc3 32. axb4 Bxb4 33. Bd2 Bxd2 34. Kxd2 Rxg2+ 35. Kd3 Rxg5 36. Rfd1 Rd5+ 37. Ke2 Rxd1 38. Rxd1+ Ke7 39. Rd7+ Kf6 40. e4 a4 41. Ke3 Kg7 42. e5 Kf8 43. Rd8+ Kg7 44. Kd4 a3 45. bxa3 Kh6 46. e7 Kh7 47. e8=Q Kh6 48. Rd6+ Kg5 49. Qg8+ Kf4 50. Qh8 Kf3 51. Qh5+ Kf2 52. Rf6+ Kg2 53. Qf3+ Kg1 54. Qf2+ Kh1 55. Rh6# 1-0"

#Heres where the problems start...Kf4 (for black) isn't available from my in_check() module. Prolly because it sees pawn diagonally attacking backwards?
#47. e8=Q Kh6 48. Rd6+ Kg5 49. Qg8+ ... !!! Kf4 !!! 50. Qh8 Kf3 51. Qh5+ Kf2 52. Rf6+ Kg2 53. Qf3+ Kg1 54. Qf2+ Kh1 55. Rh6# 1-0"

# game = Game(s_pgn_instructions = ss_pgn
#             ,pgn_control = (0,1)
#             ,b_log_move = True
#             ,test_exit_moves = 98
#             ,b_display_always_print = True
#             )
# ret = game.play()
# print ret

#Printout a game to observe it
# ss_long = '1. g1 e1 2. b1 d1 3. g2 e2 4. b3 d3 5. e2 d3 6. b6 d6 7. g5 e5 8. a2 c3 9. h4 d8 10. b7 c7 11. h6 c1 12. a1 c1 13. h1 f1 14. a6 c8 15. h7 f6 16. b2 d2 17. h3 g2 18. a5 a6 19. e1 d2 20. c8 d7 21. d8 c7 22. d7 e6 23. h5 h7 24. b8 c8 25. g3 e3 26. e6 b3 27. g7 e7 28. c3 e4 29. c7 b7 30. a6 a5 31. b7 c7 32. c1 c7 33. d2 c2 34. b4 d4 35. f6 e4 36. d6 e5 37. h2 f3 38. c8 d8 39. f1 d1 40. c7 c4 '            
# game = Game(s_instructions = ss_long
#         ,test_exit_moves = None
#         ,b_display_show_opponent = True
#         ,b_log_move = True
#         )

# game.play(king_in_check_on=False, king_in_check_test_copy_apply_4=True)