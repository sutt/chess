import sqlite3
import os
import json
from schema_module import TimeAnalysisSchema


DATA_DIR = "../data/perf/perf_db.db"
ERR_CODE = -1


class DBErrLog:
    
    ''' used to track db operation failures without printing to console '''
    
    def __init__(self, verbose=False):
        self.msgList = []
        self.verbose = verbose

    def addMsg(self
                ,method_name=None
                ,method_args=None
                ,method_kwargs=None
                ,exception_class=None
                ):
        ''' add a dict of info about the exception thrown '''
        msgDict = {}
        msgDict['method_name'] = method_name
        msgDict['method_args'] = method_args
        msgDict['method_kwargs'] = method_kwargs
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
                            ,method_kwargs = kwargs
                            ,exception_class = e
                            )
                
                if self.verbose:
                    print 'failure: ', str(method_name)
                
            return result
        return call


#Instantiate now, and pass into DBDriver
# Note: handling this at module level means only one DBErrLog will be created,
#       while multiple intances of DBDriver may be created in modules
#       where it is imported, e.g. inside perf_test

errLog = DBErrLog()
tryWrap = errLog.tryWrap


class DBDriver:

    ''' A generic db class for inheritance into task-specific-db class'''
    
    def __init__(self, data_dir=DATA_DIR, **kwargs):

        self.conn = None
        self.c = None

        self.errLog = errLog
        self.errLog.resetMsgList()
        
        @tryWrap
        def initConnect():
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


#Task specific DB classes ---------------------------------------------

POPULATE_GAMES_DATA_DIR = "../data/"
POPULATE_GAMES_DATA_FN = "GarryKasparovGames.txt"

class TasPerfDB(DBDriver):

    def __init__(self, data_dir=DATA_DIR, populate=False):

        DBDriver.__init__(self, data_dir = data_dir)

        @tryWrap
        def initCreateTas():
            s = """CREATE TABLE tas_table
                    (id text, analysis_type text, algo_style text, tas text)"""
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

        @tryWrap
        def initCreateGamesTable():
            s = """CREATE TABLE games (game_id text, game_instructions text)"""
            self.c.execute(s)
            self.conn.commit()
        initCreateGamesTable()

        self.verifyTable("games")

        @tryWrap
        def initPopulateGamesTable():
            
            s = "SELECT * FROM games"
            self.c.execute(s)
            if len(self.c.fetchall()) > 1:
                print str(self.conn)
                print 'already populated'
                return
            
            print 'Populating games table:'
            fn = POPULATE_GAMES_DATA_DIR + POPULATE_GAMES_DATA_FN
            with open(fn,'r') as f:
                instructions = f.readlines()
            game_records = [ (
                                POPULATE_GAMES_DATA_FN + "-" + str(i+1)
                                ,instructions[i]
                             )
                             for i in range(len(instructions))
                            ]

            # print game_records[:3]
            
            self.insert_many_games(game_records)

            self.conn.commit()
            
            s = "SELECT * FROM games"
            self.c.execute(s)
            rows = self.c.fetchall()
            numRows = len(rows)
            if numRows < 1:
                print 'failed to load!'
                errLog = self.getErrLog()
                print 'ErrLog length: ', str(len(errLog))
                # print 'first seven errors: '
                # print errLog[:min(len(errLog), 7)]
            else:
                print 'Num Rows in game table: ', str(numRows)
                print 'First 3 rows...'
                print rows[:3]

        if populate:
            print 'starting populate'
            initPopulateGamesTable()
            
            
            
    @tryWrap
    def insert_many_games(self, game_records):
        s = """INSERT INTO games(game_id, game_instructions) VALUES(?,?)"""
        self.c.executemany(s, game_records)
        self.conn.commit()
        

    @tryWrap
    def drop_table_basic_tas(self):
        self.c.execute("drop table basic_tas")
        self.conn.commit()
        return 0

    @tryWrap
    def drop_table_tas_table(self):
        pass

    @tryWrap
    def build_games_table(self, games_fn):
        ''' take a pgn file and create a table with an id and insturctions '''
        pass

    @tryWrap
    def update_tas_record(self, tas_id, trials_data):
        ''' update instead of insert '''
        pass

    @tryWrap
    def add_tas_record(self, tas, tas_id = "DUMMY"):
        
        tas_tuple = (tas_id, tas['log'], tas['meta_analysis'], tas['trials'])
        s = "INSERT INTO tas_table VALUES (?,?,?,?)"
        self.c.execute(s, tas_tuple)
        self.conn.commit()

    @tryWrap
    def add_tas_record(self, id, tas, b_basic=False):
        
        if b_basic:
            tas_tuple = (id, tas.to_json(data_dir=None))
            s = "INSERT INTO basic_tas VALUES (?,?)"
        
        else:
            _analysis_type = tas.get_all()['meta_analysis']['analysis_type']    
            _algo_style = tas.get_all()['meta_analysis']['algo_style']    
            
            tas_tuple = (id, _analysis_type, _algo_style, tas.to_json(data_dir=None))
            s = "INSERT INTO tas_table VALUES (?,?,?,?)"

        self.c.execute(s, tas_tuple)
        self.conn.commit()

    @tryWrap
    def update_tas_record(self, id, tas, b_basic=False):
        
        if b_basic:
            tas_tuple = (tas.to_json(data_dir=None), id)
            s = "update basic_tas set tas=? where id=?"
        
        else:
            _analysis_type = tas.get_all()['meta_analysis']['analysis_type']    
            _algo_style = tas.get_all()['meta_analysis']['algo_style']    
            
            
            tas_tuple = (tas.to_json(data_dir=None), id, _analysis_type, _algo_style)
            s = """update tas_table set tas=? where id=? 
                    and analysis_type=? and algo_style=?"""

        self.c.execute(s, tas_tuple)
        self.conn.commit()

    @tryWrap
    def check_for_tas_record(self, game_id, analysis_type=None, algo_style=None
                            ,b_basic=False):
        ''' returns true if record exists in basic_tas tbl '''
        if b_basic:
            self.c.execute("select id from basic_tas where id=?", (game_id,))
        else:
            self.c.execute("""select id from tas_table 
                                where id=? and analysis_type=? and algo_style=?"""
                            ,(game_id, analysis_type, algo_style)
                            )
        return len(self.c.fetchall()) == 1

    @tryWrap
    def get_tas_from_tbl(self, game_id, analysis_type=None, algo_style=None
                        ,b_basic=False):
        ''' returns true if record exists in basic_tas tbl '''
        
        if b_basic:
            self.c.execute("select tas from basic_tas where id=?", (game_id,))
        
        else:
            tas_tuple = (game_id, analysis_type, algo_style,)
            self.c.execute("""SELECT tas from tas_table where id=?
                                and analysis_type=? and algo_style=? """
                            ,tas_tuple)

        fetched = self.c.fetchall()
        tas = TimeAnalysisSchema()
        tas.from_json(path_fn=None, s_json=fetched[0][0])
        return tas

    @tryWrap
    def get_instructions_from_games(self, game_id):
        ''' return game_instructions from games tbl '''
        self.c.execute("select game_instructions from games where game_id=?", (game_id,))
        return self.c.fetchall()[0][0]  #first row, first elem of tuple

    @tryWrap
    def select_all_tas(self):
        s = "select * from tas_table"
        self.c.execute(s)
        ret = self.c.fetchall()

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

    @tryWrap
    def select_all_basic(self):
        s = "select * from basic_tas"
        self.c.execute(s)
        return self.c.fetchall()



if __name__ == "__main__":
    pass
    

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


def test_different_errlogs_respectively_1():
    ''' if you create 2 db drivers, then do you have different errLogs?'''
    
    db = DBDriver(data_dir="../data/perf/mock_db.db")
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    assert len(db.getErrLog()) == 2

    db = DBDriver(data_dir="../data/perf/mock_db.db")
    db.execStr("select * from BAD_TABLE", b_fetch=True)
    
    assert len(db.getErrLog()) == 1


def test_errlog_msg_1():
    ''' Build a DB class that inherits DBDriver, like TasPerfDB, check msgList '''
    
    class MockDB(DBDriver):
        def __init__(self, data_dir):
            DBDriver.__init__(self, data_dir)
        @tryWrap
        def good_calc(self):
            return 1
        @tryWrap
        def bad_calc(self):
            return (1/0)

    db = MockDB("../data/perf/mock_db.db")
    assert len(db.getErrLog()) == 0
    db.good_calc()
    assert len(db.getErrLog()) == 0
    db.bad_calc()
    assert len(db.getErrLog()) == 1
    


def test_errlog_msg_2():
    ''' verify args and function name are present in in errLog.'''
    
    db = DBDriver(data_dir="../data/perf/mock_db.db")

    db.execStr("select * from BAD_TABLE")
    errLog = db.getErrLog()

    e1 = errLog[0]
    assert e1['method_name'] == "execStr"
    assert e1['method_args'][1] == "select * from BAD_TABLE"
    assert e1['method_kwargs'] == {}
    assert e1['exception_msg'] == 'no such table: BAD_TABLE'



def test_errlog_msg_3():
    ''' verify args and function name are present in in errLog.'''
    
    db = TasPerfDB()

    _tas = TimeAnalysisSchema()
    
    db.add_tas_record(id=(1,1), tas=_tas, b_basic=True)    #Tas id not a tuple, should break

    errLog = db.getErrLog()

    badOperationItem = None
    for errItem in errLog:
        if errItem.get('method_name', None) == 'add_tas_record':
            badOperationItem = errItem
            break
    
    assert badOperationItem is not None
    
    assert badOperationItem['exception_msg'] == 'Error binding parameter 0 - probably unsupported type.'

    assert badOperationItem['method_kwargs']['id'] == (1, 1)
    assert badOperationItem['method_kwargs']['b_basic'] == True


def test_execmany_1():
    ''' what happens when one of the many executemany() ops fails? 
        in an insert? in a select? '''
    db = DBDriver(data_dir="../data/perf/mock_db.db")
    db.execStr("drop table mocktbl")
    db.execStr("create table mocktbl (id int, s str)")
    vals = [(1,"a"),(2,"b")]
    db.c.executemany("insert into mocktbl(id, s) values(?,?)", vals)
    db.conn.commit()
    fetched = db.execStr("select * from mocktbl", b_fetch=True)
    assert len(fetched) == 2
    assert fetched[1][1] == "b"


def test_populate_games_table_1():
    
    db = TasPerfDB(data_dir = "../data/perf/mock_db.db", populate=False)
    db.execStr("drop table games")
    
    fetched = db.execStr("select * from games", b_fetch=True)
    assert fetched == -1
    
    db = TasPerfDB(data_dir = "../data/perf/mock_db.db", populate=True)

    fetched = db.execStr("select * from games", b_fetch=True)
    assert len(fetched) > 1

def test_non_basic_tas_1():
    ''' using b_basic=False'''
    db = TasPerfDB(data_dir="../data/perf/mock_db.db")
    db.c.execute('delete from tas_table where id = "dummy"')
    db.conn.commit()
    tas0 = TimeAnalysisSchema()
    with open('../data/perf/demo.tas', 'r') as f:
        lines = f.readlines()
    tas_json = lines[0]
    tas0.from_json(path_fn=None, s_json=tas_json)
    db.add_tas_record("dummy", tas0, b_basic=False)
    db.c.execute('select * from tas_table where id = "dummy"')
    ret = db.c.fetchall()
    db.closeConn()
    assert len(ret) == 1
    

def test_err_execmany_1():
    ''' what happens when one of the many executemany() ops fails? 
        in an insert? in a select? '''
    pass


if __name__ == "__main__":
    # test_errlog_msg_2()
    pass