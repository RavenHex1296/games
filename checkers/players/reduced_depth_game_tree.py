import copy
import time
import random

class Node():
    def __init__(self, state, turn, player_num):
        self.state = state
        self.turn = turn
        self.player_num = player_num
        self.winner = self.check_for_winner()
        self.previous = []
        self.children = []
        self.value = None

    def get_rows(self):
        return [row for row in self.state]

    def get_columns(self):
        columns = []

        for column_index in range(len(self.state[0])):
            columns.append([row[column_index] for row in self.state])

        return columns

    def get_board_elements(self):
        board_elements = []

        for row in self.state:
            for value in row:
                board_elements.append(value)

        return board_elements

    def flatten(self, board):
        flattened_board = []
        
        for row in board:
            flattened_board += row

        return flattened_board

    def check_for_winner(self):
        flattened_board = self.flatten(copy.deepcopy(self.state))
        remainding_players = []
        remainding_player_instances = {1: 0, 2: 0}

        for entry in flattened_board:
            if entry != 0:
                if abs(entry) not in remainding_players:
                    remainding_players.append(abs(entry))
            
                remainding_player_instances[abs(entry)] += 1

        if len(remainding_players) == 1:
            return remainding_players[0]

        if remainding_player_instances[1] == 1 and remainding_player_instances[2] == 1:
            return "Tie"

    def convert_board(self, neural_net):
        converted_board = copy.deepcopy(self.state)

        for row in converted_board:
            for column in row:
                if column == self.player_num:
                    column = 1

                if column == 3 - self.player_num:
                    column = -1

                if column == -self.player_num:
                    column = neural_net.k_value

                if column == - (3 - self.player_num):
                    column = -neural_net.k_value

        return converted_board

    def reduce_board(self, board):
        reduced_board = []

        for i in range(0, len(board)):
            for j in range(0, len(board[i])):
                if i % 2 == 0:
                    if j % 2 == 1:
                        reduced_board.append(board[i][j])

                if i % 2 == 1:
                    if j % 2 == 0:
                        reduced_board.append(board[i][j])

        return reduced_board

    def heuristic_evaluation(self, neural_net):
        if self.check_for_winner() not in ["Tie", None]:
            if self.check_for_winner() == self.player_num:
                return 1

            if self.check_for_winner() == 3 - self.player_num:
                return -1

        else:
            converted_board = self.convert_board(neural_net)
            reduced_board = self.reduce_board(converted_board)
            neural_net.build_neural_net(reduced_board)
            return neural_net.get_node(86).node_output


class ReducedSearchGameTree():
    def __init__(self, root_state, player_num, ply, neural_net):
        self.root_node = Node(root_state, 1, player_num)
        self.current_nodes = [self.root_node]
        self.num_terminal_nodes = 0
        self.player_num = player_num
        self.nodes_dict = {str(root_state): self.root_node}
        self.ply = ply
        self.neural_net = neural_net

    def get_valid_translations(self, coord, board):
        #print(self.board)
        #print(coord)
        #print(self.board[coord[0]][coord[1]], "\n")

        if board[coord[0]][coord[1]] == 1:
            return [(-1, 1), (-1, -1)]

        if board[coord[0]][coord[1]] == -1 or board[coord[0]][coord[1]] == -2:
            return [(-1, 1), (-1, -1), (1, 1), (1, -1)]

        if board[coord[0]][coord[1]] == 2:
            return [(1, -1), (1, 1)]

    def get_possible_translations(self, coord, board):
        valid_regular_translations = self.get_valid_translations(coord, board)

        possible_regular_translations = []
        possible_kill_translations = []

        for translation in valid_regular_translations:
            new_x = coord[0] + translation[0]
            new_y = coord[1] + translation[1]
            new_kill_x = coord[0] + translation[0] * 2
            new_kill_y = coord[1] + translation[1] * 2

            if new_x in [n for n in range(8)] and new_y in [n for n in range(8)]:
                if board[new_x][new_y] == 0:
                    possible_regular_translations.append(translation)

                if new_kill_x in [n for n in range(8)] and new_kill_y in [n for n in range(8)]:
                    if board[new_x][new_y] == (3 - abs(board[coord[0]][coord[1]])) and board[new_kill_x][new_kill_y] == 0:
                        possible_kill_translations.append((translation[0] * 2, translation[1] * 2))

        return possible_kill_translations + possible_regular_translations

    def get_possible_moves(self, board, player_turn):
        possible_moves = []

        board_elements = []

        for i in range(len(board)):
            for j in range(len(board[i])):
                if abs(board[i][j]) == player_turn:
                    possible_translations = self.get_possible_translations((i, j), copy.deepcopy(board))
                    board_elements.append(board[i][j])

                    for translation in possible_translations:
                        possible_moves.append(((i, j), translation))
        
        return possible_moves

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

    def create_children(self, node):
        if node.winner != None or len(node.children) != 0:
            return

        children = []
        possible_moves = self.get_possible_moves(node.state, node.turn)

        for move in possible_moves:
            new_state = self.translate(move, possible_moves, copy.deepcopy(node.state))

            if str(new_state) in list(self.nodes_dict.keys()):
                #possibly its possible to have both players have that state
                children.append(self.nodes_dict[str(new_state)])
                self.nodes_dict[str(new_state)].previous.append(node)
                continue

            if move[1] in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                child = Node(new_state, node.turn, self.player_num)

            else:
                child = Node(new_state, 3 - node.turn, self.player_num)

            child.previous = [node]
            children.append(child)
            self.nodes_dict[str(child.state)] = child

        node.children = children

    def set_node_values(self, nodes_by_layer, neural_net):
        for layer in list(nodes_by_layer.keys())[::-1]:
            for node in nodes_by_layer[layer]:
                if layer == list(nodes_by_layer.keys())[-1]:
                    node.value = node.heuristic_evaluation(neural_net)

                else:
                    if node.children == None or len(node.children) == 0:
                        node.value = node.heuristic_evaluation(neural_net)

                    else:
                        converted_scores = []

                        for child in node.children:
                            if child.turn == node.turn:
                                converted_scores.append(child.value)

                            else:
                                converted_scores.append(-child.value)

                        if node.turn == node.player_num:
                            node.value = max(converted_scores)

                        elif node.turn == 3 - node.player_num:
                            node.value = min(converted_scores)

    def reset_node_values(self):
        for node in list(self.nodes_dict.values()):
            node.value = None

    def build_tree(self, current_nodes):
        children = []

        for node in current_nodes:
            self.create_children(node)

            if len(node.children) != 0 or node.children != None:
                children += node.children

            else:
                self.num_terminal_nodes += 1

        return children