import sys
sys.path.append('../')

from src.main import Game
from src.utils import format_move_log

def convert_pgn_to_a1(s_pgn):
    ''' convert s_pgn to a1-tuple '''

    game = Game(s_pgn_instructions=s_pgn
                ,b_log_move=True
                )
    ret = game.play()
    gameLog = game.get_gamelog()
    s_instruct = format_move_log(gameLog.get_log_move())

    s_instruct = s_instruct.rstrip()
    s_instruct = s_instruct.lstrip()

    return s_instruct

if __name__ == "__main__":
    
    s_input = "1. c4"
    print convert_pgn_to_a1(s_input)


def test_convert_pgn_to_a1_1():
    ''' testing some string conversions'''
    
    #note turn8 has white castling
    s_input = "1. c4 Nf6 2. Nc3 g6 3. g3 c5 4. Bg2 Nc6 5. Nf3 d6 6. d4 cxd4 7. Nxd4 Bd7 8. O-O Bg7 9. Nxc6 Bxc6 10. e4 O-O 11. Be3 a6 12. Rc1 Nd7 13. Qe2 b5 14. b4 Ne5 15. cxb5 axb5 16. Nxb5 Bxb5 17. Qxb5 Qb8 18. a4 Qxb5 19. axb5 Rfb8 20. b6 Ng4 21. b7"
    
    s_output = convert_pgn_to_a1(s_input)
    
    ANSWER = "1. c2 c4 2. g8 f6 3. b1 c3 4. g7 g6 5. g2 g3 6. c7 c5 7. f1 g2 8. b8 c6 9. g1 f3 10. d7 d6 11. d2 d4 12. c5 d4 13. f3 d4 14. c8 d7 15. e1 g1 16. f8 g7 17. d4 c6 18. d7 c6 19. e2 e4 20. e8 g8 21. c1 e3 22. a7 a6 23. a1 c1 24. f6 d7 25. d1 e2 26. b7 b5 27. b2 b4 28. d7 e5 29. c4 b5 30. a6 b5 31. c3 b5 32. c6 b5 33. e2 b5 34. d8 b8 35. a2 a4 36. b8 b5 37. a4 b5 38. f8 b8 39. b5 b6 40. e5 g4 41. b6 b7"

    assert s_output == ANSWER
    


    

    