import random
import math
import sys
sys.path.append('checkers/players')
from reduced_depth_game_tree import *

class TopLeftNNPlayer:
    def __init__(self, ply, neural_net):
        self.symbol = None
        self.player_num = None
        self.ply = ply
        self.neural_net = neural_net
  
    def set_player_number(self, n):
        self.player_num = n
        root_state = [[(i + j) % 2 * ((3 - ((j < 3) - (j > 4))) % 3) for i in range(8)] for j in range(8)]
        self.game_tree = ReducedSearchGameTree(root_state, self.player_num, self.ply, self.neural_net)

    def translate(self, chosen_move, board):
        x, y = chosen_move[0]
        piece = board[x][y]
        board[x][y] = 0

        board[x + chosen_move[1][0]][y + chosen_move[1][1]] = piece

        if len(chosen_move[2]) > 0:
            for killed_coord in chosen_move[2]:
                board[killed_coord[0]][killed_coord[1]] = 0

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

        assert len(current_node.children) == len(choices), "Node has different number of children than choices"
        self.game_tree.set_node_values(nodes_by_layer, self.neural_net)
        max_value = current_node.children[0].value

        for child in current_node.children:
            if child.value > max_value:
                max_value = child.value

        optimal_choices = []

        for choice in choices:
            new_board = self.translate(choice, copy.deepcopy(board))
            board_value = self.game_tree.nodes_dict[str(new_board)].value

            if board_value == max_value:
                optimal_choices.append(choice)

        top_left_piece = optimal_choices[0][0]

        for choice in optimal_choices:
            if choice[0][0] < top_left_piece[0]:
                top_left_piece = choice[0]

            elif choice[0][0] == top_left_piece[0] and choice[0][1] < top_left_piece[1]:
                top_left_piece = choice[0]

        options = []

        for choice in optimal_choices:
            if choice[0] == top_left_piece:
                options.append(choice)

        top_left_move = options[0]

        for choice in options:
            if top_left_piece[0] + choice[1][0] < top_left_piece[0] + top_left_move[1][0]:
                top_left_move = choice
                
            elif top_left_piece[0] + choice[1][0] == top_left_piece[0] + top_left_move[1][0] and top_left_piece[1] + choice[1][1] < top_left_piece[1] + top_left_move[1][1]:
                top_left_move = choice

        return top_left_move