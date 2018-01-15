
#ByRef bug

def _print(data):
    print "\n".join(map(str,data))
    print "\n"

#BAD
data = [[0] * 8] * 8
_print(data) 

data[1][1] = 1  #overrides all column 1
_print(data)

#GOOD
data2 = [[0 for i in range(8)] for j in range(8)]
data2[1][1] = 1
_print(data2)

