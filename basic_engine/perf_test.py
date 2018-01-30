import time
from main import Game

n = 10

ss = "1. h7 f8 2. b1 c1 3. g5 e5 4. b2 c2 5. h6 f4 6. b3 c3 7. h5 h6 8. b4 c4 9. h6 h5 10. b5 c5"

t0 = time.time()
for i in range(n):
    game = Game(s_instructions = ss)
    game.play()
t1 = time.time()

t = float(float(t1) - float(t0))
print 'total time: ', str(t)[:5]

t = float(t)/ float(n)
print 'per game: ', str(t)[:7]

t0 = time.time()
for i in range(n):
    game = Game(s_instructions = ss)
    game.play(king_in_check_on=False)
t1 = time.time()

t = float(float(t1) - float(t0))
print 'total time: ', str(t)[:5]

t = float(t)/ float(n)
print 'per game: ', str(t)[:7]

t0 = time.time()
for i in range(n):
    game = Game(s_instructions = ss)
    game.play(king_in_check_on=False, king_in_check_test_copy=True)
t1 = time.time()

t = float(float(t1) - float(t0))
print 'total time: ', str(t)[:5]

t = float(t)/ float(n)
print 'per game: ', str(t)[:7]

### 100x slower without filter king in check, 50x slower just with copying ###
# total time:  2.502
# per game:  0.25020
# total time:  0.046
# per game:  0.00469
# total time:  1.657
# per game:  0.16570
