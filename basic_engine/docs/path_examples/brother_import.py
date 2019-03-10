import os

def ppath():
    print(__name__ + '\n')
    
    print(' __file__:   %s'    % __file__)

    print(' dirname :   %s'     % os.path.dirname(__file__))
    
    print(' cwd     :   %s'     % os.getcwd())
    
    print(' relpath :   %s'     % os.path.relpath(os.path.dirname(__file__)))

    print('\n')








