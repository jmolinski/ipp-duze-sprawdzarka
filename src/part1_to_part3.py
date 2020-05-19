# type: ignore

from __future__ import annotations

import re
import sys
from typing import Any, List

"""
Najpierw conwersja c -> py convert_to_py.
"""

STATEMENTS: List[str] = []

correct_golden_possible: Any


def gamma_golden_possible(g: Any, player: Any) -> Any:
    res = int(correct_golden_possible(g, player))
    STATEMENTS.append(f"assert(gamma_golden_possible({{}}, {player}) == {res});")


def main() -> None:
    import part1
    global correct_golden_possible
    correct_golden_possible = part1.gamma_golden_possible
    part1.gamma_golden_possible = gamma_golden_possible

    try:
        path_to_test = sys.argv[1]
        path_to_test_c = sys.argv[2]
    except IndexError:
        exit(
            "sprawdz path do testu "
            "usage python skrypt.py sciezka/do/testu.py sciezka/do/testu.c> test.c"
        )
    else:
        with open(path_to_test) as f:
            test = f.read().replace("assert ", "")
        with open(path_to_test_c) as f:
            c_test = f.read()
        if not re.findall(r"gamma_golden_possible", c_test):
            print(c_test)
            return
        global STATEMENTS
        STATEMENTS.clear()
        exec(test)
        i = 0
        with open(path_to_test_c) as f:
            for line in f.readlines():
                if re.findall(r"gamma_golden_possible", line):
                    name = re.findall(r"(?<=gamma_golden_possible\()\w+", line)[0]
                    print(STATEMENTS[i].format(name))
                    i += 1
                else:
                    print(line)


if __name__ == "__main__":
    main()
