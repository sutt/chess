import os
import json
import time
from utils import find_app_path_root
from GameLog import GameSchema

def pgn_to_xpgn(pgn_fn
                ,xpgn_fn
                ,pgn_path = '../data/'
                ,xpgn_path = '../data/'
                ,b_silent = False
                ,max_lines = None
                ):
    
    """

    .pgn -> .xpgn { meta-data:
                    {
                        parse-time
                    }
                    data:
                        [
                            { source-id, GameSchema-json {} }
                            { source-id, GameSchema-json {} }
                            ...
                        ]
                    }

    """

    game_schemas = []
    source_keys = []
    
    with open(pgn_path + pgn_fn, 'r') as f:
        lines = f.readlines()

    if max_lines is not None:
        lines = lines[:max_lines]

    #Load data from .pgn
    for i, line in enumerate(lines):
        
        if line[:2] != '1.':
            continue

        #Found an instruction line   
        instr_ind = i
        game_schema = GameSchema()
        game_schema.set_pgn_instructions(line)

        #Find Results line
        try:
            b_result_found = False
            result_ind = i - 2
            result_line = lines[result_ind]
            s_find_result = '[Result'
            if result_line[:len(s_find_result)] == s_find_result:
                quote_inds = [_i for _i,s in enumerate(result_line) if s == '"']
                if len(quote_inds) == 2:
                    b_result_found = True
            
            if b_result_found:
                s_outcome = result_line[quote_inds[0] + 1: quote_inds[1]]
                game_schema.set_pgn_s_outcome(s_outcome)
        except:
            pass

        #Apply ETL on the game_schema, implemented within that class
        game_schema.all_parse_pgn_instructions()
        
        #Load the game_schema into the list
        game_schemas.append(game_schema)

        #Build a source key to identify duplicates
        source_key = pgn_fn + "-" + str(i)
        source_keys.append(source_key)


    #Build up full array of data
    data_list = []
    
    assert len(source_keys) == len(game_schemas)

    for i, gameSchema in enumerate(game_schemas):
            
        data_elem = {}

        data_elem['source-key'] = source_keys[i]
        
        game_schema_dict = json.loads(gameSchema.to_json())
        data_elem['game-schema'] = game_schema_dict
        
        data_list.append(data_elem)

    
    #Top Level Hierachy for xpgn.json
    xpgn_dict = {}

    xpgn_dict['data'] = data_list

    #meta data for parsing here, e.g. commit version
    xpgn_meta = {}
    xpgn_meta['parse-time'] = str(time.time())
    xpgn_dict['meta-data'] = xpgn_meta


    #Writeout
    if not(b_silent):
        with open(xpgn_path + xpgn_fn, 'w') as f:
            json.dump(xpgn_dict, f)

    
    #Return for non filesystem testing
    if b_silent:
        return xpgn_dict

    return None


PATH_TO_DATA = os.path.join(find_app_path_root(__file__), 'basic_engine', 'data')


def test_pgn_to_xpgn_1():
    
    '''verify the output xpgn creation tool'''
    
    #path changed so pytest is called froom root
    
    s_json = pgn_to_xpgn(pgn_fn = 'GarryKasparov.pgn'
                            ,xpgn_fn = 'output1.xpgn'
                            ,pgn_path = os.path.join(PATH_TO_DATA, '')
                            ,xpgn_path = os.path.join(PATH_TO_DATA, '')
                            ,max_lines = 100
                            ,b_silent = True)

    assert s_json.has_key('data')

    assert s_json['data'][0].has_key('source-key')
    
    assert len(s_json['data']) == 6


def test_pgn_to_xpgn_2():
    
    '''Verify file-system transaction here '''

    # test_dir = '../data/tests/' #if run from src/
    test_dir = os.path.join(PATH_TO_DATA, 'tests', '')

    target_fn = 'test_dummy_1.xpgn'
    
    fns_before = os.listdir(test_dir)
    
    if target_fn in fns_before:
        print 'first removing file...' + str(target_fn)
        os.remove(test_dir + target_fn)
        assert not(target_fn in os.listdir(test_dir))
    
    ret = pgn_to_xpgn( pgn_fn = 'test_pgn_1.pgn'
                        ,xpgn_fn = target_fn
                        ,pgn_path = test_dir     
                        ,xpgn_path = test_dir                            
                        ,max_lines = 100
                        )

    #Test it got created
    assert target_fn in os.listdir(test_dir)

    #Test the output makes some sense in it
    with open(test_dir + target_fn, 'r') as f:
        lines = f.readlines()

    xpgn_json = json.loads(lines[0])

    assert xpgn_json.has_key('data')

    assert len(xpgn_json['data']) > 0
    