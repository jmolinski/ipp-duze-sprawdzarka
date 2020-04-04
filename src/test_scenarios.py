import random

from typing import Any, Dict

from part1 import (
    gamma_busy_fields,
    gamma_free_fields,
    gamma_golden_possible,
    gamma_move,
)
from test_tools import (
    ScenarioType,
    StatementStoreType,
    assert_call,
    cycle_players,
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
        x, y = random.randint(0, 9), random.randint(0, 9)
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


def test_check_busy_fields(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "busy_fields, with collisions, many players, unlimited areas"
    store(make_comment(doc))

    board = make_board(store, 7, 13, 3, 100)

    for _ in range(7 * 13):
        x, y = random.randint(0, 6), random.randint(0, 12)
        player = random.randint(1, 3)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_busy_fields, board, player))

    delete_board(store, board)


def fill_board_with_areas_limit(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move, with collisions, many players, limited areas"
    store(make_comment(doc))

    board = make_board(store, 5, 5, 3, 4)

    for player in cycle_players(players=3, take=5 * 5 * 3):
        x, y = random.randint(0, 4), random.randint(0, 4)
        store(assert_call(gamma_move, board, player, x, y))

    delete_board(store, board)


def test_free_fields(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "free_fields, with collisions, many players, limited areas"
    store(make_comment(doc))

    board = make_board(store, 8, 8, 5, 8)

    for player in cycle_players(players=5, take=8 * 8 * 2):
        x, y = random.randint(0, 4), random.randint(0, 4)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_busy_fields, board, player))
        store(assert_call(gamma_free_fields, board, player))

    delete_board(store, board)


def test_golden_possible(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "golden_possible, limited areas"
    store(make_comment(doc))

    board = make_board(store, 4, 4, 8, 3)

    for player in cycle_players(players=8, take=4 * 4):
        x, y = random.randint(0, 4), random.randint(0, 4)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_golden_possible, board, player))

    delete_board(store, board)


scenarios: Dict[str, ScenarioType] = {
    "fill_board_with_collisions": fill_board_with_collisions,
    "fill_board_without_collisions": fill_board_without_collisions,
    "test_check_busy_fields": test_check_busy_fields,
    "fill_board_with_areas_limit": fill_board_with_areas_limit,
    "test_free_fields": test_free_fields,
    "test_golden_possible": test_golden_possible,
}


__all__ = ["scenarios"]
