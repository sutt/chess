def dummy():
    '''
    sut -> pgn

        (game.i_turn + 1) / 2   -> pgn turn
        A -> 1
        1 -> A

    https://en.wikipedia.org/wiki/Portable_Game_Notation

    Notes
        castling king side: O-O
        castling queen side: O-O-O

        First letter (Capitalized): Piece Class, (ommitted = Pawn)
        [optinal second letter (lower case)]:
        row(letter)column(number)
        Appendix:

            +: checking
            #: checkmating 
            =: promotion [Q / B / N / R]

            ; / {} :comments

    Testing Thoughts
        GarryKasparov only has 25 mates of 1800 games
        Can use + to verify player_in_check

    '''
    pass

#Just the games
if False:
    
    path_fn = 'data/GarryKasparov.pgn'
    f = open(path_fn)
    data = f.readlines()
    f.close()

    print 'lines: ', str(len(data))

    valid = []
    for line in data:
        if line[:3] == '1. ':
            valid.append(line)

    print 'valids: ', str(len(valid))

    path_fn = 'data/GarryKasparovGames.txt'
    f = open(path_fn, 'w')
    f.writelines(valid)
    f.close()

#Read in the Games
if True:
    path_fn = 'data/GarryKasparovGames.txt'
    f = open(path_fn)
    games = f.readlines()
    f.close()

    max_moves = 0
    min_moves = 999
    min_moves_ind = 0
    cntr = 0
    for game in games:
        cntr += 1
        moves = game.split('.')
        if len(moves) > max_moves:
            max_moves = len(moves)
        if len(moves) < min_moves:
            min_moves = len(moves)
            min_moves_ind = cntr

    print 'max_moves: ', max_moves
    print 'min_moves: ', min_moves
    print 'min_moves_ind: ', min_moves_ind

if True:

    #first the appendix
    move_b_check = False
    move_b_mate = False
    move_b_promotion = False

    check_split = move.split('+')
    if len(check_split) == 2:
        move_b_check = True
    
    mate_split = move.split('#')
    if len(mate_split) == 2:
        move_b_mate = True

    mate_split = move.split('#')
    if len(mate_split) == 2:
        move_b_mate = True

    
    #Now, find the 
    i_rev_first_digit = filter(lambda s: str.isdigit(s), move[::-1] ).index(True)
    i_first_digit =  len(move) - i_rev_first_digit

    dest_alphanum = move[i_first_digit - 1:]
