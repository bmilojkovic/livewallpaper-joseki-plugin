
import sgf, sys

with open("example.sgf") as f:
    collection = sgf.parse(f.read())

game = collection[0]

current_node = collection[0].nodes[0]

collection.output(sys.stdout)
while current_node is not None:
    if "B" in current_node.properties.keys():
        movex = ord(current_node.properties["B"][0][0]) - ord('a')
        movey = ord(current_node.properties["B"][0][1]) - ord('a')

        print(current_node.properties["B"][0] + " " + str(movex) + " " + str(movey))
        #print(movex)
        #print(" ")
        #print(movey)
    if "W" in current_node.properties.keys():
        print(current_node.properties["W"])

    current_node = current_node.next
