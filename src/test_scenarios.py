import random

from typing import Any, Dict

from part1 import gamma_move
from test_tools import (
    EMPTY_LINE,
    ScenarioType,
    StatementStoreType,
    assert_call,
    delete_board,
    make_board,
    make_comment,
)


def fill_board_with_collisions(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move, fill board 1 player, unlimited areas"
    store(make_comment(doc))

    board = make_board(store, 10, 10, 3, 100)
    player = 2

    for _ in range(35):
        x, y = random.randint(0, 10), random.randint(0, 10)
        store(assert_call(gamma_move, board, player, x, y))

    delete_board(store, board)


def fill_board_without_collisions(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move, fill board no collisions, many players, unlimited areas"
    store(make_comment(doc))

    board = make_board(store, 10, 10, 30, 100)

    all_fields = [(x, y) for x in range(10) for y in range(10)]
    random.shuffle(all_fields)

    for (x, y) in all_fields:
        player = random.randint(1, 30)
        store(assert_call(gamma_move, board, player, x, y))

    delete_board(store, board)


scenarios: Dict[str, ScenarioType] = {
    "fill_board_with_collisions": fill_board_with_collisions,
    "fill_board_without_collisions": fill_board_without_collisions,
}


__all__ = ["scenarios"]
