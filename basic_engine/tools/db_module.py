import sqlite3
import os
import json
from schema_module import TimeAnalysisSchema


DATA_DIR = "../data/perf/db_perf.db"
ERR_CODE = -1


class DBErrLog:
    
    ''' used to track db operation failures without printing to console '''
    
    def __init__(self, verbose=False):
        self.msgList = []
        self.verbose = verbose

    def addMsg(self
                ,method_name=None
                ,method_args=None
                ,exception_class=None
                ):
        ''' add a dict of info about the exception thrown '''
        msgDict = {}
        msgDict['method_name'] = method_name
        msgDict['method_args'] = method_args
        msgDict['exception_msg'] = exception_class.message
        #TODO - stacktrace
        
        self.msgList.append(msgDict)

    def getMsgList(self):
        return self.msgList

    def resetMsgList(self):
        self.msgList = []

    def tryWrap(self, wrappedMethod):
    
        ''' Wrap wrappedMethod in try/except, logs function +  errMsg.
            Used as a decorator to DBDriver methods'''

        def call(*args, **kwargs):
            try:
                result = wrappedMethod(*args, **kwargs)
            
            except Exception as e:
                
                result = ERR_CODE
                
                method_name = wrappedMethod.__name__
                
                self.addMsg( method_name = method_name
                            ,method_args = args
                            ,exception_class = e
                            )
                
                if self.verbose:
                    print 'failure: ', str(method_name)
                
            return result
        return call


#Instantiate now, and pass into DBDriver
errLog = DBErrLog()
tryWrap = errLog.tryWrap


class DBDriver:
    
    def __init__(self, data_dir=DATA_DIR, **kwargs):

        self.conn = None
        self.c = None

        self.errLog = errLog
        self.errLog.resetMsgList()      #From Previous Driver instances
        
        @tryWrap
        def initConnect():
            #TODO - allow different db connectionts
            self.conn = sqlite3.connect(data_dir)
            self.c = self.conn.cursor()
        initConnect()

    
    def getErrLog(self):
        return self.errLog.getMsgList()
    
    @tryWrap
    def verifyTable(self, tbl_name):
        ''' see if tbl_name exists '''
        s = ("SELECT * FROM " + tbl_name)
        self.c.execute(s)
        
    @tryWrap
    def closeConn(self):
        self.c.close()
        self.conn.close()

    @tryWrap
    def execStr(self, s_sql, b_commit=False, b_fetch=False):
        self.c.execute(s_sql)
        if b_commit:
            self.conn.commit()
        if b_fetch:
            return self.c.fetchall()


class TasPerfDB(DBDriver):

    def __init__(self, data_dir=DATA_DIR):

        DBDriver.__init__(self, data_dir = data_dir)

        @tryWrap
        def initCreateTas():
            s = """CREATE TABLE tas_table
                    (id text, log text, meta_analysis text, trials text)"""
            self.c.execute(s)
            self.conn.commit()
        initCreateTas()

        @tryWrap
        def initCreateBasic():
            s = """CREATE TABLE basic_tas (id text, tas text)"""
            self.c.execute(s)
            self.conn.commit()
        initCreateBasic()

        self.verifyTable("tas_table")
        self.verifyTable("basic_tas")


    def drop_table_basic_tas(self):
        self.c.execute("drop table basic_tas")
        self.conn.commit()
        return 0

    def drop_table_tas_table(self):
        pass

    def build_games_table(self, games_fn):
        ''' take a pgn file and create a table with an id and insturctions '''
        pass
    
    def check_for_tas_record(self, tas_id):
        ''' return True if record already exists, False otherwise '''
        pass

    def update_tas_record(self, tas_id, trials_data):
        ''' update instead of insert '''
        pass

    def add_tas_record(self, tas, tas_id = "DUMMY"):
        
        tas_tuple = (tas_id, tas['log'], tas['meta_analysis'], tas['trials'])
        s = "INSERT INTO tas_table VALUES (?,?,?,?)"
        try:
            self.c.execute(s, tas_tuple)
        except:
            print "failed to add_tas_record"
            return -1

        self.conn.commit()
        return 0

    def add_basic_record(self, s_tas, tas_id = "DUMMY"):
        
        tas_tuple = (tas_id, s_tas)
        s = "INSERT INTO basic_tas VALUES (?,?)"
        try:
            self.c.execute(s, tas_tuple)
            self.conn.commit()
        except:
            print "failed to add_basic_record"
            return -1

        return 0

    def update_basic_record(self, id, s_tas):
        
        tas_tuple = (s_tas, id)
        s = "update basic_tas set tas=? where id=?"
        try:
            self.c.execute(s, tas_tuple)
            self.conn.commit()
        except:
            print "failed to add_basic_record"
            return -1

        return 0

    def select_all_tas(self):
        s = "select * from tas_table"
        self.c.execute(s)
        ret = self.c.fetchall()
        print ret

        tas_list = []

        for line in ret:
            tas_temp = TimeAnalysisSchema()
            temp = {}
            temp['log'] = line[1]
            temp['meta_analysis'] = line[2]
            temp['trials'] = line[3]
            tas_temp.from_json(json.dumps(temp))
            tas_list.append(tas_temp)

        return tas_list

    def select_all_basic(self):
        s = "select * from basic_tas"
        self.c.execute(s)
        return self.c.fetchall()



if __name__ == "__main__":
    
    
    db = DBDriver()
    if "db_perf.db" in os.listdir("../data/perf/"):
        print "db is there"
    else:
        print "could not find db"

    dummy_tas = {}
    dummy_tas['log'] = "dummy log"
    dummy_tas['meta_analysis'] = "dummy meta"
    dummy_tas['trials'] = "dummy trials"

    db.add_tas_record(dummy_tas)

    db.check_table("tas_table")

    ret = db.select_all_tas()

    print 'My TAS ENTRY-0:'
    print ret[0].get_all()


    tas = TimeAnalysisSchema()
    tas.from_json("../data/perf/demo.tas")

    print 'GET ALL from Obj:'
    print tas.get_all()

    db.add_basic_record(tas.to_json())

    db.select_all_basic()

#Unit Tests ----------------------------------------------------------

def test_calling_instance_method_in_init():
    ''' Testing Design Pattern: call function below init, in init '''

    class MyClass:
        def __init__(self):
            self.data = 1
            self.data2 = self.bottomFunc(self.data)

        def bottomFunc(self, val):
            return val + 1

    mc = MyClass()
    assert mc.data2 == 2


def test_class_wrapper_1():
    ''' Testing Desgin Pattern: wrapper/decorators within classes '''

    def decorate(func):
        def call(*args, **kwargs):
            try:
                print 'starting calc'
                result = func(*args, **kwargs)
            except:
                print 'failure! ', str( func.__name__ )
                return -1
            return result
        return call
    
    class MyClass:

        def __init__(self):
            self.z = 1

        @decorate
        def calc(self,x, y):
            print 'executing function'
            return (x / y)  + self.z

    mc = MyClass()
    assert mc.calc(1,2) == 1
    assert mc.calc(1,0) == -1
    assert mc.calc(1,2) == 1


def test_inherit_dbdriver_1():
    ''' build a class ontop of generic DBDriver '''
    pass


def test_errlog_msg_1():
    ''' Testing how the errlog '''

    mock_data_dir = "../data/perf/mock_db.db"

    db = DBDriver(data_dir=mock_data_dir)

    #use execStr for some successful and some failure operations
    #...

def test_different_errlogs_respectively_1():
    ''' if you create 2 db drivers, then do you have different errLogs?'''
    
    db = DBDriver(data_dir="../data/perf/mock_db.db")
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    assert len(db.getErrLog()) == 2

    db = DBDriver(data_dir="../data/perf/mock_db.db")
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    print db.getErrLog()
    assert len(db.getErrLog()) == 1

def test_errlog_msg_2():
    ''' Build a DB class that inherits DBDriver, like TasPerfDB, check msgList '''
    pass


def test_err_execmany_1():
    ''' what happens when one of the many executemany() ops fails? 
        in an insert? in a select? '''
    pass

