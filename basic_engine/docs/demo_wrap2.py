DEFAULT_EXCEPT_RET = -1

class ErrLog:
    
    def __init__(self, verbose=False):
        self.msg = []
        self.verbose = verbose

    def addMsg(self, funcName):
        self.msg.append(funcName)
        if self.verbose:
            print 'FAILURE:', str(funcName)

    def getMsg(self):
        return self.msg

    @classmethod
    def decorate_class(cls,func):
        def call(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except:
                result = DEFAULT_EXCEPT_RET
            return result
        return call

    
    def decorate_regular(self,func):
        ''' an instance method, thus has access 
            to the class's data'''

        def call(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except:
                self.addMsg(func.__name__)      #added
                result = DEFAULT_EXCEPT_RET
            return result
        return call


#Instantiate & Alias
errLog = ErrLog()
decorate_regular = errLog.decorate_regular


#works when decorate() is a classmethod
decorate_class = ErrLog.decorate_class  

 
class MyClass:

    def __init__(self, errLog=None):
        self.z = 1
        self.errLog = errLog
        
    def getErrLog(self):
        return self.errLog

    @decorate_class
    def calc(self,x, y):
        return (x / y)  + self.z

    @decorate_regular
    def calc2(self,x, y):
        return (x / y)  + self.z


print 'using decorate_class:\n'
mc = MyClass()
print mc.calc(1,2)
print mc.calc(1,0)
print mc.calc(1,2)
# these cant log an MyClass-ownde errLog because 
# as classmethod, it doesn't have an instance data

print 'using regular_class:\n'
mc = MyClass(errLog)
print mc.calc2(1,2)
print mc.calc2(1,0)
print mc.calc2(1,2)

print 'Local Variable errLog.msg: '
print str(errLog.getMsg())

print 'MyClass contained reference to local errLog: '
print str(mc.getErrLog().getMsg())