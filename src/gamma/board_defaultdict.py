from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Mapping, MutableMapping, cast


class BoardDefaultRowCol(defaultdict):
    min_key: int
    max_key: int
    save: bool

    def set_boundaries(self, lower: int, upper: int) -> None:
        self.min_key = lower
        self.max_key = upper

    def __missing__(self, key: int) -> int:
        if key > self.max_key or key < self.min_key or self.default_factory is None:
            raise KeyError()

        default_factory = cast(Callable[[], int], self.default_factory)

        if not self.save:
            return default_factory()

        self[key] = ret_val = default_factory()
        return ret_val


def make_empty_board(
    width: int, height: int, free_field: int
) -> Mapping[int, MutableMapping[int, int]]:
    def make_row() -> Mapping[int, int]:
        row = BoardDefaultRowCol(lambda: free_field)
        row.set_boundaries(0, width - 1)
        row.save = False
        return row

    board = BoardDefaultRowCol(make_row)
    board.set_boundaries(0, height - 1)
    board.save = True

    return board
