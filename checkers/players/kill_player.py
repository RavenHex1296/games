import random
import math

class KillPlayer:
    def __init__(self):
        self.player_num = None

    def set_player_number(self, n):
        self.player_num = n

    def choose_move(self, board, choices):
        for choice in choices:
            if len(choice[2]) > 0:
                return choice

        return random.choice(choices)