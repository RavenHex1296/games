import random
import copy
import math
import itertools


class SemiRandomPlayer:
    def __init__(self):
        self.number = None
    
    def set_player_number(self, n):
        self.number = n

    def get_diagonals(self, board):
        fdiag = [[] for _ in range(len(board) + len(board[0]) - 1)]
        bdiag = [[] for _ in range(len(fdiag))]

        for x in range(len(board[0])):
            for y in range(len(board)):
                fdiag[x + y].append(board[y][x])
                bdiag[x - y - (1 - len(board))].append(board[y][x])

        return fdiag + bdiag

    def get_columns(self, board):
        columns = []

        for column_index in range(len(board[0])):
            columns.append([row[column_index] for row in board])

        return columns

    def get_row_with_lowest_available_column(self, j, board):
        largest_row = 0

        for n in range(len(board)):
            if board[n][j] == 0:
                largest_row = n

        return largest_row

    def check_for_winner(self, board):
        rows = board
        cols = self.get_columns(board)
        diags = self.get_diagonals(board)

        str_info = []

        board_full = True

        for info in rows + cols + diags:
            if 0 in info:
                board_full = False

        for info in rows + cols + diags:
            for player_num in [1, 2]:
                if str(player_num) * 4 in "".join([str(element) for element in info]):
                    return player_num

        if board_full:
            return 'Tie'

        return None

    def check_if_list_element_in_str(self, input_list, input_string):
        for element in input_list:
            if element in input_string:
                return True

        return False
    
    def choose_move(self, game_board):
        choices = []
        win_choices = []
        block_choices = []

        for i in range(6):
            for j in range(7):
                if game_board[i][j] == 0 and j not in choices:
                    choices.append(j)

        for choice in choices:
            new_board = copy.deepcopy(game_board)
            i = self.get_row_with_lowest_available_column(choice, new_board)
            new_board[i][choice] = self.number

            if self.check_for_winner(new_board) == self.number:
                win_choices.append(choice)

            rows = copy.deepcopy(new_board)

            info = []

            for n in range(0, len(rows)):
                if rows[n] != game_board[n]:
                    info.append(rows[n])
                
            cols = self.get_columns(rows)

            for n in range(0, len(cols)):
                if cols[n] != self.get_columns(game_board)[n]:
                    info.append(cols[n])

            diags = self.get_diagonals(rows)

            for n in range(0, len(diags)):
                if diags[n] != self.get_diagonals(game_board)[n]:
                    info.append(diags[n])
                
            perms = list(itertools.permutations(list(str(3 - self.number)*3 + str(self.number))))
            perms = [''.join(perm) for perm in perms]

            for data in info:
                if self.check_if_list_element_in_str(perms, "".join([str(element) for element in data])):
                    print(f"block choices {choice}")
                    block_choices.append(choice)
            
        if len(win_choices) > 0:
            return random.choice(win_choices)

        if len(block_choices) > 0:
            return random.choice(block_choices)

        return random.choice(choices)


'''
rows = new_board
            cols = self.get_columns(new_board)
            diags = self.get_diagonals(new_board)
            perms = list(itertools.permutations(list(str(3 - self.number)*3 + str(self.number))))
            perms = [''.join(perm) for perm in perms]

            for info in rows + cols + diags:
                if self.check_if_list_element_in_str(perms, info):
                    print(choice)
                    return choice

'''