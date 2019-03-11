import os, sys

print('-----------------')
print('__name__:', __name__)
print('__package__:', __package__)
print('-----------------')
print("\n".join([str(x) for x in sys.path]))
print('-----------------')

def hello():
    print('hello')
    # print 'hello'
    return 1

def hello2():
    return None