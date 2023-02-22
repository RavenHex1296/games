import random
import math

class InputPlayer:
    def __init__(self):
        self.symbol = None
        self.number = None
    
    def set_player_symbol(self, n):
        self.symbol = n

    def set_player_number(self, n):
        self.player_num = n

    def choose_move(self, board, choices):
        for choice in choices:
            print(f"Piece: {choice[0]}, Total translation: {choice[1]}, Captured pieces: {choice[2]}")

        chosen_choice = input("Type index of choice \n")
        return choices[int(chosen_choice)]