from main import Game
from utils import printout_to_data
from datatypes import moveHolder
Move = moveHolder()

def test_filter_forward_diagonal_1():
    
    """This is looking at MOVE_TYPE['forward-diagonal'] used in Mirror.
        It looks to see that optimzed_check_filter views non-pawn pieces
        which attack by diagonal are viewed the same from "in front" and "behind".
        """
    
    s_test = """
    A  B ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(king_in_check_test_copy_apply_4 = False
                                ,king_in_check_on = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    ret_data_opt = game.play(king_in_check_test_copy_apply_4 = True
                                ,king_in_check_on = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert not(Move(pos0=(2, 2), pos1=(1, 1), code=0) in opt_check_moves)

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ B ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(king_in_check_test_copy_apply_4 = False
                                ,king_in_check_on = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    ret_data_opt = game.play(king_in_check_test_copy_apply_4 = True
                                ,king_in_check_on = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert not(Move(pos0=(2, 2), pos1=(3, 3), code=0) in opt_check_moves)

def test_filter_forward_diagonal_2():
    
    """This continues tests for forward-diagonal when right next to the piece.
        Also it tests the idea of moving king to capture and eliminate an
        unprotected opponent piece. Can opt do this?
        """
        

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ B ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ ~ ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(king_in_check_test_copy_apply_4 = False
                                ,king_in_check_on = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    ret_data_opt = game.play(king_in_check_test_copy_apply_4 = True
                                ,king_in_check_on = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(2, 2), pos1=(1, 1), code=0) in opt_check_moves

    s_test = """
    A  ~ ~ ~ ~ ~ ~ ~ ~
    B  ~ ~ ~ ~ ~ ~ ~ ~
    C  ~ ~ k ~ ~ ~ ~ ~
    D  ~ ~ ~ B ~ ~ ~ ~
    E  ~ ~ ~ ~ ~ ~ ~ ~
    F  ~ ~ ~ ~ ~ ~ ~ ~
    G  ~ ~ ~ ~ ~ ~ ~ ~
    H  ~ ~ ~ ~ ~ ~ ~ ~
    """    

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = copy.deepcopy(board.data_by_player)
                ,init_pieces = copy.deepcopy(pieces)
                ,init_player = False     
                ,test_exit_moves = 1    
                )

    ret_data_generic = game.play(king_in_check_test_copy_apply_4 = False
                                ,king_in_check_on = True
                                )
    generic_check_moves = ret_data_generic['moves']

    game.reset_test()
    ret_data_opt = game.play(king_in_check_test_copy_apply_4 = True
                                ,king_in_check_on = False
                                )
    opt_check_moves = ret_data_opt['moves']

    print generic_check_moves
    print opt_check_moves

    assert opt_check_moves == generic_check_moves

    assert Move(pos0=(2, 2), pos1=(3, 3), code=0) in opt_check_moves

def test_filter_check_pinned_piece_1():
    
    #dont let white-knight at (5,2) move; it's pinned to king.

    s_test = """    
       1 2 3 4 5 6 7 8
    A  r ~ b q k ~ ~ r
    B  p p p p ~ p p p
    C  ~ ~ n ~ ~ n ~ ~
    D  ~ ~ ~ ~ p ~ ~ ~
    E  ~ b B ~ P ~ ~ ~
    F  ~ ~ N P ~ ~ ~ ~
    G  P P P ~ ~ P P P
    H  R ~ B Q K ~ N R
    """

    board, pieces = printout_to_data(s_test)

    game = Game(init_board = board.data_by_player
                ,init_pieces = pieces
                ,init_player = True
                ,test_exit_moves = 1    
                )

    # ret = game.play(king_in_check_on=True)
    ret = game.play(king_in_check_on=False)
    moves = ret['moves']

    assert not(Move(pos0=(5, 2), pos1=(6, 4), code=0) in moves)