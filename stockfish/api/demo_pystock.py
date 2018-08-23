'''
    This is to test import/use of the stockfish library found here:
    https://pypi.org/project/stockfish/

    lib_stockfish.py is copied and then several functions are added.
'''

# from py_stockfish.stockfish.stockfish import Stockfish

from lib_stockfish import Stockfish

sf = Stockfish(path = "../Stockfish/src/stockfish")
best_move = sf.get_best_move()
print best_move

out = sf.get_position()
print out

