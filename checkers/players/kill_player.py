import random
import math

class KillPlayer:
    def __init__(self):
        self.player_num = None

    def set_player_number(self, n):
        self.player_num = n

    def choose_move(self, board, choices):
        for choice in choices:
            if (2, 2) in choice[1] or (2, -2) in choice[1] or (-2, 2) in choice[1] or (-2, -2) in choice[1]:
                return choice

        return random.choice(choices)