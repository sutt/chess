from collections import namedtuple

def moveHolder():
    return namedtuple('MoveHolder', 'pos0 pos1 code')

def moveAHolder():
    return namedtuple('MoveAHolder', 'pos1 code')

