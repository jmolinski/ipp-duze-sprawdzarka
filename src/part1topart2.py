# type: ignore

from __future__ import annotations

import random
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


def make_random_spacing(threshold: float = 0.1) -> str:
    length = random.choice(range(1, 8)) if threshold > 0 else 1
    crazy = random.random() < threshold
    if crazy:
        length = random.choice(range(5, 15))
        characters = "\t \v\f\r"
    else:
        if threshold == 0:
            characters = " "
        else:
            characters = " \t"
    return "".join(random.choices(characters, k=length))


def obfuscate_line(line: str) -> str:
    cmd = line[0]
    args = [int(a) for a in line[1:].split()]

    if random.random() < 0.9:
        # większość linijek powinna pozostać bez zmian
        return line

    if random.random() < 0.1:  # slightly change arg value
        if args:
            position = random.randrange(len(args))
            args[position] += random.randint(-10, 10)

    if random.random() < 0.1:  # set small random arg value
        if args:
            position = random.randrange(len(args))
            args[position] = random.randint(-10, 10)

    if random.random() < 0.1:  # set gigantic random arg value
        if args:
            position = random.randrange(len(args))
            args[position] = random.randint(-(2 ** 4096), 2 ** 4096)

    obfuscated = list(cmd + "".join(str(a) for a in args))

    if random.random() < 0.1:  # remove char
        obfuscated.pop(len(obfuscated) - 1)

    if random.random() < 0.1:  # insert string
        for _ in range(random.randrange(1, 4)):
            rand_code = random.randint(0, 255)
            obfuscated.insert(random.randrange(len(obfuscated)), chr(rand_code))

    if random.random() < 0.1:  # swap
        p, q = random.randrange(len(obfuscated)), random.randrange(len(obfuscated))
        obfuscated[p], obfuscated[q] = obfuscated[q], obfuscated[p]

    if random.random() < 0.2:  # spacing
        random_spacing = make_random_spacing()
        obfuscated_line = random_spacing.join(obfuscated)
    else:
        obfuscated_line = "".join(obfuscated)

    if cmd in "IB":
        # jeśli linijka była prawidłowa, nie ma już po niej raczej prawidłowych polecen I/B
        # zatem aby reszta testu się wykonała poprawnie, gra musi zostać jednak utworzona
        return obfuscated_line + line

    return obfuscated_line


def main() -> None:
    obfuscate = len(sys.argv) > 1 and any(
        "obfuscate" in p.lower() for p in sys.argv[1:]
    )

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

        global STATEMENTS
        STATEMENTS.clear()
        exec(test)

        if obfuscate:
            STATEMENTS = [obfuscate_line(s) for s in STATEMENTS]

        print(*STATEMENTS, sep="\n")


if __name__ == "__main__":
    main()
