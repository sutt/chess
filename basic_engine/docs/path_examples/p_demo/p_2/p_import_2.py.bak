import os

def find_path():

    here_abs = os.path.abspath(os.path.dirname(__file__))

    _path = here_abs
    print here_abs
    
    for i in range(6):
    # while(True):
    
        try:
            _head, _tail = os.path.split(_path)
            print _tail
            if str.lower(_tail) == str.lower('path_examples'):
                break
            _path = _head

        except:
            print 'exception'
            break

    
    print 'found path: %s' % os.path.abspath(_path)

    p3_path = os.path.join(_path,'p_3')
    p4_path = os.path.join(_path,'p_3', 'p_4')
    print p3_path

    p3_rel = os.path.relpath(p3_path, start = os.getcwd())
    print os.getcwd()
    print p3_rel


    print 'p_3/ contains tmp.txt: %s' % str(os.listdir(p3_path))
    print 'p_3/ contains tmp.txt: %s' % str(os.listdir(p3_rel))

    print 'p_3/p_4/ contains tmp2.txt: %s' % str(os.listdir(p4_path))

if __name__ == "__main__":
    print __file__
    find_path()
        