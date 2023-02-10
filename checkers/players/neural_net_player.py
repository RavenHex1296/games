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
        root_state = [[(i + j) % 2 * ((3 - ((j < 3) - (j > 4))) % 3) for i in range(8)] for j in range(8)]
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

        return board

    def choose_move(self, board, choices):
        self.game_tree.reset_node_values()

        if board not in list(self.game_tree.nodes_dict.keys()):
            self.game_tree.nodes_dict[str(board)] = Node(board, self.player_num, self.player_num)

        current_node = self.game_tree.nodes_dict[str(copy.deepcopy(board))]
        current_nodes = [current_node]
        children = self.game_tree.build_tree(current_nodes)
        nodes_by_layer = {1: current_nodes, 2: children}
        current_nodes = children

        for n in range(3, self.ply + 1):
            children = self.game_tree.build_tree(current_nodes)
            nodes_by_layer[n] = children
            current_nodes = children

        self.game_tree.set_node_values(nodes_by_layer, self.neural_net)
        max_value = current_node.children[0].value

        for child in current_node.children:
            if child.value > max_value:
                max_value = child.value

        optimal_choices = []
        #num choices < num children sometimes fsr?
        for choice in choices:
            new_board = self.translate(choice, choices, copy.deepcopy(board))
            board_value = self.game_tree.nodes_dict[str(new_board)].value
            #if self.game_tree.nodes_dict[str(new_board)] not in current_node.children:
                #print(new_board)

            if board_value == max_value:
                optimal_choices.append(choice)

        choice = random.choice(optimal_choices)
        return choice