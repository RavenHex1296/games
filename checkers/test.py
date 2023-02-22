import sys
sys.path.append('checkers')
from game import *
sys.path.append("checkers/players")
from random_player import *
from input_player import *
import time


players = [RandomPlayer(), RandomPlayer()]
game = Checkers(players)
game.run_to_completion()
print(game.winner)