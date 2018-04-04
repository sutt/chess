import copy, sys

#From src/utils -----------------------------

def alphanum_to_pos(inp, b_legacy=True, b_legacy2=True):
    if b_legacy:
        letter_data = 'ABCDEFGH'
        pos0 = letter_data.index(str.upper(inp[0]))
        pos1 = int(inp[1]) - 1
        return (pos0,pos1)
    elif b_legacy2:
        col_letters = 'ABCDEFGH'
        row = int(inp[1]) - 1
        col = col_letters.index(str.upper(inp[0]))
        return (row, col)
    else:
        col_letters = 'ABCDEFGH'
        row = 8 - int(inp[1])                       #update
        col = col_letters.index(str.upper(inp[0]))
        return (row, col)

def pos_to_alphanum(inp, b_legacy=True, b_legacy2=True):
    if b_legacy:
        letter_data = 'abcdefgh'
        number_data = [i+1 for i in range(8)]
        s1 = letter_data[inp[0]]
        s2 = str(number_data[inp[1]])
        return s1 + s2
    elif b_legacy2:
        letter_data = 'abcdefgh'
        number_data = [i+1 for i in range(8)]
        s1 = letter_data[inp[1]]
        s2 = str(number_data[inp[0]])
        return s1 + s2
    else:
        letter_data = 'abcdefgh'
        number_data = [i for i in range(8,0,-1)]    #update
        s1 = letter_data[inp[1]]
        s2 = str(number_data[inp[0]])
        return s1 + s2

#custom funcs -------------------------------------

def is_alphanum_tuple(s):
    if len(s) != 2:
        return False
    if not(s[0].isalpha()):
        return False
    if not(s[1].isdigit()):
        return False
    return True

def convert_string(s_input):

    final_string = ""

    ind = 0
    # for ind in range(0, len(s_input) - 2):
    while(ind < len(s_input) - 1):
        
        two_chars = s_input[ind:ind + 2]

        if is_alphanum_tuple(two_chars):
            
            #convert
            _pos = alphanum_to_pos(two_chars, b_legacy=False, b_legacy2=True)
            _new = pos_to_alphanum(_pos, b_legacy=False, b_legacy2=False)

            #write
            final_string += _new[0]
            final_string += _new[1]

            ind += 2

        else:
            
            final_string += s_input[ind] 
            ind += 1

    print final_string
    return final_string
            

# tests ----------------------------------------------------            

def test_str_funcs():
    
    s = "a"
    assert True == s.isalpha()
    s = " "
    assert False == s.isalpha()
    s = "1"
    assert False == s.isalpha()
    s = "."
    assert False == s.isalpha()

    s = "1"
    assert True == s.isdigit()
    s = " "
    assert False == s.isdigit()
    s = "a"
    assert False == s.isdigit()
    s = "."
    assert False == s.isdigit()


def test_is_1():
    
    assert True == is_alphanum_tuple("a1")
    assert False == is_alphanum_tuple("1a")

def test_conv_1():
    
    pass
    # s_in = '1. g1 e1 2. b1 d1'
    s_in = '1. a7 a5 2. a2 a4'
    s_out = '1. a2 a4 2. a7 a5'
    assert convert_string(s_in) == s_out

#MAIN
if __name__ == "__main__":
    #must double quote your arg for windows cmd terminal
    convert_string(sys.argv[1])

# src/main.py::test_castling_allowed_misc FAILED                           [ 33%]
# src/main.py::test_castling_disallowed_rook FAILED                        [ 35%]
# src/main.py::test_castling_disallowed_king FAILED                        [ 37%]
# src/main.py::test_enpassant_take FAILED                                  [ 39%]
# src/main.py::test_enpassant_disallowed FAILED                            [ 41%]
# src/main.py::test_king_in_check1 PASSED                                  [ 43%]
# src/main.py::test_king_in_check2 PASSED                                  [ 45%]
# src/main.py::test_king_in_check3 PASSED                                  [ 47%]
# src/main.py::test_post_castling_move_rook FAILED                         [ 50%]
# src/main.py::test_player_in_and_out_of_check FAILED                      [ 52%]
# src/main.py::test_castling_disallowed_in_check FAILED                    [ 54%]
# src/main.py::test_castling_disallowed_into_check FAILED                  [ 56%]
# src/main.py::test_castling_disallowed_when_dead FAILED                   [ 58%]