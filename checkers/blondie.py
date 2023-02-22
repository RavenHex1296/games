import math
import random
import itertools
import numpy as np
import matplotlib.pyplot as plt
import time
import copy
import sys
sys.path.append('checkers')
from game import *
sys.path.append("checkers/players")
from random_player import *
from neural_net_player import *
from kill_player import *
from input_player import *


logs = Logger('/workspace/games/fogel.txt')

def activation_function(x):
    if x > 100:
        return 1

    if x < -100:
        return 0

    return 1 / (1 + math.exp(-x))


class Node:
    def __init__(self, node_num):
        self.node_num = node_num
        self.parents = []
        self.node_input = None
        self.node_output = 0
        self.children = []


class EvolvedNeuralNet:
    def __init__(self, nodes_by_layer, node_weights, bias_node_nums, piece_difference_node_num, mutation_rate, k):
        self.nodes = nodes_by_layer
        self.node_weights = node_weights
        self.bias_nodes = bias_node_nums
        self.piece_difference_node_num = piece_difference_node_num
        self.mutation_rate = mutation_rate
        self.k_value = k

        for node in flatten(self.nodes):
            if node.node_num in self.bias_nodes:
                node.node_output = 1

        for weight in node_weights:
            i, n = weight.split(',')
            current_node = self.get_node(int(i))
            next_node = self.get_node(int(n))

            current_node.children.append(next_node)

            if int(n) not in self.bias_nodes:
                next_node.parents.append(current_node)

    def build_neural_net(self, input_array):
        for n in range(0, len(input_array)):
            node = self.nodes[1][n]

            if node.node_num == self.piece_difference_node_num:
                continue

            else:
                node.node_input = input_array[n]
                node.node_output = input_array[n]

        piece_difference_node = self.get_node(self.piece_difference_node_num)
        piece_difference_node.node_output = sum([node.node_output for node in self.nodes[1] if node.node_num != piece_difference_node])

        for node in self.nodes[2] + self.nodes[3] + self.nodes[4]:
            total_input = 0

            for input_node in node.parents:
                total_input += input_node.node_output * self.node_weights[str(input_node.node_num) + ',' + str(node.node_num)]

            node.node_input = total_input

            node.node_output = activation_function(total_input)

        return self.nodes[4][0].node_output

    def get_node(self, node_num):
        for node in flatten(self.nodes):
            if node.node_num == node_num:
                return node



def flatten(input_dict):
    flattened_dict = []

    for key in input_dict:
        for value in input_dict[key]:
            flattened_dict.append(value)

    return flattened_dict


def get_weight_ids(nodes_by_layer, bias_node_nums):
    weight_ids = []

    for layer in nodes_by_layer:
        if layer != 4:
            for node in nodes_by_layer[layer]:
                for next_layer_node in nodes_by_layer[layer + 1]:
                    if next_layer_node.node_num not in bias_node_nums:
                        weight_ids.append(f'{node.node_num},{next_layer_node.node_num}')

    return weight_ids


def get_nodes_excluded_from_removal(nodes, bias_node_nums):
    nodes_exempt = []

    for node in nodes:
        if node.node_num in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            nodes_exempt.append(node)

        elif node.node_num in [node.node_num for node in nodes if len(node.children) == 0]:
            nodes_exempt.append(node)

        elif node.node_num in bias_node_nums:
            nodes_exempt.append(node)

    return nodes_exempt



def make_new_gen_v2(parents):
    new_gen = copy.deepcopy(parents)

    for parent in parents:
        child_weights = {}
        child_bias_node_nums = parent.bias_nodes
        child_mutation_rate = parent.mutation_rate * math.exp(np.random.normal(0, 1) / ((2 * (1742 ** 0.5)) ** 0.5))
        child_k = parent.k_value * math.exp(np.random.normal(0, 1) / (2 ** 0.5))

        if child_k < 1:
            child_k = 1

        if child_k > 3:
            child_k = 3

        for weight in parent.node_weights:
            weight_value = parent.node_weights[weight] + child_mutation_rate * np.random.normal(0, 1)
            #assert abs(weight_value) - abs(parent.node_weights[weight]) < 0.3, "Child weight value changed too much"
            child_weights[weight] = weight_value

        child = EvolvedNeuralNet(parent.nodes, child_weights, child_bias_node_nums, parent.piece_difference_node_num, child_mutation_rate, child_k)
        assert child != parent, "Child neural net is the same as parent"
        new_gen.append(child)

    return new_gen


def run_game(players):
    game = TicTacToe(players)
    game.run_to_completion()


def convert_to_nodes_by_layer(nodes): #special to first gen only
    nodes_by_layer = {1: [], 2: [], 3: []}

    for n in range(0, len(nodes)):
        node = nodes[n]

        if n <= 9:
            nodes_by_layer[1].append(node)

        elif node in nodes[-9:]:
            nodes_by_layer[3].append(node)

        else:
            nodes_by_layer[2].append(node)

    return nodes_by_layer

def make_first_gen(population_size):
    first_gen = []

    for n in range(population_size):
        nodes_by_layer = {1: [Node(n) for n in range(1, 34)], 2: [Node(n) for n in range(34, 75)], 3: [Node(n) for n in range(75, 86)], 4: [Node(86)]}
        weight_ids = get_weight_ids(nodes_by_layer, [33, 74, 85])
        nodes_by_layer[1].append(Node(87))
        weight_ids.append("87,86")

        weights = {}

        for weight_id in weight_ids:
            weight = random.uniform(-0.2, 0.2)
            assert abs(weight) <= 0.2
            weights[weight_id] = weight	

        neural_net = EvolvedNeuralNet(nodes_by_layer, weights, [33, 74, 85], 87, 0.05, 2)
        first_gen.append(neural_net)

    return first_gen


def run_games(players, num_games):
    win_data = {1: 0, 2: 0, "Tie": 0}

    for _ in range(num_games):
        game = Checkers(players)
        game.run_to_completion()
        win_data[game.winner] += 1

    return win_data


def get_subset(choices, excluded_net, max_elements):
    subset = []

    while len(subset) < max_elements:
        random_net = random.choice(choices)

        if random_net != excluded_net:
            subset.append(random_net)

    return subset


def evaluation(neural_nets):
    payoff_data = {}

    for neural_net in neural_nets:
        comparing_nets = get_subset(copy.deepcopy(neural_nets), neural_net, 5) #change last number to change number compared to
        payoff_data[neural_net] = 0

        for net in comparing_nets:
            game = Checkers([NNPlayer(2, neural_net), NNPlayer(2, net)])
            game.run_to_completion()

            if game.winner == 1:
                payoff_data[neural_net] += 1

            elif game.winner == 2:
                payoff_data[neural_net] -= 2

    return payoff_data


def select_parents(payoff_data):
    sorted_data = sorted(payoff_data.items(), key=lambda x: x[1], reverse=True)
    sorted_nets = [info[0] for info in sorted_data]
    return sorted_nets[:int(len(sorted_nets) / 2)]


def find_average_payoff(neural_nets, return_net=False):
    payoff_values = []

    for neural_net in neural_nets:
        game = Checkers([NNPlayer(2, neural_net), RandomPlayer()])
        game.run_to_completion()

        if game.winner == 1:
            payoff_values.append(1)

        if game.winner == 2:
            payoff_values.append(-2)

        if game.winner == "Tie":
            payoff_values.append(0)

    #if return_net == True:
        #to_print_data = copy.deepcopy(max_total_payoff_net.__dict__)
        #to_print_data['nodes'] = [node.node_num for node in flatten(to_print_data['nodes'])]
        #file_object.write(f'{max_total_payoff_net.__dict__} \n')
    return sum(payoff_values) / len(payoff_values)


file_object = open('blondie.txt', 'a')


def run(num_first_gen, num_gen):
    average_payoff_values = {}
    return_net = False
    start_time = time.time()
    first_gen = make_first_gen(num_first_gen)
    evaluation_data = evaluation(first_gen)
    #print("Evaluation for Gen 0 Done")
    next_gen_parents = select_parents(evaluation_data)
    #print("Parents from Gen 0 have been selected")
    average_payoff_values[0] = find_average_payoff(next_gen_parents)
    #print("Got Average Total Payoff Value for Gen 0")
    current_gen = make_new_gen_v2(next_gen_parents)
    print(f"Gen 0 took {time.time() - start_time} seconds to complete")


    for n in range(1, num_gen):
        start_time = time.time()
        evaluation_data = evaluation(current_gen)
        #print(f"Evaluation for Gen {n} Done")
        #testing next_gen_parents = select_parents(second_evaluation_data)
        next_gen_parents = select_parents(evaluation_data)
        print(f"Parents from Gen {n} have been selected")            

        #if n == num_gen - 1:
        #    return_net = True

        #max_payoff_values[n] = find_max_payoff(evaluation_data, return_net)
        average_payoff_values[n] = find_average_payoff(next_gen_parents)
        print(f"Got Average Total Payoff Value for Gen {n}")
        current_gen = make_new_gen_v2(next_gen_parents)
        print(f"Gen {n} took {time.time() - start_time} seconds to complete")

    return average_payoff_values


total_values = {}
first_gen_size = 10
num_generations = 10
num_trials = 1

#logs.write(f'HYPERPARAMETERS \n\t Networks in first generation: {first_gen_size} \n\t Selection percentage: 0.5')

for n in range(0, num_generations):
    total_values[n] = 0

#run(first_gen_size, num_generations)

for n in range(0, num_trials):
    start_time = time.time()
    average_payoff_values = run(first_gen_size, num_generations)

    for layer in average_payoff_values:
        total_values[layer] += average_payoff_values[layer]

    print(f"Trial {n} took {time.time() - start_time} seconds to complete")


x_values = [key for key in list(total_values.keys())]
y_values = [value / num_trials for value in list(total_values.values())]

plt.style.use('bmh')
plt.plot(x_values, y_values)
plt.xlabel('num generations')
plt.ylabel('average total payoff')
plt.legend(loc="best")
plt.savefig('blondie.png')