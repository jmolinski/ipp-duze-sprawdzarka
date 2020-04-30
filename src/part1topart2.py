# type: ignore

from __future__ import annotations

import sys

from typing import Any, List

"""
Testy w stylu part1 moga zostac skonwertowane tym skryptem na wersje
dzialajaca z part2 batch mode;
skrypt na wejsciu bierze sciezke do pliku {nazwa_testu}.py, a na stdout
wypluwa ten test skonwertowany na LISTE POLECEN w formacie pliku .in
batch mode.
Nastepnie ta zwrotka moze zostac przepuszczona przez part2.py 
aby wyprodukowac pliki .out i .err

Usage: python part1topart2.py sciezka/do/testu.py > test.in
"""

STATEMENTS: List[str] = []


def gamma_new(width: int, height: int, players: int, areas: int) -> None:
    STATEMENTS.append(f"B {width} {height} {players} {areas}")


def gamma_delete(*args: Any) -> None:
    STATEMENTS.append("")


def gamma_move(g: Any, player: int, x: int, y: int, *args: Any) -> None:
    STATEMENTS.append(f"m {player} {x} {y}")


def gamma_golden_move(g: Any, player: int, x: int, y: int, *args: Any) -> None:
    STATEMENTS.append(f"g {player} {x} {y}")


def gamma_busy_fields(g: Any, player: int) -> None:
    STATEMENTS.append(f"b {player}")


def gamma_free_fields(g: Any, player: Any) -> None:
    STATEMENTS.append(f"f {player}")


def gamma_golden_possible(g: Any, player: Any) -> None:
    STATEMENTS.append(f"q {player}")


def gamma_board(g: Any) -> None:
    STATEMENTS.append("p")


def main() -> None:
    import part1

    part1.gamma_new = gamma_new
    part1.gamma_delete = gamma_delete
    part1.gamma_move = gamma_move
    part1.gamma_golden_move = gamma_golden_move
    part1.gamma_busy_fields = gamma_busy_fields
    part1.gamma_free_fields = gamma_free_fields
    part1.gamma_golden_possible = gamma_golden_possible
    part1.gamma_board = gamma_board

    try:
        path_to_test = sys.argv[1]
    except IndexError:
        exit(
            "sprawdz path do testu "
            "usage python skrypt.py sciezka/do/testu.py > test.in"
        )
    else:
        with open(path_to_test) as f:
            test = f.read().replace("assert ", "")

        exec(test)

        print(*STATEMENTS, sep="\n")


if __name__ == "__main__":
    main()
