import sys
import subprocess
import time


def stock_popen():
    cmd = ["../stockfish/src/stockfish"]
    try:
        p = subprocess.Popen(cmd
                            ,shell=False
                            ,stdin=subprocess.PIPE
                            ,stdout=subprocess.PIPE
                            ,universal_newlines=True
                            )
        print 'stockfish popen complete'
    except Exception as e:
        print e
    return p

def send_cmd(p, cmd):
    p.stdin.write(cmd + "\n")
    p.stdin.flush()

def receive_text(p, exit_text = "Checkers:", max_lines = 100):
    lines = []
    for i in range(max_lines):
        line = p.stdout.readline()
        lines.append(line)
        if line[:len(exit_text)] == exit_text:
            return lines
    return lines

    

if __name__ =="__main__":

    p = stock_popen()

    send_cmd(p, "d")
    text = receive_text(p)
    print 'received text: \n'
    print ''.join(text)
    time.sleep(1)

    send_cmd(p, "position startpos moves e2e4")
    
    send_cmd(p, "d")
    text = receive_text(p)
    print 'received text: \n'
    print ''.join(text)
    time.sleep(1)

    

    # print 'poliing...'
    # print p.poll()
    # print 'going d'
    # ret = p.communicate(input="d")
    # print 'd cmd complete \n\n\n\n'
    # print ret
    # print 'poliing...'
    # print p.poll()
    # # time.sleep(3)
    # # print 'going d'
    # # p.communicate(input="d")
    # time.sleep(1)
    # print 'going quit'
    # p.communicate(input="quit")
    # time.sleep(1)
    # print 'going d'
    # p.communicate(input="d")

    # while(True):
    #     inp = raw_input("q on off dcmd \n")
    #     if inp == "q":
    #         sys.exit()
    #     if inp == "on":
    #         print 'calling stock_popen()'
    #         stock_popen()
    #     if inp == "off":
    #         print 'calling quit cmd'
    #         stock_off()
    #     if inp == "demo":
    #         demoA()
    #     if inp == "dcmd":
    #         stock_dcmd()
        




# def capture_image_pi(fn, b_verbose=False):
# 	path_fn = PATH_IMG + fn
# 	cmd = ["raspistill", "-o", path_fn]
# 	if b_verbose:
# 		cmd.exntend(["-v"])
# 	out = subprocess.check_output(cmd)
# 	return out

# def run_opencfu(input_img_path_name, fn, b_windows=False, b_filesystem=True):
# 	cmd = ["opencfu", "-i", input_img_path_name]
# 	if b_windows:
# 		wsl_path = "c:/windows/SysNative/wsl.exe"
# 		cmd = [wsl_path, "opencfu", "-i", input_img_path_name]
# 	if b_filesystem:
# 		path_to_colony_data = PATH_COLONY_DATA + fn + ".csv"
# 		cmd.extend([">", path_to_colony_data])	#pipe to data/colony-data/
# 	output_text = subprocess.check_output(cmd, shell=False)
# 	return output_text