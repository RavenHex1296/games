import random
import math
import sys
sys.path.append('tic_tac_toe')
from reduced_depth_game_tree import *

class NNPlayer:
    def __init__(self, ply, neural_net):
        self.symbol = None
        self.player_num = None
        self.ply = ply
        self.neural_net = neural_net
  
    def set_player_number(self, n):
        self.player_num = n
        root_state = [[None, None, None], [None, None, None], [None, None, None]]
        self.game_tree = ReducedSearchGameTree(root_state, self.player_num, self.ply, self.neural_net)

    def convert_board(self, board):
        converted_board = copy.deepcopy(board)

        for row in converted_board:
            for column in row:
                if column == self.player_num:
                    column = 1

                if column == 3 - self.player_num:
                    column = -1

                if column == -self.player_num:
                    column = self.neural_net.k_value

                if column == - (3 - self.player_num):
                    column = -self.neural_net.k_value

        return converted_board

    def choose_move(self, board, choices):
        self.game_tree.reset_node_values()

        converted_board = self.convert_board(board)

        if converted_board not in list(self.game_tree.nodes_dict.keys()):
            self.game_tree.nodes_dict[str(converted_board)] = Node(converted_board, self.player_num, self.player_num)

        current_node = self.game_tree.nodes_dict[str(converted_board)]

        self.game_tree.build_tree([current_node])
        children = self.game_tree.build_tree([current_node])

        for _ in range(self.ply - 1):
            self.game_tree.build_tree(children)
            children = self.game_tree.build_tree(children)

       
        return choice