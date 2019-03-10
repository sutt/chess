import os
from .p_demo.p_import import ppath as  import_ppath
from .brother_import import ppath as brother_ppath
from .p_demo.p_2.p_import_2 import find_path

def get_rel_path():
    try:
        return os.path.relpath(os.path.dirname(__file__))
    except:
        return ""

print(__name__ + '\n')

print(' __file__:   %s'    % __file__)

print(' dirname :   %s'     % os.path.dirname(__file__))

print(' cwd     :   %s'     % os.getcwd())

print(' relpath :   %s'     % get_rel_path())

print(' abspath :   %s'     % os.path.abspath(get_rel_path())) 

print('\n')

import_ppath()

brother_ppath()

find_path()



