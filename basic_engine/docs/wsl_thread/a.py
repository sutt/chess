'''
This looks at outputting a launched WSL process to a tmp file
'''

import os
import subprocess
import time



def simple_popen_wsl(b_lines=True, num_lines=5):

    f = open('tmp.txt', 'w')

    proc = subprocess.Popen(
                    [
                    'c:/windows/sysnative/bash.exe'
                    ,'-c'
                    ,"printenv"
                    ]
            
                    ,stdin=subprocess.PIPE
                    ,stdout=f
                    ,stderr=subprocess.PIPE
            
                    ,cwd = "/"                    
            )

    proc.wait()
    
    f.close()                   #does this before/after wait() matter?

    with open('tmp.txt', 'r') as f2:
    
        if b_lines:
            print ''.join(f2.readlines())
        else:
            for i in range(num_lines):
                print f2.readline()

    
    
def full_flask_1():

    
    if 'tmp2.txt' in os.listdir(os.getcwd()):
        try:
            os.remove('tmp2.txt')
            print 'removed tmp2.txt'
        except:
            print 'couldnt remove tmp2.txt'
    else:
        print 'couldnt find tmp2.txt'
    
    
    f = open('tmp2.txt', 'w')

    t0 = time.time()
    
    proc = subprocess.Popen(
                    [
                    'c:/windows/sysnative/bash.exe'
                    ,'-c'
                    ,"printenv"
                    ,"&&"
                    ,"source"
                    , "~/.customprofile"
                    ,"&&"
                    ,"flask"
                    ,"run"
                    ]
            
            ,stdin=subprocess.PIPE
            ,stdout=subprocess.PIPE
            ,stderr=f
            
            ,cwd = '../../../stockfish/api/'
        )


    f.close()

    
    with open('tmp2.txt', 'r') as f2:

        while(True):

            if time.time() - t0 > 5:
                print 'timed out'
                break
            
            line = f2.readline()
            if line.find('http:') > -1:
                print line
                print 'time to find: ', str(time.time() - t0)[:4]
                #reliably 0.63-0.65 secs
                break

            time.sleep(.1)
    
    
    print 'three seconds till proc kill'
    time.sleep(3)
    proc.kill()    
    
    
    print 'done.'


if __name__ == "__main__":
    # simple_popen_wsl(b_lines=False, num_lines=30)
    full_flask_1()

