import sys, json, pprint, copy
from time import time

sys.path.append('../')
from src.main import Game


class TimeAnalysisSchema:
    '''
    Games - a list of instructions: [ "1. c4...", "1. e4...", ...]
    for each game: {
                  
                  meta_analysis: {
                      // these hold must be held constant for different trials to make sense
                      'algo_style':     : 'baseline_yk'
                      'analysis_type'   : 'analysis2'   //by turn times 
                        }
                  
                  log: {
                       // these are "X" in regression
                      'num_avaialble' : [20,22,26,...,0]
                      'king_moves'    : [0,0,2,...,0]    
                          ...
                      }
                  
                  trials: [
                  
                    [trial]: {  //unnamed as the dict is simply an element in a list
                        
                        trial_meta: {
                            // these are used to aggregate separate runs
                            'N'             : 250        //number of trials run and aggregated
                            'data-time-run' : 2018-6-13-13-12-22-345  //runs strated here
                            }

                        trial_data: {
                            // this is "Y" in regression
                            avg-turn-time: [0.028, 0.031, 0.051, ..., 0.288]  //index by turn-num
                            }
                          }
                    , trial: {...}
                    , trial: {...}
                    ,...
                    ]
                  }
    '''
    
    def __init__(self):
        
        self.log = None
        
        self.meta_analysis = None
        self.algo_style = None
        self.analysis_type = None

        self.trials = []

        self.trial = None
        
        self.trial_meta = None
        self.N = None
        self.date_time_run = None

        self.trial_data = None

    
    def get_all(self):
        
        temp = {}
        temp['log'] = self.log
        temp['meta_analysis'] = self.meta_analysis
        temp['trials'] = copy.deepcopy(self.trials)
        
        return copy.deepcopy(temp)

    def set_meta_analysis(self, algo_style, analysis_type):
        
        self.algo_style = algo_style
        self.analysis_type = analysis_type

        self.meta_analysis = {}
        self.meta_analysis['algo_style'] = self.algo_style
        self.meta_analysis['analysis_type'] = self.analysis_type
        

    def set_trial_meta(self, N, **kwargs):
        
        self.N = N
        self.date_time_run = time()
        
        self.trial_meta = {}
        self.trial_meta['N'] = self.N
        self.trial_meta['data_time_run'] = self.date_time_run

    def set_log(self, log_data):
        self.log = copy.deepcopy(log_data)

    @staticmethod
    def aggregate_y(data):
        ''' average each i-th element together'''
        try:
            assert len(data) > 1
            len0  = len(data[0])
            assert all(map(lambda data_i: len(data_i) == len0, data))
        except AssertionError:
            print 'data fed to aggregate_y is of different length; cant aggregate that.'
            return None
        try:
            temp = []
            n = len(data)
            j = len(data[0])
            for _j in range(j):
                sum_elems = sum(map(lambda d: d[_j], data))
                avg_elems = float(sum_elems) / float(n)
                temp.append(avg_elems)
            return temp
        except:
            print 'failed to aggregate, but did not catch in exception'
            return None

    @staticmethod
    def weighted_avg(list_n, list_list_y):
        
        num_elems = len(list_n)
        num_turns = len(list_list_y[0])
        total_n = sum(list_n)
        
        cum_sum_y = [0 for j in range(num_turns)]
        
        for i in range(num_elems):
            weighted_y = map(lambda elem: elem * float(list_n[i]), list_list_y[i])
            cum_sum_y = [cum_sum_y[j] + weighted_y[j] for j in range(num_turns)]

        avg_y = [float(cum_sum_y[j]) / float(total_n) for j in range(num_turns)]

        return avg_y

        
    def weighted_avg_trials(self):
        
        list_n = []
        list_list_y = []
        
        for trial in range(len(self.trials)):
            
            list_n.append(trial['trial_meta']['N'])
            list_list_y.append(trial['trial_data'])

        return self.weighted_avg(list_n, list_list_y)


    def set_trial_data(self, analysis_results):
        ''' set results of analysis to temp var: trial_data'''
        self.trial_data = self.aggregate_y(analysis_results['turn_time'])


    def add_trial(self):
        ''' append trial_meta and trial_data onto trials '''
        self.trial = {}
        self.trial['trial_meta'] = self.trial_meta
        self.trial['trial_data'] = self.trial_data

        self.trials.append(self.trial)
        


    def to_json(self, data_dir=None, data_fn=None):
        ''' return json string or write to json file '''
        
        tas = self.get_all()
        
        if data_dir is None:
            return json.dumps(tas)
    
        #write to output
        data_dir = '../data/perf/'
        data_fn = 'demo.tas'
        try:
            with open(data_dir + data_fn, 'w') as f:
                json.dump(tas, f)
        except:
            print 'failed to write file output'
            return None
        print 'wrote output to: ', data_dir, data_fn

    
    def from_json(self, path_fn="../data/perf/demo.tas"):
        ''' load the TAS from json file'''
        try:
            with open(path_fn, "r") as f:
                d_tas = json.load(f)
        except:
            print 'could not load json from: ', str(path_fn)
            return None

        try:
            self.log = d_tas['log']
            self.meta_analysis = d_tas['meta_analysis']
            self.trials = d_tas['trials']

        except:
            print 'could not convert json to TAS'
            return None

        return 0

class TurnAttributeSchema:
        
    def __init__(self):
        self.s_instructions = None
        self.s_pgn_instructions = None
        
        self.num_available = None
        self.num_player_pieces = None

    def load_instructions(self, insturctions, b_pgn=True):
        ''' load the insturctions and note whether they are boolean '''
        if b_pgn:
            self.s_pgn_instructions = insturctions
        else:
            self.s_instructions = insturctions

    def data_from_gamelog(self, gameLog):
        ''' input a gameLog object to extract trun attributes '''
        self.num_available = gameLog.get_log_num_available()
        self.num_player_pieces = gameLog.get_log_num_player_pieces()
        
    
    def create_data(self, **kwargs):
        ''' run a game using instructions and pass the gameLog into'''

        if self.s_instructions is not None:
            game = Game(s_instructions=self.s_instructions
                        ,b_log_full=True)            
        elif self.s_pgn_instructions is not None:
            game = Game(s_pgn_instructions=self.s_pgn_instructions
                        ,b_log_full=True)
        else:
            print 'could not find instructions to run create_data()'
            return None

        game.play()

        self.data_from_gamelog(game.get_gamelog())


    def get_data(self,**kwargs):
        ''' return data asa a dict '''
        data = {}
        
        if self.s_instructions is not None:
            data['s_instructions'] = self.s_instructions
        else:
            data['s_instructions'] = self.s_pgn_instructions

        data['num_available'] = self.num_available
        data['num_player_pieces'] = self.num_player_pieces
        
        return data