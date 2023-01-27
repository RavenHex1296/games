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

    def translate(self, chosen_move, possible_moves, board):
        x, y = chosen_move[0]
        new_x = x + chosen_move[1][0]
        new_y = y + chosen_move[1][1]

        while new_x not in [0, 1, 2, 3, 4, 5, 6, 7] or new_y not in [0, 1, 2, 3, 4, 5, 6, 7]:
            chosen_move = random.choice(possible_moves)
            new_x = x + chosen_move[1][0]
            new_y = y + chosen_move[1][1]

        piece = board[x][y]
        board[x][y] = 0

        if chosen_move[1] in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
            x_change, y_change = chosen_move[1][0] / 2, chosen_move[1][1] / 2
            board[int(x + x_change)][int(y + y_change)] = 0

        if new_x == 0 and piece == 1:
            board[new_x][new_y] = -1

        elif new_x == 7 and piece == 2:
            board[new_x][new_y] = -2

        else:
            board[new_x][new_y] = piece

        return (new_x, new_y)

    def choose_move(self, board, choices):
        self.game_tree.reset_node_values()

        if board not in list(self.game_tree.nodes_dict.keys()):
            self.game_tree.nodes_dict[str(board)] = Node(board, self.player_num, self.player_num)

        current_node = self.game_tree.nodes_dict[str(board)]

        self.game_tree.build_tree([current_node])
        children = self.game_tree.build_tree([current_node])

        for _ in range(self.ply - 1):
            self.game_tree.build_tree(children)
            children = self.game_tree.build_tree(children)

        self.game_tree.set_node_values(current_node)
        max_value_node = current_node.children[0]

        for child in current_node.children:
            if child.value > max_value_node.value:
                max_value_node = child

        optimal_choices = []

        for choice in choices:
            new_board = copy.deepcopy(game_board)
            self.translate(choice, choices, new_board)

            if new_board == max_value_node.state:
                optimal_choices.append(choice)

        choice = random.choice(optimal_choices)
        return choice