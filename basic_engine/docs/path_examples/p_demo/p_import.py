import os

def ppath():
    print __name__ + '\n'
    
    print ' __file__:   %s'    % __file__

    print ' dirname :   %s'     % os.path.dirname(__file__)
    
    print ' cwd     :   %s'     % os.getcwd()
    
    print ' relpath :   %s'     % os.path.relpath(os.path.dirname(__file__))

    print '\n'
    
    # os.path.abspath
    # print 'p_demo.p_import __name__: %s' % __name__
    # print 'p_demo.p_import __package: %s' % __package__


