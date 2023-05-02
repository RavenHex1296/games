import ast

def get_text_file_data(text_file_name):
    f = open(text_file_name, "r")
    list_data = f.read().split("\n")
    neural_net_data = []

    for neural_net in list_data[1:]:
        neural_net_data.append(ast.literal_eval(neural_net))

    return neural_net_data
    
data = get_text_file_data("saved_parents.txt")

print(data[0].keys())