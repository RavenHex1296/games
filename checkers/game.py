import random
from logger import *
import copy
import time

class Checkers:
    def __init__(self, players):
        self.players = players
        self.logs = Logger('/workspace/games/checkers/logs.txt')
        self.logs.clear_log()
        self.set_player_numbers()
        self.board = [[(i + j) % 2 * ((3 - ((j < 3) - (j > 4))) % 3) for i in range(8)] for j in range(8)]
        self.round =  1
        self.winner = None
        self.log_board()

    def set_player_numbers(self): 
        self.players[0].set_player_number(1)
        self.players[1].set_player_number(2)

    def run_to_completion(self):
        while self.winner == None:
            if self.round > 100:
                self.winner = "Tie"
                break

            self.logs.write(f"Beginning round {self.round} \n")
            self.complete_round()
            self.logs.write(f"Ending round {self.round} \n\n")
            self.round += 1

    def complete_round(self):
        for player in self.players:
            possible_moves = self.get_possible_moves(player)

            if possible_moves == []:
                self.winner = 3 - player.player_num
                break

            chosen_move = player.choose_move(copy.deepcopy(self.board), possible_moves)

            if chosen_move not in possible_moves:
                    chosen_move = random.choice(possible_moves)

            self.update_board(player, chosen_move)
            self.winner = self.check_for_winner()

            if self.winner != None:
                break

            self.logs.write(f"\tPlayer {player.player_num} moved from {chosen_move[0]} to {chosen_move[0][0] + chosen_move[1][0], chosen_move[0][1] + chosen_move[1][1]} and captured pieces at {chosen_move[2]}\n")
            self.log_board()

    def translate(self, coord1, coord2):
        return (coord1[0] + coord2[0], coord1[1] + coord2[1])

    def find_translation(self, coord1, coord2):
        return (coord1[0] - coord2[0], coord1[1] - coord2[1])

    def nested_list_in_list(self, parent_list, nested_list):
        for l in parent_list:
            if all(x == y for x, y in zip(l, nested_list)):
                return True

        return False

    def get_possible_moves(self, player, board=None):
        if board == None: board = self.board

        possible_moves = []

        # loop through all coordinates

        for i in range(8):
            for j in range(8):

                current_coords = (i, j)
                current_piece = board[i][j]

                # check if there is a piece on the current coord

                if abs(current_piece) == player.player_num:

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

                        elif abs(new_piece) == 3 - player.player_num:

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

    def add_moves_to_check(self, current_piece, current_coords, captured_coords, moves_to_check):
        direction = 1 - 2*(current_piece % 2)
        moves_to_check.append([current_coords, [direction, -1], captured_coords])
        moves_to_check.append([current_coords, [direction, 1], captured_coords])

        if current_piece < 0:
            moves_to_check.append([current_coords, [-direction, -1], captured_coords])
            moves_to_check.append([current_coords, [-direction, 1], captured_coords])
        
        return moves_to_check

    def update_board(self, player, move):
        current_coords, translation, captured_coords = move
        new_coords = self.translate(current_coords, translation)

        self.board[new_coords[0]][new_coords[1]] = self.board[current_coords[0]][current_coords[1]] # set new coord to the old coord's piece
        self.board[current_coords[0]][current_coords[1]] = 0 # set old coord to 0

        for coords in captured_coords:
            self.board[coords[0]][coords[1]] = 0 # set captured coords to 0

        # turn pieces into kings

        p1_piece_should_be_king = (player.player_num == 1 and new_coords[0] == 0 and self.board[new_coords[0]][new_coords[1]] > 0)
        p2_piece_should_be_king = (player.player_num == 2 and new_coords[0] == 7 and self.board[new_coords[0]][new_coords[1]] > 0)

        if p1_piece_should_be_king or p2_piece_should_be_king:
            self.board[new_coords[0]][new_coords[1]] *= -1

    def check_for_winner(self):
        flattened_board = [piece for row in self.board for piece in row]
        all_pieces = [abs(piece) for piece in flattened_board if piece != 0]

        p1_count = all_pieces.count(1)
        p2_count = all_pieces.count(2)

        if p1_count == 0: return 2
        if p2_count == 0: return 1
        if p1_count == 1 and p2_count == 1: return 'Tie'

        return None

    def log_board(self):
        self.logs.write("-" * 25 + "\n")

        for i in range(len(self.board)):
            row = self.board[i]
            row_string = '|'

            for space in row:
                if space == "":
                    row_string += ' '

                else:
                    if space > 0:
                        row_string += "R" + str(space) + '|'

                    elif space == 0:
                        row_string += "__|"

                    else:
                        row_string += "C" + str(abs(space)) + '|'

            self.logs.write(row_string[:-1] + "|\n" + "-" * 25 + "\n")

        self.logs.write('\n')