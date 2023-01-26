import random
import time
#import numpy as np
import itertools

def transpose(input_board):
    return np.array(input_board).T.tolist()

nodes_by_layer = {1: [n for n in range(1, 34)], 2: [n for n in range(34, 75)], 3: [n for n in range(75, 86)], 4: [86]}

print(nodes_by_layer)