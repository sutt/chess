import sys
from main import Game
from Display import Display
from utils import format_move_log

display = Display()


run_type = "interactive"
if len(sys.argv) > 1:
    run_type = str(sys.argv[1])
print '\nRunning: ', run_type, '\n'

# run_type = 'randomplay2'    #for debugging
# run_type = 'replay'    #for debugging
# run_type = 'manyrandom'    #for debugging

if run_type == "interactive":

    ''' Interactive Mode '''

    game = Game(manual_control = (1,0)
                    ,b_display_show_opponent = True
                    ,b_log_move = True
                    )
    game.play()


elif run_type == "randomplay":
    
    game = Game(manual_control = ()
                ,b_display_never_print = True
                ,b_log_move = False
                ,test_exit_moves = 1000
                )
    
    ret = game.play()
    
    if game.i_turn == 1000:
        print '1000 turn game'
    else:
        
        outcome, board, pieces = ret

        print 'Outcome: ', str(outcome)
        
        display.print_board_letters(pieces)

        log = game.get_gamelog()
        move_log = log.get_log_move()

        print 'Game Turn on exit: ', str(game.i_turn)
        print 'Len of Log Moves:  ', str(len(move_log))

if run_type == '20random':
    
    for t in range(20):
        game = Game(manual_control = ()
                    ,b_display_never_print = True
                    ,b_log_move = False
                    ,test_exit_moves = 1000
                    )
        
        ret = game.play()
        
        if game.i_turn == 1000:
            print '1000 turn game'
        else:
            
            outcome, board, pieces = ret

            print 'Outcome: ', str(outcome)
            
            display.print_board_letters(pieces)

            log = game.get_gamelog()
            move_log = log.get_log_move()

            print 'Game Turn on exit: ', str(game.i_turn)
            print 'Len of Log Moves:  ', str(len(move_log))

if run_type == 'manyrandom':
    
    for t in range(200):
        game = Game(manual_control = ()
                    ,b_display_never_print = True
                    ,b_log_move = False
                    ,test_exit_moves = 1000
                    )
        
        ret = game.play()
        
        if game.i_turn == 1000:
            print '1000 turn game'
        else:
            
            outcome, board, pieces = ret

            print 'Outcome: ', str(outcome)
            
            display.print_board_letters(pieces)

            log = game.get_gamelog()
            move_log = log.get_log_move()

            print 'Game Turn on exit: ', str(game.i_turn)
            print 'Len of Log Moves:  ', str(len(move_log))


elif run_type == "randomplay2":
    
    '''This looks at discrepancy in checkmate'''
    
    game = Game(manual_control = ()
                ,b_log_move = True
                
                )
    
    try:
        outcome, board, pieces = game.play()
    except Exception as e:
        
        #Game Broke, so let's look at the previous move, what happend?
        print 'exception: ', str(e)

        log = game.get_gamelog()
        move_log = log.get_log_move()
        s_instructions_0 = format_move_log(move_log[:-2])
        s_instructions_1 = format_move_log(move_log[:-1])
        s_instructions_2 = format_move_log(move_log)

        if True:
            fn0, fn1, fn2 = "data/fn0.txt", "data/fn1.txt", "data/fn2.txt"
            f = open(fn0, 'w')
            f.write(s_instructions_0)
            f.close()
            f = open(fn1, 'w')
            f.write(s_instructions_1)
            f.close()
            f = open(fn2, 'w')
            f.write(s_instructions_2)
            f.close()

        g0 = Game(s_instructions = s_instructions_0)
        ret0 = g0.play()
        pieces0, board0 = ret0['pieces'], ret0['board']
        
        g1 = Game(s_instructions = s_instructions_1)
        ret1 = g1.play()
        pieces1, board1 = ret1['pieces'], ret1['board']

        g2 = Game(s_instructions = s_instructions_2)
        ret2 = g2.play()
        pieces2, board2 = ret2['pieces'], ret2['board']

        print 'Game 2 moves before break'
        display.print_board_letters(board0, pieces0, True)    
        
        print 'Game 2 moves before break'
        display.print_board_letters(board1, pieces1, True)    
        
        print 'Game 1 move before break'
        display.print_board_letters(board2, pieces2, True)

    #What does end game look like?
    print 'Outcome: ', str(outcome)
    display.print_board_letters(board, pieces, True)
    print "\n".join([str(x) for x in board.data_by_player])

    #Verify checkmate with naive algo
    if False and outcome[2] == 'CHECKMATE':
        
        print 'its a checkmate, so lets cross examine'

        losing_player = outcome[0]

        game2 = Game(manual_control = ()
                     ,init_board = board.data_by_player
                     ,init_pieces = pieces
                     ,init_player = losing_player
                     ,test_exit_moves = 1 )

        ret_moves = game2.play(king_in_check_on = True
                                ,king_in_check_test_copy_4 = False
                                )

        print 'Moves available: ', str(ret_moves['moves'])

    # try:
    #     outcome, board = game.play()
    # except Exception as e:
    #     print 'exception!'
    #     print e

    print 'Outcome: ', str(outcome)

    display.print_board_letters(board, pieces, True)

    log = game.get_gamelog()
    move_log = log.get_log_move()

    print 'Game Turn on exit: ', str(game.i_turn)
    print 'Len of Log Moves:  ', str(len(move_log))

elif run_type == 'replay':

    f = open('data/fn1.txt','r')
    s = f.readlines()
    f.close()
    s = s[0]
    print s

    game = Game(s_instructions = s, test_exit_moves = 64)
    ret = game.play()
    print 'i_turn: ', str(game.i_turn)
    print ret

    # moves = ret['moves']
    # print moves




