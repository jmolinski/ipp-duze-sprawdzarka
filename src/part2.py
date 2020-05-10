import sys
from typing import List, Optional
import part1



WHITESPACES = "\t \v\f\r"

def isspace(s: str) -> bool:
    return all(map(lambda c: c in WHITESPACES, s))


MAX_UINT32 = 2 ** 32 - 1

COMMAND_ARGS = {"B": 4, "I": 4, "m": 3, "g": 3, "b": 1, "f": 1, "q": 1, "p": 0}

"""usage: cat test.in | python part2.py 1>output.out 2>output.err"""

board: Optional[part1.Gamma] = None


def parse_unsigned_ints(string: str, expected: int) -> Optional[List[int]]:
    for c in string:
        if not isspace(c) and not c.isdigit():
            return None

    try:
        elements = [int(stripped) for k in string.split() if (stripped := k.strip())]
    except ValueError:
        return None

    if len(elements) != expected or any(k > MAX_UINT32 for k in elements):
        return None

    return elements


def run_batch_mode_command(command: str, raw_args: str, line: int) -> None:
    if command not in "mgfbqp":
        print(f"ERROR {line}", file=sys.stderr)
        return

    args = parse_unsigned_ints(raw_args, expected=COMMAND_ARGS[command])
    if args is None:
        print(f"ERROR {line}", file=sys.stderr)
        return

    assert board is not None
    if command == "m":
        # manual unpack to not fuck up mypy with default arg handler
        print(int(part1.gamma_move(board, args[0], args[1], args[2])))
    if command == "g":
        print(int(part1.gamma_golden_move(board, *args)))
    if command == "f":
        print(part1.gamma_free_fields(board, *args))
    if command == "b":
        print(part1.gamma_busy_fields(board, *args))
    if command == "q":
        print(int(part1.gamma_golden_possible(board, *args)))
    if command == "p":
        print(part1.gamma_board(board), end="")


def run_start_game_command(command: str, raw_args: str, line: int) -> None:
    global board
    if board is None and command == "I":
        raise NotImplemented("interactive mode is not supported")
    elif board is None and command == "B":
        args = parse_unsigned_ints(raw_args, expected=COMMAND_ARGS[command])
        if args is None:
            print(f"ERROR {line}", file=sys.stderr)
            return
        board = part1.gamma_new(*args)
        print("OK", line)

    if board is None:
        print(f"ERROR {line}", file=sys.stderr)
        return


def run_command(statement: str, line: int) -> bool:
    global board
    command, raw_args = statement[0], statement[1:]
    if raw_args and not isspace(raw_args[0]):
        print(f"ERROR {line}", file=sys.stderr)
        return False
    if board is None:
        run_start_game_command(command, raw_args, line)
    else:
        run_batch_mode_command(command, raw_args, line)

    return False


def main() -> None:
    statements = sys.stdin.read()
    split_statements = statements.split("\n")

    for line, statement in enumerate(split_statements, start=1):
        if line == len(split_statements):
            if statement != "":
                print(f"ERROR {line}", file=sys.stderr)
        elif statement == "" or statement[0] == "#":
            pass
        else:
            end_game = run_command(statement, line)
            if end_game:
                return


if __name__ == "__main__":
    main()
