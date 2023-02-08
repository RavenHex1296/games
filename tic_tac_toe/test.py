import sys
sys.path.append('tic_tac_toe')
from game import *
sys.path.append("tic_tac_toe/players")
from random_player import *
from input_player import *
from heuristic_minimax import *
from minimax_player import *
from near_perfect import *
from top_left import *
import time

'''
alternate = False
win_data = {1: 0, 2: 0}

for _ in range(100):
    game = TicTacToe([RandomPlayer(), RandomPlayer()])
    game.run_to_completion()

    if game.winner != 'Tie':
        if alternate:
            win_data[3 - game.winner] += 1

        else:
            win_data[game.winner] += 1

    alternate = not alternate

print("100 games:", win_data, "\n")

alternate = False
win_data = {1: 0, 2: 0}

for _ in range(1000):
    players = [RandomPlayer(), RandomPlayer()]
    game = TicTacToe(players)
    game.run_to_completion()

    if game.winner != 'Tie':
        if alternate:
            win_data[3 - game.winner] += 1

        else:
            win_data[game.winner] += 1

    alternate = not alternate

print("1000 games:", win_data)

'''

'''
all_possible_game_states = []

def get_random_game_state():
    state = ''

    for _ in range(9):
        state += str(random.choice([0, 1, 2]))

    return state

start_time = time.time()

while len(all_possible_game_states) < (3 ** 9):
    new_state = get_random_game_state()

    if new_state not in all_possible_game_states:
        all_possible_game_states.append(new_state)


for _ in range(10):
    game = TicTacToe([RandomPlayer(), RandomPlayer()])
    game.run_to_completion()
    print(game.winner)

'''
'''
win_data = {1: 0, 2: 0, "Tie": 0}
print("p1")
for _ in range(25):
    players = [MiniMaxPlayer(), RandomPlayer()]
    game = TicTacToe(players)
    game.run_to_completion()

    print(game.winner)
    win_data[game.winner] += 1

print("p2")
for _ in range(25):
    players = [RandomPlayer(), MiniMaxPlayer()]
    game = TicTacToe(players)
    game.run_to_completion()
    print(game.winner)
    if game.winner == 1:
        win_data[2] += 1

    if game.winner == 2:
        win_data[1] += 1

    if game.winner == "Tie":
        win_data["Tie"] += 1

print(win_data)
'''
'''
win_data = {1: 0, 2: 0, "Tie": 0}
for _ in range(10):
    players = [HeuristicMiniMax(ply=5), HeuristicMiniMax(ply=9)]
    game = TicTacToe(players)
    game.run_to_completion()

    win_data[game.winner] += 1

for _ in range(10):
    players = [HeuristicMiniMax(ply=9), HeuristicMiniMax(ply=5)]
    game = TicTacToe(players)
    game.run_to_completion()
    if game.winner == 1:
        win_data[2] += 1

    if game.winner == 2:
        win_data[1] += 1

    if game.winner == "Tie":
        win_data["Tie"] += 1

print(f"5 ply vs 9 ply {win_data}")


win_data = {1: 0, 2: 0, "Tie": 0}
for _ in range(10):
    players = [HeuristicMiniMax(ply=5), RandomPlayer()]
    game = TicTacToe(players)
    game.run_to_completion()

    win_data[game.winner] += 1

for _ in range(10):
    players = [RandomPlayer(), HeuristicMiniMax(ply=5)]
    game = TicTacToe(players)
    game.run_to_completion()
    if game.winner == 1:
        win_data[2] += 1

    if game.winner == 2:
        win_data[1] += 1

    if game.winner == "Tie":
        win_data["Tie"] += 1

print(f"5 ply vs Random {win_data}")


win_data = {1: 0, 2: 0, "Tie": 0}
for _ in range(10):
    players = [HeuristicMiniMax(ply=9), RandomPlayer()]
    game = TicTacToe(players)
    game.run_to_completion()

    win_data[game.winner] += 1

for _ in range(10):
    players = [RandomPlayer(), HeuristicMiniMax(ply=9)]
    game = TicTacToe(players)
    game.run_to_completion()
    if game.winner == 1:
        win_data[2] += 1

    if game.winner == 2:
        win_data[1] += 1

    if game.winner == "Tie":
        win_data["Tie"] += 1

print(f"9 ply vs Random {win_data}")
'''
start_time = time.time()
players = [HeuristicMiniMax(ply=4), RandomPlayer()]
game = TicTacToe(players)
game.run_to_completion()
print(time.time() - start_time)