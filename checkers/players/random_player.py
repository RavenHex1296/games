import random
import math

class RandomPlayer:
    def __init__(self):
        self.player_num = None

    def set_player_number(self, n):
        self.player_num = n

    def choose_move(self, board, choices):
        return random.choice(choices)