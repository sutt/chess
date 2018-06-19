import sqlite3
import os
import json
from perf_test import TimeAnalysisSchema

DATA_DIR = "../data/perf/db_perf.db"

class DBDriver:

    def check_table(self, table_name):
        try:
            s = "SELECT * FROM "
            s += table_name
            self.c.execute(s)
            ret = self.c.fetchall()
        except:
            print "table ", table_name, "could not be found"
            return None

        print "Table has length: ", str(len(ret))
    
    def __init__(self, **kwargs):

        self.conn = None
        self.c = None
        
        #Initialize --------------------------------
        try:
            self.conn = sqlite3.connect(DATA_DIR)
            print "connected to: ", DATA_DIR
        except:
            print "could not connect to db"
            return -1

        self.c = self.conn.cursor()

        try:
            s = """CREATE TABLE tas_table
                    (id text, log text, meta_analysis text,
                    trials text)"""
            self.c.execute(s)
            self.conn.commit()
        except:
            print "could not create table tas_table"

        try:
            s = """CREATE TABLE basic_tas (id text, tas text)"""
            self.c.execute(s)
            self.conn.commit()
        except:
            print "could not create table basic_tas"

        if kwargs.get('b_check_table', True):
            self.check_table("tas_table")
        
        if kwargs.get('b_check_table', True):
            self.check_table("basic_tas")

        self.conn.commit()

    
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

    def add_basic_record(self, s_tas, id = "DUMMY"):
        
        tas_tuple = (id, s_tas)
        s = "INSERT INTO basic_tas VALUES (?,?)"
        try:
            self.c.execute(s, tas_tuple)
        except:
            print "failed to add_tas_record"
            return -1

        self.conn.commit()
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
        ret = self.c.fetchall()
        print ret



    #SCRATCHPAD

        #CREATE the record for the first time
        
        #Read the record for reporting
            #select * where 

        #Read the record

        #Also we need more characteristics on the game like num_turns, etc...
            #put this in meta_tas_table with left join on id


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

        



