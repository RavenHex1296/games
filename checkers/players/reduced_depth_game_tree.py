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
        flattened_board = [piece for row in self.state for piece in row]
        all_pieces = [abs(piece) for piece in flattened_board if piece != 0]
        p1_count = all_pieces.count(1)
        p2_count = all_pieces.count(2)

        if p1_count == 0: return 2
        if p2_count == 0: return 1
        if p1_count == 1 and p2_count == 1: return 'Tie'

        return None

    def convert_board(self, neural_net):
        converted_board = copy.deepcopy(self.state)

        for i in range(0, len(converted_board)):
            for j in range(0, len(converted_board[i])):
                if self.state[i][j] == self.player_num:
                    converted_board[i][j] = 1

                if self.state[i][j] == 3 - self.player_num:
                    converted_board[i][j] = -1

                if self.state[i][j] == -self.player_num:
                    converted_board[i][j] = neural_net.k_value

                if self.state[i][j] == - (3 - self.player_num):
                    converted_board[i][j] = -neural_net.k_value

        return converted_board

    def reduce_board(self, board):
        reduced_board = []

        for i in range(0, len(board)):
            for j in range(0, len(board[i])):
                piece = board[i][j]
                assert abs(piece) <= 3, "Board values too large"

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
            assert len(reduced_board) == 32, "Reduced board given to heurstic isn't correct size"
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

    def add_moves_to_check(self, current_piece, current_coords, captured_coords, moves_to_check):
        
        direction = 1 - 2*(current_piece % 2)

        moves_to_check.append([current_coords, [direction, -1], captured_coords])
        moves_to_check.append([current_coords, [direction, 1], captured_coords])

        if current_piece < 0:
            moves_to_check.append([current_coords, [-direction, -1], captured_coords])
            moves_to_check.append([current_coords, [-direction, 1], captured_coords])

        return moves_to_check

    def nested_list_in_list(self, parent_list, nested_list):
        for l in parent_list:
            if all(x == y for x, y in zip(l, nested_list)):
                return True

        return False

    def get_possible_moves(self, player_num, board):
        possible_moves = []

        # loop through all coordinates

        for i in range(8):
            for j in range(8):

                current_coords = (i, j)
                current_piece = board[i][j]

                # check if there is a piece on the current coord

                if abs(current_piece) == player_num:

                    # get moves that the piece might be able to do

                    moves_to_check = self.add_moves_to_check(current_piece, current_coords, [], [])

                    while len(moves_to_check) > 0:

                        # check first move in moves_to_check

                        move_to_check = moves_to_check.pop(0) # moves_to_check is a queue
                        coord, translation_to_check, captured_coords = move_to_check

                        new_i, new_j = self.translate(coord, translation_to_check)
                        if new_i < 0 or new_i > 7 or new_j < 0 or new_j > 7: continue
                        new_piece = board[new_i][new_j]

                        # check if the new spot is empty

                        if abs(new_piece) == 0 and captured_coords == []:
                            possible_moves.append(move_to_check)
                    
                        # check if the opponent is in the new spot

                        elif abs(new_piece) == 3 - player_num:
                            
                            # if so, and if the next next spot is empty, add that spot to moves_to_check

                            next_translation = [2*t for t in translation_to_check]
                            new_new_i, new_new_j = self.translate(coord, next_translation)
                            if new_new_i < 0 or new_new_i > 7 or new_new_j < 0 or new_new_j > 7: continue
                            new_new_piece = board[new_new_i][new_new_j]

                            if abs(new_new_piece) == 0 and not self.nested_list_in_list(captured_coords, [new_i, new_j]):

                                # add capture to possible moves

                                previous_translation = self.find_translation(coord, current_coords)
                                new_translation = self.translate(previous_translation, next_translation)
                                new_captured_coords = captured_coords + [(new_i, new_j)]
                                possible_moves.append([current_coords, new_translation, new_captured_coords])

                                # add potential to combo captures

                                next_next_coords = self.translate(current_coords, new_translation)
                                moves_to_check = self.add_moves_to_check(current_piece, next_next_coords, new_captured_coords, moves_to_check)

                                # then, it'll loop back to the start of moves_to_check
        
        return possible_moves

    def translate(self, coord1, coord2):
        return (coord1[0] + coord2[0], coord1[1] + coord2[1])

    def find_translation(self, coord1, coord2):
        return (coord1[0] - coord2[0], coord1[1] - coord2[1])

    def update_board(self, move, board):
        x, y = move[0]
        piece = board[x][y]
        board[x][y] = 0

        board[x + move[1][0]][y + move[1][1]] = piece

        if len(move[2]) > 0:
            for killed_coord in move[2]:
                board[killed_coord[0]][killed_coord[1]] = 0

        return board

    def create_children(self, node):
        if node.winner != None or len(node.children) != 0:
            return

        children = []
        possible_moves = self.get_possible_moves(node.turn, node.state)

        for move in possible_moves:
            new_state = self.update_board(move, copy.deepcopy(node.state))

            if str(new_state) in list(self.nodes_dict.keys()):
                #its possible to have both players have that state
                children.append(self.nodes_dict[str(new_state)])
                self.nodes_dict[str(new_state)].previous.append(node)
                continue

            child = Node(new_state, 3 - node.turn, self.player_num)
            child.previous = [node]
            children.append(child)
            self.nodes_dict[str(child.state)] = child

        node.children = children

    def set_node_values(self, nodes_by_layer, neural_net):
        for layer in list(nodes_by_layer.keys())[::-1]:
            for node in nodes_by_layer[layer]:
                if node.children == None or len(node.children) == 0:
                    node.value = node.heuristic_evaluation(neural_net)

                else:
                    if node.turn == node.player_num:
                        node.value = max([child.value for child in node.children])

                    elif node.turn == 3 - node.player_num:
                        node.value = min([child.value for child in node.children])

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