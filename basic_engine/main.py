import sys, random, time
from basic import *
from utils import *

class Log:
    def __init__(self,**kwargs):
        self.proc = False
        self.all_moves = False
        self.num_moves = False
        self.move_info = False
        self.board_end_turn = True
        self.kill_move = True
        self.stop_kill_move = False
        self.moves_log = []

b_player_control = [True,False]

def parse_player_input(raw, board, input_type = 'alphanum'):
    ret = -1
    if raw == "hint":
        return 1, []
    try:
        if input_type == 'numeric':
            data = raw.split('|')
            data = [x.split(',') for x in data]
            data = [tuple(map(int,item)) for item in data]
            data = tuple(data)
            if len(data) == 2 and \
            len(data[0]) == 2 and len(data[0]) == 2 and \
            all([ isinstance(data[i][j], int) for i in range(2) for j in range(2)]):
                ret = 0
            else:
                print 'failed to validate properties of move parse output'
        elif input_type == 'alphanum':
            print 'here'
            out = alphamove_to_posmove(raw)
            if out == -1:
                return -1,[]
            else:
                ret = 0
                data = out
    except:
        data = []
        print 'failure in routine to parse user input.'
    return ret, data

def print_board_letters(board, pieces, b_lower_black = False):

    board.start_annotate()
    for p in pieces:
        board.mark_annotate(p, disambiguate = True, b_lower_case = b_lower_black)
    board.print_board(b_annotate = True, b_show_grid = True)

def main():

    board = Board()
    board, pieces = place_pieces(board)
    print_board_letters(board, pieces, True)

    game_going = True
    i_turn = 0
    log = Log()
    dead_pieces = []

    while(game_going):
        
        i_turn += 1

        for _player in (True,False):
            
            #Find all available moves
            moves_player = []
            for p in pieces:
                if p.white == _player:
                    
                    moves_p = p.get_available_moves(board)
                    moves_p = filter(lambda _m: len(_m) > 0, moves_p)
                    
                    current_pos = p.pos
                    d_moves_p = [(current_pos,_move) for _move in moves_p]
                    
                    moves_player.extend(d_moves_p)

            if log.all_moves: print moves_player

            #Check for end-game conditions
            num_moves = len(moves_player)
            if  num_moves == 0:
                game_going = False
                continue
            else:
                if log.num_moves:
                    print "Player: ", str(_player), " has num moves: ", str(num_moves)

            #Select the Move
            if not(b_player_control[1 - int(_player)]):
                move_i = random.sample(range(0,num_moves),1)[0]
                the_move = moves_player[move_i]
            else:
                #Input control from console
                msg = "Type your move, " + str(board.player_name_from_bool(_player))
                msg += ". Or type 'hint' to see list of all available moves."
                msg += "\n"
                while(True):
                    raw = raw_input(msg)    #example: >1,1 | 2,2
                    ret, the_move = parse_player_input(raw, board)
                    if ret == 0:
                        if the_move in moves_player:
                            break
                        else:
                            print 'this move is not legal according to the game engine.'
                    if ret == 1: 
                        print moves_player
                    if ret == -1:
                        print 'could not recognize move ', str(raw), ". Try again:"
                        

            pos0,pos1 = the_move[0], the_move[1]
            piece_i = filter(lambda _p: _p[1].pos == pos0, enumerate(pieces))[0][0]
            
            log.moves_log.append(the_move)
            
            #Make the Move
            if board.data_by_player[pos1[0]][pos1[1]] != 0 and log.stop_kill_move:
                print board.player_name_from_bool(_player), ' KILL FROM: \n'
                print str(pos0), " to ", str(pos1)
                ret = input("about to kill...\n")
            

            #is it a killing move?
            kill_flag = False
            if board.data_by_player[pos1[0]][pos1[1]] != 0:
                kill_flag = True
            
            #old position removed from board
            board.old_player_pos(pos0)

            #new posistion set on board in on moving_piece's pos prop
            board.new_player_pos(_player,pos1)
            pieces[piece_i].pos = pos1

            
            if kill_flag:
                killed_piece_i = filter(lambda _p: (_p[1].pos == pos1) and 
                                                    not(_p[1].white == _player), 
                                        enumerate(pieces))
                killed_piece_i = killed_piece_i[0][0]
                pieces[killed_piece_i].alive = False
                dead_pieces.append(pieces.pop(killed_piece_i))
                if log.kill_move:
                    print dead_pieces


            if log.move_info:
                print 'Move from: ', str(pos0), " to ", str(pos1)

            #Does this modify Castling or EnPassant Game-Ledger?
            
            #Check_for_checkmate()

            if log.board_end_turn:
                print_board_letters(board, pieces, True)
            
            if kill_flag and log.stop_kill_move:
                input('the kill has happend...')
            if log.proc: print 'new player...'

            

        print 'new turn...'
        # input("end turn")

        if i_turn == 15:
            break




    # ret = raw_input("What's your message?\n")
    # print str(ret)
    # print "done."

if __name__ == "__main__":
    main()