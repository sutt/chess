from basic import *

def main():

    board = Board()
    board.print_board()
    board, pieces = place_pieces(board)
    board.print_board(b_player_data=True)

if __name__ == "__main__":
    main()