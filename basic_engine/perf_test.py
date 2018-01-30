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


