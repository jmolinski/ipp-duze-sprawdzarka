import re
import sys
from typing import List


def get_board() -> List[str]:
    height = 0
    width = 0
    board = []
    for line in sys.stdin.readlines():
        line = line.strip()
        if not line:
            break
        height += 1
        if not width:
            width = len(line)
        if width != len(line):
            raise Exception("Lines have different width")
        if not re.match(r"([1-9]|\.)+", line):
            print(line)
            raise Exception("Incorrect line")
        board.append(line)
    if height < 2 or width < 1:
        raise Exception("Dimensions are to small")
    return board


def main():
    board = get_board()
    width = len(board[0])
    height = len(board)
    print(f"START {width} {height} 9 {width * height}")
    for y, row in enumerate(board, start=1):
        for x, cell in enumerate(row):
            if cell == ".":
                continue
            print(f"GOTO {x} {height - y}")
            player = int(cell)
            print(f"SKIPTURNS {player - 1}")
            print(f"MOVE")
            print(f"SKIPTURNS {9 - player}")


if __name__ == "__main__":
    main()
