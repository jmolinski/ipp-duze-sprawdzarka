import random
import sys

from typing import Callable, List, Tuple

from part1 import gamma_delete, gamma_move, gamma_new
from test_tools import (
    EMPTY_LINE,
    PyCVariants,
    assert_call,
    assign_call,
    make_assert,
    make_statements_dispatcher,
    native_call,
)


def scenario1(store: Callable[[PyCVariants], None]) -> None:
    statements, board = assign_call(
        gamma_new, None, 10, 10, 9, 100, c_type="gamma_t*", var_name="board"
    )
    store(statements)
    store(make_assert("board", assert_type="isnotnull"))
    store(EMPTY_LINE)

    for _ in range(115):
        player = random.randint(1, 9)
        x, y = random.randint(0, 10), random.randint(0, 10)
        store(assert_call(gamma_move, board, player, x, y))

    store(EMPTY_LINE)
    store(native_call(gamma_delete, board))


def make_tests() -> Tuple[List[str], List[str]]:
    spython: List[str] = []
    sclang: List[str] = []
    store = make_statements_dispatcher(spython, sclang)

    scenario1(store)

    return sclang, spython


def main(output_file_name) -> None:
    with open("c_file_template", "r") as f:
        c_file_template = f.read()
    with open("py_file_template", "r") as f:
        py_file_template = f.read()

    c_statements, py_statements = make_tests()
    output_file_c = c_file_template.format("\n".join(c_statements))
    output_file_py = py_file_template.format("\n".join(py_statements))

    with open(output_file_name + ".c", "w") as f:
        f.write(output_file_c)

    with open(output_file_name + ".py", "w") as f:
        f.write(output_file_py)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "usage: python make_tests.py output_file\n"
            "[without extension, will generate output_file.c and output_file.py]"
        )
        sys.exit(1)

    main(sys.argv[1])
