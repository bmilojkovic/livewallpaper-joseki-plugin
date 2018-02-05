
from go_stone import Stone


class GoAlgorithm(object):

    @staticmethod
    def __print_board(board):
        for row in board:
            s = ""
            for val in row:
                if val == Stone.WHITE:
                    s += "1 "
                elif val == Stone.BLACK:
                    s += "2 "
                else:
                    s += "0 "
            print(s)

    @staticmethod
    def __clone_board(board):
        new_board = [[0 for x in range(19)] for y in range(19)]

        for row in range(19):
            for val in range(19):
                new_board[row][val] = board[row][val]

        return new_board

    @staticmethod
    def __mark_libs(pos_x, pos_y, color, tmp_board):
        if pos_x < 0 or pos_x > 18 or pos_y < 0 or pos_y > 18:
            return
        if tmp_board[pos_x][pos_y] == Stone.EMPTY:
            tmp_board[pos_x][pos_y] = Stone.LIBERTY
        elif tmp_board[pos_x][pos_y] == color:
            tmp_board[pos_x][pos_y] = -1
            GoAlgorithm.__mark_libs(pos_x - 1, pos_y, color, tmp_board)
            GoAlgorithm.__mark_libs(pos_x + 1, pos_y, color, tmp_board)
            GoAlgorithm.__mark_libs(pos_x, pos_y - 1, color, tmp_board)
            GoAlgorithm.__mark_libs(pos_x, pos_y + 1, color, tmp_board)

    @staticmethod
    def __count_libs(tmp_board):
        count = 0
        for row in tmp_board:
            for val in row:
                if val == Stone.LIBERTY:
                    count = count + 1

        return count

    @staticmethod
    def __erase_group(pos_x, pos_y, color, board, stones):
        if pos_x < 0 or pos_x > 18 or pos_y < 0 or pos_y > 18:
            return
        if board[pos_x][pos_y] == color:
            board[pos_x][pos_y] = Stone.EMPTY
            for stone in stones:
                if stone.pos_x == pos_x and stone.pos_y == pos_y:
                    stone.removed = True

            GoAlgorithm.__erase_group(pos_x - 1, pos_y, color, board, stones)
            GoAlgorithm.__erase_group(pos_x + 1, pos_y, color, board, stones)
            GoAlgorithm.__erase_group(pos_x, pos_y - 1, color, board, stones)
            GoAlgorithm.__erase_group(pos_x, pos_y + 1, color, board, stones)

    @staticmethod
    def remove_stones(stones, color):
        board = [[Stone.EMPTY for x in range(19)] for y in range(19)]

        for stone in stones:
            board[stone.pos_x][stone.pos_y] = stone.stone_color

        for stone in stones:
            if stone.stone_color == color:
                tmp_board = GoAlgorithm.__clone_board(board)
                GoAlgorithm.__mark_libs(stone.pos_x, stone.pos_y, stone.stone_color, tmp_board)
                count = GoAlgorithm.__count_libs(tmp_board)
                if count == 0:
                    GoAlgorithm.__erase_group(stone.pos_x, stone.pos_y, stone.stone_color, board, stones)

