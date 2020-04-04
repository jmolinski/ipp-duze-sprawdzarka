import random

from typing import Callable

from part1 import gamma_delete, gamma_move, gamma_new
from test_tools import (
    EMPTY_LINE,
    PyCVariants,
    assert_call,
    assign_call,
    make_assert,
    make_comment,
    native_call,
)

__all__ = ["scenario1"]


def scenario1(store: Callable[[PyCVariants], None]) -> None:
    store(
        make_comment("prosty test, tylko gamma_move, zapelnianie planszy z kolizjami")
    )
    statements, board = assign_call(
        gamma_new, None, 5, 5, 1, 100, c_type="gamma_t*", var_name="board"
    )
    store(statements)
    store(make_assert("board", assert_type="isnotnull"))
    store(EMPTY_LINE)

    for _ in range(35):
        player = random.randint(1, 9)
        x, y = random.randint(0, 10), random.randint(0, 10)
        store(assert_call(gamma_move, board, player, x, y))

    store(EMPTY_LINE)
    store(native_call(gamma_delete, board))
