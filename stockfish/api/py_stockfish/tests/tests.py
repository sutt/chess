import os, sys, time
import unittest

# print(*sys.path, sep='\n')
# print(os.getcwd())

from pystockfish.stockfish import Stockfish
from .utils import find_app_path_root


class TestStockfish(unittest.TestCase):

    def setUp(self):
        
        time.sleep(1)
        
        root_dir = find_app_path_root(__file__)
        
        if os.name == 'posix':
            exec_name = 'stockfish'
        elif os.name == 'nt':
            # this program was ultimately compiled for windows
            # so we can run it from a python+windows subproc 
            exec_name = 'stockfish-32.exe'
        else:
            print('failed to find a supported os; exiting tests')
            sys.exit(-1)

        stockfish_path = os.path.join(   root_dir, 
                                        'stockfish', 
                                        'Stockfish', 
                                        'bin', 
                                        exec_name
                                        )

        self.stockfish = Stockfish(path = stockfish_path)
        
        print('setup')

    def tearDown(self):
        del(self.stockfish)
        print('teardown')
        time.sleep(1)

    def test_get_best_move(self):
        best_move = self.stockfish.get_best_move()
        self.assertIn(best_move, ('e2e4', 'g1f3', 'b1c3',))

        self.stockfish.set_position(['e2e4', 'e7e6'])
        best_move = self.stockfish.get_best_move()
        self.assertIn(best_move, ('d2d4', 'g1f3',))

        # mate
        self.stockfish.set_position(['f2f3', 'e7e5', 'g2g4', 'd8h4'])
        self.assertFalse(self.stockfish.get_best_move())

        print('done with test1')

    def test_set_fen_position(self):
        self.stockfish.set_fen_position("7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27")
        self.assertTrue(self.stockfish.is_move_correct('f4f5'))
        self.assertFalse(self.stockfish.is_move_correct('a1c1'))

        print('done with test2')

    def test_is_move_correct(self):
        self.assertFalse(self.stockfish.is_move_correct('e2e1'))
        self.assertTrue(self.stockfish.is_move_correct('a2a3'))
        self.stockfish.set_position(['e2e4', 'e7e6'])
        self.assertFalse(self.stockfish.is_move_correct('e2e1'))
        self.assertTrue(self.stockfish.is_move_correct('a2a3'))

        print('done with test3')


if __name__ == '__main__':
    unittest.main()
