import os, sys

#duplicate from basic_engine/src/utils
def find_app_path_root(input_file, find_dir = "chess"):
    ''' input:  input_file - pass in __file__
        return: a relative-path to folder or None '''
    
    _path = os.path.abspath(os.path.dirname(input_file))
    
    while(True):
    
        _head, _tail = os.path.split(_path)
        
        if _head == _path:
            return None
        
        if str.lower(_tail) == str.lower(find_dir):
            return os.path.relpath(_path, start = os.getcwd())
        
        _path = _head