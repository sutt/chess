def wrap(pre, post):
    def decorate(func):
        def call(*args, **kwargs):
            pre(func, *args, **kwargs)
            result = func(*args, **kwargs)
            post(func, *args, **kwargs)
            return result
        return call
    return decorate

def trace_in(func, *args, **kwargs):
    print "Entering function",  func.__name__
 
def trace_out(func, *args, **kwargs):
    print "Leaving function", func.__name__
 
@wrap(trace_in, trace_out)
def calc(x, y):
    print 'executing function'
    return x + y

calc(1,2)