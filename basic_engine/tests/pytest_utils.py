import os
import sys
import shutil

sys.path.append("../")

from src.utils import find_app_path_root

def delete_pyc_files(p_local):
    ''' delete all .pyc files in p_local directory'''
    pyc_files = []
    local_files =  os.listdir(p_local)
    for fn in local_files:
        _ext = os.path.splitext(os.path.join(p_local, fn))
        if len(_ext) != 2:
            continue
        if _ext[1] == ".pyc":
            pyc_files.append(fn)

    for fn in pyc_files:
        os.remove(os.path.join(p_local,fn))

def delete_pycache_dir(p_local):
    ''' deletes the __pycache__ directory in p_local directory '''
    local_files =  os.listdir(p_local)

    if "__pycache__" in local_files:
        if os.path.isdir(os.path.join(p_local,"__pycache__")):
            shutil.rmtree(os.path.join(p_local,"__pycache__"))

def reset_pytest():

    p_root = find_app_path_root(__file__)

    p_src = os.path.join(p_root,"basic_engine", "src")
    p_tools = os.path.join(p_root,"basic_engine", "tools")
    p_tests = os.path.join(p_root,"basic_engine", "tests")

    delete_pyc_files(p_src)
    delete_pycache_dir(p_src)

    delete_pyc_files(p_tools)
    delete_pycache_dir(p_tools)

    delete_pyc_files(p_tests)
    delete_pycache_dir(p_tests)

if __name__ == "__main__":
    reset_pytest()