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

b_player_control = [True,True]



def print_board_letters(board, pieces, b_lower_black = False):

    board.start_annotate()
    for p in pieces:
        board.mark_annotate(p, disambiguate = True, b_lower_case = b_lower_black)
    board.print_board(b_annotate = True, b_show_grid = True)

def main():

    board = Board()
    board, pieces = place_pieces(board)

    game_going = True
    i_turn = 0
    log = Log()
    dead_pieces = []

    print_board_letters(board, pieces, True)

    while(game_going):
        
        i_turn += 1

        for _player in (True,False):
            
            #Find all available moves
            moves_player = []
            for p in pieces:
                if p.white == _player:
                    
                    moves_p = p.get_available_moves(board, move_type_flag = True)
                    moves_p = filter(lambda _m: len(_m) > 0, moves_p)
                    
                    current_pos = p.pos
                    d_moves_p = [(current_pos,_move[0],_move[1]) for _move in moves_p]
                    
                    moves_player.extend(d_moves_p)

            #TODO - Filter moves for king in check
            
            if log.all_moves: print moves_player

            #Check for end-game conditions
            num_moves = len(moves_player)
            if  num_moves == 0:
                game_going = False
                print 'Player ', str(board.player_name_from_bool(_player)), ' has no moves available. Game over.'
                #TODO - add checkmate detector
                continue
            else:
                if log.num_moves:
                    print "Player: ", str(_player), " has num moves: ", str(num_moves)

            #Select the Move
            if not(b_player_control[1 - int(_player)]):
                move_i = random.sample(range(0,num_moves),1)[0]
                the_move = moves_player[move_i][0:2]
                the_move_code = moves_player[move_i][2]
            else:
                the_move, the_move_code = player_control_input(board, moves_player)

            b_enpassant, b_castling = False, False
            if the_move_code == MOVE_CODE['en_passant']: b_enpassant = True
            if the_move_code == MOVE_CODE['castling']: b_castling = True
                        
            #TODO - check for castling_flag here, else do below

            pos0,pos1 = the_move[0], the_move[1]
            piece_i = filter(lambda _p: _p[1].pos == pos0, enumerate(pieces))[0][0]
            
            log.moves_log.append(the_move)
            
            # Unnec
            kill_flag = False
            if board.data_by_player[pos1[0]][pos1[1]] != 0 or b_enpassant:
                kill_flag = True
            
            board.old_player_pos(pos0)

            board.clear_enpassant_vulnerability(_player)

            b_two_advances = two_advances(pos0,pos1)
            board.new_player_pos(_player, pos1, pieces[piece_i], b_two_advances)
            pieces[piece_i].pos = pos1
            pieces[piece_i].modify_castling_property()


            if kill_flag:
                kill_pos = pos1 if not(b_enpassant) else en_passant_pos(pos1, _player)
                
                killed_piece_i = filter(lambda _p: (_p[1].pos == kill_pos) and 
                                                    not(_p[1].white == _player)
                                        ,enumerate(pieces))
                killed_piece_i = killed_piece_i[0][0]
                pieces[killed_piece_i].alive = False
                dead_pieces.append(pieces.pop(killed_piece_i))
                if log.kill_move:
                    print dead_pieces

            #TODO - any promotions here

            if log.move_info:
                print 'Move from: ', str(pos0), " to ", str(pos1)

            #Does this modify Castling or EnPassant Game-Ledger?


            if log.board_end_turn:
                print_board_letters(board, pieces, True)
            
            if kill_flag and log.stop_kill_move:
                input('the kill has happend...')
            if log.proc: print 'new player...'

        print 'new turn...'

        if i_turn == 15:
            break




    # ret = raw_input("What's your message?\n")
    # print str(ret)
    # print "done."

if __name__ == "__main__":
    main()