
from go_stone import Stone
from go_algorithm import GoAlgorithm

stones = []
stones.append(Stone(2, 2, Stone.BLACK, "1"))
stones.append(Stone(2, 3, Stone.BLACK, "1"))
stones.append(Stone(1, 2, Stone.WHITE, "1"))
stones.append(Stone(3, 2, Stone.WHITE, "1"))
stones.append(Stone(1, 3, Stone.WHITE, "1"))
stones.append(Stone(3, 3, Stone.WHITE, "1"))
stones.append(Stone(2, 1, Stone.WHITE, "1"))
stones.append(Stone(2, 4, Stone.WHITE, "1"))

print("Before:")
for stone in stones:
    print(stone)

GoAlgorithm.remove_stones(stones, Stone.BLACK)

print("After:")
for stone in stones:
    print(stone)

stones = []
stones.append(Stone(2, 2, Stone.BLACK, "1"))
stones.append(Stone(2, 3, Stone.BLACK, "1"))
stones.append(Stone(1, 2, Stone.WHITE, "1"))
stones.append(Stone(3, 2, Stone.WHITE, "1"))
stones.append(Stone(1, 3, Stone.WHITE, "1"))
stones.append(Stone(3, 3, Stone.WHITE, "1"))
stones.append(Stone(2, 1, Stone.WHITE, "1"))

print("Before:")
for stone in stones:
    print(stone)

GoAlgorithm.remove_stones(stones, Stone.BLACK)

print("After:")
for stone in stones:
    print(stone)