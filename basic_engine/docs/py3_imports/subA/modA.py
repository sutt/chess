import sys
from .modB import hello

print('-----------------')
try:
    from modB import hello2
    print('import in modA (of modB) succeeds, as expected in py2')
except Exception as e:
    print('the import in modA (of modB) failed, as expected in py3')
    print(e)
print('-----------------')

print('-----------------')
print('__name__:', __name__)
print('__package__:', __package__)
print('-----------------')
print("\n".join([str(x) for x in sys.path]))
print('-----------------')

def foo2():
    hello()
    return None