import sys
import subprocess
import time


'''
TODOs
    add clean text function
    make it a class to import it
    flush title statement
    add new game feature
        with tests
    add a set position function
    add a go command
    add a fen extractor

QUESITONS
    how to test if stockfish has all valid moves?

'''

def stock_popen():
    cmd = ["../stockfish/src/stockfish"]
    try:
        p = subprocess.Popen(cmd
                            ,shell=False
                            ,stdin=subprocess.PIPE
                            ,stdout=subprocess.PIPE
                            ,universal_newlines=True
                            )
    except Exception as e:
        print(e)
    return p

def flush_process_stdout(p):
    """ this doesnt appear to work """
    p.stdout.flush()        #This fails to work
    p.stdout.readline( )    #This works, but hangs if called incorrectly

def send_cmd(p, cmd):
    p.stdin.write(cmd + "\n")
    p.stdout.flush()

def receive_text(p, exit_text = "Checkers:", max_lines = 100):
    lines = []
    for i in range(max_lines):
        try:
            line = p.stdout.readline()
        except:
            return lines
        lines.append(line)
        if line[:len(exit_text)] == exit_text:
            return lines
    return lines

    

if __name__ =="__main__":

    p = stock_popen()

    send_cmd(p, "d")
    text = receive_text(p)
    print('received text: \n')
    print(''.join(text))
    time.sleep(1)

    send_cmd(p, "position startpos moves e2e4")
    
    send_cmd(p, "d")
    text = receive_text(p)
    print('received text: \n')
    print(''.join(text))
    time.sleep(1)





def test_stock_on():
    p = stock_popen()
    txt = receive_text(p, exit_text = "Stockfish")
    assert len(txt) == 1
    clean_txt = ''.join(txt).strip()
    assert clean_txt == "Stockfish 200818 64 by T. Romstad, M. Costalba, J. Kiiski, G. Linscott"

def test_receive_text_no_match():
    pass
    # p = stock_popen()
    # txt = receive_text(p, exit_text = "blah blah", max_lines=10)
    # assert len(txt) == 10
    # assert txt[1] is None
    
    
def test_stock_cmd_d():
    p = stock_popen()
    time.sleep(1)
    # flush_process_stdout(p)
    
    send_cmd(p, "d")
    txt = receive_text(p, exit_text = "Checkers:")
    print('_________________________')
    print(''.join(txt))
    assert txt[2] ==' +---+---+---+---+---+---+---+---+\n'
    assert txt[3] == ' | r | n | b | q | k | b | n | r |\n'
    
    clean_txt = ''.join(txt).strip()

    
