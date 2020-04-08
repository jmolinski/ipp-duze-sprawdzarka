from __future__ import annotations

from typing import Dict, Mapping, MutableMapping, cast

from gamma.board_defaultdict import make_empty_board
from gamma.group_areas import ListOfAreas, group_areas_by_player


class Board:
    board: Mapping[int, MutableMapping[int, int]]

    FREE_FIELD = -1

    def __init__(self, width: int, height: int) -> None:
        if width * height > 1000 * 1000:
            raise ValueError("max supported board size is 1,000,000 fields")

        self.width = width
        self.height = height

        self.board = make_empty_board(width, height, self.FREE_FIELD)

    def print(self) -> str:
        def print_player(p: int) -> str:
            return str(p) if p < 10 else f"[{p}]"

        def row_to_string(row: Dict[int, int]) -> str:
            r = ""
            for i in range(self.width):
                player = row.get(i, -1)
                if player == -1:
                    r += "."
                else:
                    r += print_player(player)

            return r + "\n"

        rows = [
            row_to_string(cast(Dict[int, int], self.board[i]))
            for i in range(self.height)
        ]
        return "".join(reversed(rows))

    def get_grouped_areas(self) -> Dict[int, ListOfAreas]:
        return group_areas_by_player(self.board, self.width, self.height)
