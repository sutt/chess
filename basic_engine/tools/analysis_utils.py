import os, sys, json
from db_module import TasPerfDB
from schema_module import TimeAnalysisSchema

def mic_check():
    print '1,3'


def load_data(gameIds, analysis_type, algo_style):
    
    data = []
    db = TasPerfDB(data_dir="../data/perf/perf_db.db")

    for _gameId in gameIds:

        s_tas =  db.get_tas_from_tbl( _gameId
                                      ,analysis_type
                                      ,algo_style
                                      ,False
                                    )
        data.append([_gameId, s_tas])
    
    db.closeConn()
    return data


def build_data(data_tbl
              ,N = 50
              ):

    data = []
    
    for record in data_tbl:
        
        _gameId = record[0]
        # _tas = json.loads(record[1])
        _tas = record[1].get_all()
        
        for trial in _tas['trials']:
        
            _n = trial['trial_meta']['N']
            
            if _n >= N:
                
                _temp = [
                        _gameId
                        ,_n
                        ,trial['trial_data']
                        ,_tas['log']['num_available']
                        ,_tas['log']['num_player_pieces']
                        ]
                
                data.append(_temp)

    return data

if __name__ == "__main__":
    pass