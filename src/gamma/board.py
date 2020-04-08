from __future__ import annotations

from typing import Dict, List

from gamma.group_areas import ListOfAreas, group_areas_by_player


class Board:
    board: List[List[int]]

    FREE_FIELD = -1

    def __init__(self, width: int, height: int) -> None:
        if width * height > 1000 * 1000:
            raise ValueError("max supported board size is 1,000,000 fields")

        self.width = width
        self.height = height
        self.board = [[-1] * width for _ in range(height)]

    def print(self) -> str:
        def print_player(p: int) -> str:
            return str(p) if p < 10 else f"[{p}]"

        def row_to_string(row: List[int]) -> str:
            return "".join(["." if c == -1 else print_player(c) for c in row]) + "\n"

        return "".join(reversed(list(row_to_string(row) for row in self.board)))

    def get_grouped_areas(self) -> Dict[int, ListOfAreas]:
        return group_areas_by_player(self.board)
