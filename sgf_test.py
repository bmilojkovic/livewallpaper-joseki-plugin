
import sgf, sys, random, pprint


def print_move_node(node):
    if "B" in node.properties.keys():
        movex = ord(node.properties["B"][0][0]) - ord('a')
        movey = ord(node.properties["B"][0][1]) - ord('a')

        print(node.properties["B"][0] + " " + str(movex+1) + " " + str(movey+1))
    if "W" in node.properties.keys():
        movex = ord(node.properties["W"][0][0]) - ord('a')
        movey = ord(node.properties["W"][0][1]) - ord('a')

        print(node.properties["W"][0] + " " + str(movex+1) + " " + str(movey+1))


with open("kjd.sgf") as f:
    collection = sgf.parse(f.read())

var = collection[0]

node_ind = 0

pp = pprint.PrettyPrinter(indent = 4)

while True:
    #print(len(var.nodes))

    print_move_node(var.nodes[node_ind])

    node_ind = node_ind+1

    if len(var.nodes) == node_ind:
        variations = len(var.children)

        if variations == 0:
            break

        var = var.children[random.randint(0, variations - 1)]
        node_ind = 0
