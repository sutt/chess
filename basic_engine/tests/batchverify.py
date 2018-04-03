import os, sys, time, json, copy, exceptions, types
sys.path.append('../')

from src.main import Game
from src.GameLog import GameSchema

#Must run from inside directory: basic_engine/tests/


#Batch Params for batch-testing here:
#test_batch_xxx_xxx() functions run on pytest; only verify some records
BATCH_SAMPLING_N = 100
BATCH_DATA_SOURCE = '../data/GarryKasparov.xpgn'
BATCH_KICKOUTS_LOG = '../data/tests/batchverify_kickout_log.txt'

#TODO - printout or logout when there are kickouts

#Helper Fucntions -----------------------------------

def load_xpgn_data(fn = BATCH_DATA_SOURCE
                    ,max_tests = BATCH_SAMPLING_N
                    ,exclude_inds = None
                    ):

    '''This loads data for verify() tests'''
    
    with open(fn, 'r') as f:
        lines = f.readlines()

    o_json = json.loads(lines[0])
    data = o_json['data']

    if max_tests is not None:
        data = data[:max_tests]
        #TODO - add sampling not first N

    if exclude_inds is not None:
        #TODO- make this based off source-key so we can sample
        data = [v for i,v in enumerate(data) if not(i in exclude_inds)]

    return data


def build_modulo_print_data(data, modulo_print):
    ''' Build data out of slices of the data. 
        For batch runs which take a long time; print after each section.
    '''

    if modulo_print is None:
        return [data]    

    else:
        assert type(modulo_print) == types.IntType
        try:
            data_modulo = []
            for i in range(len(data) / modulo_print):        
                data_modulo.append(data[i*modulo_print:(i+1)*modulo_print])
            
            data_modulo.append(data[(i+1)*modulo_print:])    #the fractional leftover

        except:
            return None

    return data_modulo


#Main Verify() functions --------------------------------------------

def verify_has_outcome_str(data, b_assert=False):
    '''Verify there is a string in each game-schema element'''
    for i, data_elem in enumerate(data):
        
        s_gameSchema = data_elem['game-schema']
        o_gameSchema = GameSchema()
        o_gameSchema.from_json(s_gameSchema)

        s_outcome = o_gameSchema.get_s_outcome()

        if b_assert:
            assert (s_outcome is not None)
        else:
            if s_outcome is None:
                print i
                print data_elem['source-key']


def manual_batch_has_outcome_str():
    '''Run this verify with printout instead of assert.'''    
    data = load_xpgn_data(max_tests=None)
    verify_has_outcome_str(data, b_assert=False)
    print 'done.'


def test_batch_has_outcome_str():
    '''Run this verify in automated tests.'''
    verify_has_outcome_str(load_xpgn_data(), b_assert=True)
    


def verify_standard_outcome(data, b_assert=False):
    ''' verify only outcomes are: 1-0 , 0-1 , 1/2-1/2 '''
    
    
    for i, data_elem in enumerate(data):
        
        s_gameSchema = data_elem['game-schema']
        o_gameSchema = GameSchema()
        o_gameSchema.from_json(s_gameSchema)

        s_outcome = o_gameSchema.get_s_outcome()

        #Condition
        enum_outcomes = ['1-0','0-1','1/2-1/2']
        b_test = (s_outcome in enum_outcomes)
        
        #Test
        if b_assert:
            assert b_test == True
        else:
            if not(b_test):
                print 'i: ' + str(i) + ' ' + str(data_elem['source-key'])
                print s_outcome


def test_batch_standard_outcome():
    data = load_xpgn_data()
    verify_standard_outcome(data, b_assert=True)

def manual_batch_standard_outcome():
    data = load_xpgn_data(max_tests=None)
    verify_standard_outcome(data, b_assert=True)
    print 'done.'


def verify_last_player_move_at_least_ties(data, b_print=False):

    for i, data_elem in enumerate(data):
        
        try:
            s_gameSchema = data_elem['game-schema']
            o_gameSchema = GameSchema()
            o_gameSchema.from_json(s_gameSchema)

            s_outcome = o_gameSchema.get_s_outcome()

            i_last_player = o_gameSchema.get_player_last_move()

            if i_last_player == 0:  #white
                assert s_outcome != "0-1"
            elif i_last_player == 1:
                assert s_outcome != "1-0"
            else:
                assert False
        
        except AssertionError:
            
            if b_print:
                print i
                print s_gameSchema
            
            return exceptions.AssertionError()

def manual_last_player_move_at_least_ties():
    data = load_xpgn_data(max_tests=None)
    verify_last_player_move_at_least_ties(data, b_print=True)
    print 'done.'

def test_batch_last_player_move_at_least_ties():
    data = load_xpgn_data(exclude_inds = [49])
    verify_last_player_move_at_least_ties(data,b_print=False)
    

def verify_check_schedule_match(data, b_naive_check=False, b_assert=True):
    ''' Compare check each turn in pgn vs own implementation of play().
        Note: play() identify player is in check but pgn identify the 
        player that causes check. So they are off by one.
    '''

    for i, data_elem in enumerate(data):
        
        s_gameSchema = data_elem['game-schema']
        o_gameSchema = GameSchema()
        o_gameSchema.from_json(s_gameSchema)

        s_pgn = o_gameSchema.get_instructions()
        schema_check_schedule = o_gameSchema.get_check_schedule()

        game = Game(s_pgn_instructions=s_pgn
                    ,b_log_check_schedule=True
                    )

        game.play( king_in_check_on = b_naive_check
                    ,king_in_check_test_copy_apply_4 = not(b_naive_check)
                    )

        log_check_schedule = game.get_gamelog().get_log_check_schedule()
        
        b_pass = (log_check_schedule[1:] == schema_check_schedule[:-1])

        if b_assert:
            assert b_pass == True
        else:
            if not(b_pass):
                print str(i) + ' | ' + data_elem['source-key']
    

def test_batch_check_schedule_match():
    
    data = load_xpgn_data(max_tests=20)     #heavy computation, run less
    
    verify_check_schedule_match(data
                                ,b_naive_check=False
                                ,b_assert=True 
                                )

def manual_check_schedule_match(n = None, b_naive_check=False, modulo_print=None):
    
    data = load_xpgn_data(max_tests=n)

    data_modulo = build_modulo_print_data(data, modulo_print=modulo_print)

    for i, data_section in enumerate(data_modulo):
        try:

            print 'Starting Section i: ', str(i)

            verify_check_schedule_match(data_section
                                        ,b_naive_check=False
                                        ,b_assert=False
                                        )        
        except Exception as e:

            if type(e) == exceptions.KeyboardInterrupt:
                print 'BREAKING'
                break
            else:
                print 'exception in data_section_i: ', str(i)

    print 'done.'


    

#Unit-testing for the batch verify functions themselves ------------------

def test_load_xpgn_data():
    
    data = load_xpgn_data(fn = "../data/GarryKasparov.xpgn"
                            ,max_tests=None)
    
    assert len(data) == 1854

    data = load_xpgn_data()
    
    assert len(data) == 100

    data = load_xpgn_data(fn = "../data/GarryKasparov.xpgn"
                            ,max_tests=10
                            ,exclude_inds=[1,2,3])

    assert len(data) == 7


def test_build_modulo_print_data():
    ''' Test this helper function. '''
    data = load_xpgn_data(max_tests = 202)
    data2 = build_modulo_print_data(data, modulo_print=20)

    assert len(data) == 202
    assert len(data2) == 11
    assert len(data2[0]) == 20
    assert len(data2[11 - 1]) == 2


def test_verify_has_outcome_str_true_negative():
    
    '''True Negative: this xpgn has a null for outcome. Do we catch it?'''
    
    data = load_xpgn_data(fn = '../data/tests/test_dummy_1.xpgn'
                        ,max_tests=None)
    
    
    TEST_CASE_IND = 2
    data = [data[TEST_CASE_IND]]    #expecting a list of data_elems

    b_assertion = False
    try:
        verify_has_outcome_str(data, b_assert=True)
    except AssertionError:
        b_assertion = True

    assert b_assertion == True

    #Test this test against a false negative
    data = load_xpgn_data(fn = '../data/tests/test_dummy_1.xpgn'
                        ,max_tests=None)
    
    
    DUMMY_TEST_CASE_IND = 3
    data = [data[DUMMY_TEST_CASE_IND]]    #expecting a list of data_elems

    b_assertion = False
    try:
        verify_has_outcome_str(data, b_assert=True)
    except AssertionError:
        b_assertion = True

    assert b_assertion == False


def test_verify_standard_outcome_true_negative():
    
    '''True Negative: this xpgn has a non-standard string in outcome. Do we catch it?'''
    
    data = load_xpgn_data(fn = '../data/tests/test_dummy_1.xpgn'
                        ,max_tests=None)
    
    TEST_CASE_IND = 3
    data = [data[TEST_CASE_IND]]    #expecting a list of data_elems

    b_assertion = False
    try:
        verify_standard_outcome(data, b_assert=True)
    except AssertionError:
        b_assertion = True

    assert b_assertion == True


def test_verify_last_player_move_at_least_ties_true_negative():

    ''' True Negative: show last player to move losing the game.
        This actually occurs on GarryKasparove game 49 (index-0-based).
    '''

    #Control Case: show it passes first
    data = load_xpgn_data(exclude_inds = [49])
    ret = verify_last_player_move_at_least_ties(data,b_print=False)

    assert not(type(ret) == exceptions.AssertionError)


    #Test Case: the function should return an assertion error
    data = load_xpgn_data(exclude_inds = [15])
    ret = verify_last_player_move_at_least_ties(data,b_print=False)

    assert type(ret) == exceptions.AssertionError