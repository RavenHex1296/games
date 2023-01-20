import random
from logger import *
import copy

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

    def get_valid_translations(self, coord):
        if self.board[coord[0]][coord[1]] == 1:
            return [(-1, 1), (-1, -1)]

        if self.board[coord[0]][coord[1]] < 0:
            return [(-1, 1), (-1, -1), (1, 1), (1, -1)]

        if self.board[coord[0]][coord[1]] == 2:
            return [(1, -1), (1, 1)]

    def get_valid_kill_translations(self, coord):
        if self.board[coord[0]][coord[1]] == 1:
            return [(-2, 2), (-2, -2)]

        if self.board[coord[0]][coord[1]] == 2:
            return [(2, -2), (2, 2)]

        else:
            return [(-2, 2), (-2, -2), (2, -2), (2, 2)]

    def get_possible_translations(self, coord):
        valid_regular_translations = self.get_valid_translations(coord)

        possible_regular_translations = []
        possible_kill_translations = []

        for translation in valid_regular_translations:
            new_x = coord[0] + translation[0]
            new_y = coord[1] + translation[1]
            new_kill_x = coord[0] + translation[0] * 2
            new_kill_y = coord[1] + translation[1] * 2

            if new_x in [n for n in range(8)] and new_y in [n for n in range(8)]:
                if self.board[new_x][new_y] == 0:
                    possible_regular_translations.append(translation)

                if new_kill_x in [n for n in range(8)] and new_kill_y in [n for n in range(8)]:
                    if self.board[new_x][new_y] == (3 - abs(self.board[coord[0]][coord[1]])) and self.board[new_kill_x][new_kill_y] == 0:
                        possible_kill_translations.append((translation[0] * 2, translation[1] * 2))


        if len(possible_kill_translations) > 0:
            return possible_kill_translations

        else:
            return possible_regular_translations

    def get_possible_moves(self, player):
        possible_moves = []

        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == player.player_num:
                    possible_translations = self.get_possible_translations((i, j))

                    for translation in possible_translations:
                        possible_moves.append(((i, j), translation))

        return possible_moves

    def get_possible_pieces(self, player):
        movable_pieces = []
        all_piece_coords = []

        for i in board:
            for j in board[i]:
                if abs(board[i][j]) == player.player_number:
                    all_piece_coords.append((i, j))

        for coord in all_piece_coords:
            if len(self.get_possible_translations(coord)) > 0:
                movable_pieces.append(coord)
        
        return movable_pieces

    def translate(self, chosen_move, possible_moves):
        x, y = chosen_move[0]
        new_x = x + chosen_move[1][0]
        new_y = y + chosen_move[1][1]

        while new_x not in [0, 1, 2, 3, 4, 5, 6, 7] or new_y not in [0, 1, 2, 3, 4, 5, 6, 7]:
            chosen_move = random.choice(possible_moves)
            new_x = x + chosen_move[1][0]
            new_y = y + chosen_move[1][1]

        piece = self.board[x][y]
        self.board[x][y] = 0

        if new_x == 0 and piece == 1:
            self.board[new_x][new_y] = -1

        elif new_x == 7 and piece == 2:
            self.board[new_x][new_y] = -2

        else:
            self.board[new_x][new_y] = piece

        return (new_x, new_y)

    def move_again(self, possible_translations):
        if (-2, 2) not in possible_translations and (-2, -2) not in possible_translations and (2, 2) not in possible_translations and (2, -2) not in possible_translations:
            return False

        return True

    def complete_round(self):
        for player in self.players:
            possible_moves = self.get_possible_moves(player)

            if len(possible_moves) == 0:
                self.winner = 3 - player.player_num
                break

            chosen_move = player.choose_move(copy.deepcopy(self.board), possible_moves)

            if chosen_move not in possible_moves:
                chosen_move = random.choice(possible_moves)

            new_coords = self.translate(chosen_move, possible_moves)

            while chosen_move[1] in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                possible_translations = self.get_possible_translations(new_coords)
                possible_moves = [[new_coords, translation] for translation in possible_translations]

                if self.move_again(possible_translations) == True:
                    chosen_move = player.choose_move(copy.deepcopy(self.board), possible_moves)
                    new_coords = self.translate(chosen_move, possible_moves)

                else:
                    break

        self.round += 1
        self.log_board()

    def run_to_completion(self):
        while self.winner == None:
            self.complete_round()

        if self.winner != 'Tie':
            self.logs.write(f'Player {self.winner} won')

        else:
            self.logs.write('Tie')

    def get_diagonals(self):
        fdiag = [[] for _ in range(len(self.board) + len(self.board[0]) - 1)]
        bdiag = [[] for _ in range(len(fdiag))]

        for x in range(len(self.board[0])):
            for y in range(len(self.board)):
                fdiag[x + y].append(self.board[y][x])
                bdiag[x - y - (1 - len(self.board))].append(self.board[y][x])

        return fdiag + bdiag

    def get_columns(self):
        columns = []

        for column_index in range(len(self.board[0])):
            columns.append([row[column_index] for row in self.board])

        return columns

    def flatten(self, board):
        flattened_board = []
        
        for row in board:
            for column in board[row]:
                flattened_board.append(board[row][column])

    def check_for_winner(self):
        flattened_board = self.flatten(copy.deepcopy(self.board))
        remainding_players = []
        remainding_player_instances = {1: 0, 2: 0}

        for entry in flattened_board:
            if entry != 0:
                remainding_players.append(entry)
                remainding_player_instances[entry] += 1

        if len(remainding_players) == 1:
            return remainding_players[0]

        if remainding_player_instances[1] == 1 and remainding_player_instances[2] == 1:
            return "Tie"


    def log_board(self):
        for i in range(len(self.board)):
            row = self.board[i]
            row_string = ''

            for space in row:
                if space == "":
                    row_string += ' '

                else:
                    if space >= 0:
                        row_string += "+" + str(space) + ' '

                    else:
                        row_string += str(space) + ' '

            self.logs.write(row_string[:-1] + "\n")

        self.logs.write('\n')