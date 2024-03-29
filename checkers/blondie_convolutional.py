import math
import random
import itertools
import numpy as np
import matplotlib.pyplot as plt
import time
import copy
import sys
import ast
sys.path.append('checkers')
from game import *
sys.path.append("checkers/players")
from random_player import *
from neural_net_player import *
from kill_player import *
from input_player import *



def activation_function(x):
    return math.tanh(x)


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

            if node.node_num == self.piece_difference_node_num or node.node_num in self.bias_nodes:
                continue

            else:
                node.node_input = input_array[n]
                node.node_output = input_array[n]

        piece_difference_node = self.get_node(self.piece_difference_node_num)
        piece_difference_node.node_output = sum([node.node_output for node in self.nodes[1] if node.node_num not in [87, 33, 74, 85]])

        for node in self.nodes[2] + self.nodes[3] + self.nodes[4]:
            if node.node_num in self.bias_nodes:
                continue

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

def get_subsquare_nodes(board, row_index, column_index, subsquare_size):
    relevant_node_nums = []

    if row_index + subsquare_size - 1 <= 7 and column_index + subsquare_size - 1 <= 7:
        for i in range(row_index, row_index + subsquare_size):
            for j in range(column_index, column_index + subsquare_size):
                if board[i][j] != 0:
                    relevant_node_nums.append(board[i][j])

    return relevant_node_nums

def get_convoluntional_layer_weight_ids(input_nodes, output_nodes):
    board = [[(i + j) % 2 * ((3 - ((j < 3) - (j > 4))) % 3) for i in range(8)] for j in range(8)]
    current_node_num = 1

    for i in range(0, len(board)):
        for j in range(0, len(board[i])):
            piece = board[i][j]

            if i % 2 == 0:
                if j % 2 == 1:
                    board[i][j] = current_node_num
                    current_node_num += 1

            if i % 2 == 1:
                if j % 2 == 0:
                    board[i][j] = current_node_num
                    current_node_num += 1

    convolutional_layer_connections = {179: []}
    current_convo_node_num = output_nodes[0]

    for node in output_nodes:
        if node != 179:
            convolutional_layer_connections[node] = [33]

    for i in range(0, len(board)):
        for j in range(0, len(board[i])):
            for subsquare_size in [3, 4, 5, 6, 7, 8]:
                subsquare_node_nums = get_subsquare_nodes(board, i, j, subsquare_size)

                if len(subsquare_node_nums) > 0:
                    for node_num in subsquare_node_nums:
                        convolutional_layer_connections[current_convo_node_num].append(node_num)

                    current_convo_node_num += 1

    convolutional_layer_weights = []

    for key in convolutional_layer_connections:
        for value in convolutional_layer_connections[key]:
            convolutional_layer_weights.append(f"{value},{key}")

    return convolutional_layer_weights


def get_weight_ids(nodes_by_layer, bias_node_nums):
    weight_ids = []

    for layer in [2, 3, 4]:
        for node in nodes_by_layer[layer]:
            for next_layer_node in nodes_by_layer[layer + 1]:
                if next_layer_node.node_num not in bias_node_nums:
                    weight_ids.append(f'{node.node_num},{next_layer_node.node_num}')

    all_weights = weight_ids + get_convoluntional_layer_weight_ids([node.node_num for node in nodes_by_layer[1]], [node.node_num for node in nodes_by_layer[2]])
    return all_weights


def make_new_gen_v2(parents):
    new_gen = copy.deepcopy(parents)

    for parent in parents:
        child_weights = {}
        child_bias_node_nums = parent.bias_nodes
        child_mutation_rate = parent.mutation_rate * math.exp(np.random.normal(0, 1) / ((2 * (1742 ** 0.5)) ** 0.5))
        child_k = parent.k_value + random.choice([-0.1, 0, 0.1])

        if child_k < 1:
            child_k = 1

        if child_k > 3:
            child_k = 3

        assert child_k <= 3 and child_k >= 1, "Child k value is out of range"
        weights_increased = False
        weights_decreased = False

        for weight in parent.node_weights:
            weight_value = parent.node_weights[weight] + child_mutation_rate * np.random.normal(0, 1)
            assert weight_value != parent.node_weights[weight], "Child weight is the same as parent"
            assert abs(weight_value) - abs(parent.node_weights[weight]) < 6 * child_mutation_rate, "Child weight value changed too much"

            if weight_value - parent.node_weights[weight] > 0:
                weights_increased = True
            
            if weight_value - parent.node_weights[weight] < 0:
                weights_decreased = True

            child_weights[weight] = weight_value

        assert weights_increased == True and weights_decreased == True, "Weights either did not increase or decrease"
        child = EvolvedNeuralNet(parent.nodes, child_weights, child_bias_node_nums, parent.piece_difference_node_num, child_mutation_rate, child_k)
        assert child != parent, "Child neural net is the same as parent"
        new_gen.append(child)

    return new_gen


def make_first_gen(population_size):
    first_gen = []

    for n in range(population_size):
        nodes_by_layer = {1: [Node(n) for n in range(1, 34)], 2: [Node(n) for n in range(88, 180)], 3: [Node(n) for n in range(34, 75)], 4: [Node(n) for n in range(75, 86)], 5: [Node(86)]}
        weight_ids = get_weight_ids(nodes_by_layer, [33, 179, 74, 85])
        nodes_by_layer[1].append(Node(87))
        weight_ids.append("87,86")

        weights = {}

        for weight_id in weight_ids:
            weight = random.uniform(-0.2, 0.2)
            assert abs(weight) <= 0.2, "Initial weight is not in [-0.2, 0.2]"
            weights[weight_id] = weight	

        #assert(abs(sum(list(weights.values()))) < 100), "Sum of initial weights too large"
        neural_net = EvolvedNeuralNet(nodes_by_layer, weights, [33, 74, 85, 179], 87, 0.05, 2)
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
    num_rounds_data = []

    for neural_net in neural_nets:
        #comparing_nets = get_subset(copy.deepcopy(neural_nets), neural_net, 3) #change last number to change num evaluated against
        payoff_data[neural_net] = 0
        for _ in range(3):

        #for net in comparing_nets:
            #game = Checkers([NNPlayer(2, neural_net), NNPlayer(2, net)])
            game = Checkers([NNPlayer(2, neural_net), RandomPlayer()])

            try:
                game.run_to_completion()

            except:
                game.winner = "Tie"

                with open("blondie_convolutional.txt", "a") as file:
                    file.write("Game vs another net was not run properly \n")

            if game.winner == 1:
                payoff_data[neural_net] += 1

            elif game.winner == 2:
                payoff_data[neural_net] -= 2

            num_rounds_data.append(game.round)

    with open("blondie_convolutional.txt", "a") as file:
        file.write(f"avg number of rounds {sum(num_rounds_data) / len(num_rounds_data)} \n")

    print(f"avg number of rounds {sum(num_rounds_data) / len(num_rounds_data)}")
    return payoff_data


def save_parents(parents):
    for parent in parents:
        to_print_data = {}
        print_nodes = {}

        to_print_data["node_weights"] = parent.node_weights
        to_print_data['mutation_rate'] = parent.mutation_rate
        to_print_data["k"] = [parent.k_value]

        with open("saved_parents.txt", "a") as file:
            file.write(f'{to_print_data} \n\n')


def get_text_file_data(text_file_name):
    f = open(text_file_name, "r")
    list_data = f.read().split("\n")
    neural_net_data = []

    for neural_net in list_data[1:]:
        neural_net_data.append(ast.literal_eval(neural_net))

    return neural_net_data #make sure to remove blank line at end of txt file


def turn_txt_file_into_nets(txt_file_data):
    neural_nets = []
    nodes_by_layer = {1: [Node(n) for n in range(1, 34)], 2: [Node(n) for n in range(88, 180)], 3: [Node(n) for n in range(34, 75)], 4: [Node(n) for n in range(75, 86)], 5: [Node(86)]}
    nodes_by_layer[1].append(Node(87))

    for data in txt_file_data:
        neural_net = EvolvedNeuralNet(nodes_by_layer, data['node_weights'], [33, 74, 85, 179], 87, data['mutation_rate'], data['k'])
        neural_nets.append(neural_net)

    return neural_nets


def select_parents(payoff_data):
    sorted_data = sorted(payoff_data.items(), key=lambda x: x[1], reverse=True)
    sorted_nets = [info[0] for info in sorted_data]
    return sorted_nets[:int(len(sorted_nets) / 2)]


def find_average_payoff(neural_nets, return_net=False):
    payoff_values = {}

    for neural_net in neural_nets:
        payoff_values[neural_net] = 0

    for neural_net in neural_nets:
        game = Checkers([NNPlayer(2, neural_net), RandomPlayer()])

        try:
            game.run_to_completion()

        except:
            game.winner = "Tie"

            with open("blondie_convolutional.txt", "w") as file:
                file.write("Game vs kill player not run properly \n")

        if game.winner == 1:
            payoff_values[neural_net] = 1

        if game.winner == 2:
            payoff_values[neural_net] = -2

        if game.winner == "Tie":
            payoff_values[neural_net] = 0


    if return_net == True:
        max_total_payoff_net = neural_nets[0]

        for neural_net in payoff_values:
            if payoff_values[max_total_payoff_net] < payoff_values[neural_net]:
                max_total_payoff_net = neural_net

        to_print_data = copy.deepcopy(max_total_payoff_net.__dict__)
        print_nodes = {}

        for layer in to_print_data['nodes']:
            print_nodes[layer] = [node.node_num for node in to_print_data['nodes'][layer]]

        to_print_data['nodes'] = print_nodes

        with open("blondie_convolutional.txt", "a") as file:
            file.write(f'{to_print_data} \n')

    avg_gen_payoff = sum([value for value in list(payoff_values.values())]) / len([value for value in list(payoff_values.values())])
    
    with open("blondie_convolutional.txt", "a") as file:
        file.write(f"{payoff_values.values()} \n {avg_gen_payoff} \n\n")

    with open("saved_gen_payoffs.txt", "a") as file:
        file.write(f"{avg_gen_payoff},")

    print(payoff_values.values())
    return avg_gen_payoff


def run(num_first_gen, num_gen):
    with open("saved_parents.txt", 'w') as file:
        file.writelines([''])

    with open("saved_parents.txt", "w") as file:
        file.write('Gen 0 \n')

    average_payoff_values = {}
    return_net = False
    start_time = time.time()
    first_gen = make_first_gen(num_first_gen)
    evaluation_data = evaluation(first_gen)
    #print("Evaluation for Gen 0 Done")
    next_gen_parents = select_parents(evaluation_data)
    save_parents(next_gen_parents)
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
        with open("saved_parents.txt", 'w') as file:
            file.writelines([''])
            file.write(f'Gen {n} \n')

        save_parents(next_gen_parents)
        #print(f"Parents from Gen {n} have been selected")

        if n == num_gen - 1:
            return_net = True

        #max_payoff_values[n] = find_max_payoff(evaluation_data, return_net)
        average_payoff_values[n] = find_average_payoff(next_gen_parents, return_net)
        #print(f"Got Average Total Payoff Value for Gen {n}")
        current_gen = make_new_gen_v2(next_gen_parents)
        print(f"Gen {n} took {time.time() - start_time} seconds to complete")

    return average_payoff_values


def continue_evo(parents, start_gen, end_gen):
    with open("saved_parents.txt", 'w') as file:
        file.writelines([''])

    with open("saved_parents.txt", "w") as file:
        file.write(f'Gen {start_gen} \n')

    average_payoff_values = {}
    return_net = False
    start_time = time.time()
    first_gen = make_first_gen(num_first_gen)
    evaluation_data = evaluation(first_gen)
    #print("Evaluation for Gen 0 Done")
    next_gen_parents = select_parents(evaluation_data)
    save_parents(next_gen_parents)
    #print("Parents from Gen 0 have been selected")
    average_payoff_values[0] = find_average_payoff(next_gen_parents)
    #print("Got Average Total Payoff Value for Gen 0")
    current_gen = make_new_gen_v2(next_gen_parents)
    print(f"Gen 0 took {time.time() - start_time} seconds to complete")


    for n in range(start_gen + 1, end_gen):
        start_time = time.time()
        evaluation_data = evaluation(current_gen)
        #print(f"Evaluation for Gen {n} Done")
        #testing next_gen_parents = select_parents(second_evaluation_data)
        next_gen_parents = select_parents(evaluation_data)
        with open("saved_parents.txt", 'w') as file:
            file.writelines([''])
            file.write(f'Gen {n} \n')

        save_parents(next_gen_parents)
        #print(f"Parents from Gen {n} have been selected")

        if n == num_gen - 1:
            return_net = True

        #max_payoff_values[n] = find_max_payoff(evaluation_data, return_net)
        average_payoff_values[n] = find_average_payoff(next_gen_parents, return_net)
        #print(f"Got Average Total Payoff Value for Gen {n}")
        current_gen = make_new_gen_v2(next_gen_parents)
        print(f"Gen {n} took {time.time() - start_time} seconds to complete")

    return average_payoff_values


total_values = {}
first_gen_size = 10
num_generations = 100
num_trials = 1

for n in range(0, num_generations):
    total_values[n] = 0


#converts txt data to neural net objects
data = get_text_file_data("saved_parents.txt")
neural_nets = turn_txt_file_into_nets((data))
payoff_values = continue_evo(neural_nets, 51, 100)

'''
for n in range(0, num_trials):
    start_time = time.time()
    average_payoff_values = run(first_gen_size, num_generations)

    for layer in average_payoff_values:
        total_values[layer] += average_payoff_values[layer]

    print(f"Trial {n} took {time.time() - start_time} seconds to complete")
'''
'''
x_values = [n for n in range(0, 100)]#[key for key in list(total_values.keys())]
y_values = [value / num_trials for value in list(total_values.values())]

plt.style.use('bmh')
plt.plot(x_values, y_values)
plt.xlabel('num generations')
plt.ylabel('average total payoff')
plt.legend(loc="best")
plt.savefig('convo_blondie_train_eachother_test_randomv2.png')
'''