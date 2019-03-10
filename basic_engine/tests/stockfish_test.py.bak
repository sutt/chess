import unittest
import time
from os import path
import sys
import subprocess


if __name__ == '__main__' and __package__ is None:
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from src.StockfishNetwork import StockfishNetworking
else:
    #for intellisense
    from ..src.StockfishNetwork import StockfishNetworking



class TestSetup(unittest.TestCase):

    def setUp(self):
        
        time.sleep(0.1)     #needed to release SN class or tmp.txt file?
        
        self.t0 = time.time()
        
        self.stockConn = StockfishNetworking(
                                 b_launch_server=True
                                ,b_read_stderr=True
                                )
        
        self.t1 = time.time()


    def tearDown(self):
        self.stockConn = None       #kill server for next test


    def test_setup_time(self):
        ''' test the launch time of the server '''
        
        self.assertTrue(self.t1 - self.t0 > 0.1)
        self.assertTrue(self.t1 - self.t0 < 1.5)

    
    def test_response_time(self):
        ''' test http response time'''

        response_t0 = time.time()
        self.assertTrue(self.stockConn._check_server_is_up())
        response_t1 = time.time()

        print 'response time: %s' % str(response_t1 - response_t0)[:7]
        self.assertTrue(response_t1 - response_t0 > 0.001)
        self.assertTrue(response_t1 - response_t0 < 0.1)

    
    def test_teardown(self):
        pass



    
    def _check_wsl_ps(self):
        self.assertFalse(True)  #underscore func name means its not collected by test discover

if __name__ == '__main__':
    unittest.main()