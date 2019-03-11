import sys

# print(*sys.path, sep="\n")
# sys.path += ['py3_imports/subA']

print('-----------------')
print('__name__:', __name__)
print('__package__:', __package__)
print('-----------------')
print("\n".join([str(x) for x in sys.path]))
print('-----------------')

# this works
from subA.modB import hello
hello()

from subA.modA import foo2
foo2()

# this breaks
print('-----------------')
try:
    import subA.modA.foo2 as foo2
    foo2()
except Exception as e:
    print('the import in main failed as expected in py versions!')
    print(e)