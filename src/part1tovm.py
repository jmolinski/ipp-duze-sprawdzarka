from __future__ import annotations

import sys

from typing import Any, Dict, List, Optional, cast

import part1

"""
Testy w stylu part1 moga zostac skonwertowane tym skryptem na wersje
dzialajaca z part2 interactive mode;
skrypt na wejsciu bierze sciezke do pliku {nazwa_testu}.py, a na stdout
wypluwa ten test skonwertowany na LISTE POLECEN w formacie 
jezyka interpretera interactive mode.

Usage: python part1tovm.py sciezka/do/testu.py > test.ivml
"""

original_gamma_new = part1.gamma_new
original_gamma_move = part1.gamma_move
original_gamma_golden_move = part1.gamma_golden_move


class PlayerPointer:
    current: int
    game: Optional[part1.Gamma]

    def __init__(self, start: int = 1, game: Optional[part1.Gamma] = None) -> None:
        self.current = start
        self.game = game

    def reset(self) -> None:
        self.current = 1

    def set_game(self, game: Optional[part1.Gamma]) -> None:
        self.game = game

    @property
    def value(self) -> int:
        return self.current

    def can_move(self, player: int) -> bool:
        assert self.game is not None
        return part1.gamma_free_fields(
            self.game, player
        ) != 0 or part1.gamma_golden_possible(self.game, player)

    def advance(self) -> bool:
        """Przesuwa numer na nastepnego gracza"""
        assert self.game is not None
        players = self.game.players
        next_player = (self.current % players) + 1
        next_player_guard = next_player

        if self.can_move(next_player):
            self.current = next_player
            return True

        while True:
            next_player = (next_player % players) + 1
            if self.can_move(next_player):
                self.current = next_player
                return True

            if next_player == next_player_guard:
                break

        return False

    def count_skips_to_player(self, player: int) -> Optional[int]:
        """Zwraca ile razy trzeba zrobic SKIPTURN zeby dojsc do tego gracza"""
        assert self.game is not None
        simulation = PlayerPointer(self.current, self.game)
        max_skips = self.game.players + 2  # nie wiem czy +0 czy +1 wiec +2...
        skips = 0

        while simulation.current != player:
            simulation.advance()
            skips += 1

            if skips > max_skips:
                return None

        return skips


CURRENT_PLAYER = PlayerPointer()
STATEMENTS: List[str] = []
DEFAULT_WAIT_TIME = 0.25


def skip_turns(to_skip: int) -> None:
    if to_skip:
        STATEMENTS.append("SETWAIT 0")
        STATEMENTS.append(f"SKIPTURNS {to_skip}")
        for _ in range(to_skip):
            CURRENT_PLAYER.advance()
        STATEMENTS.append(f"SETWAIT {DEFAULT_WAIT_TIME}")


def gamma_new(
    width: int, height: int, players: int, areas: int
) -> Optional[part1.Gamma]:
    ret = original_gamma_new(width, height, players, areas)
    CURRENT_PLAYER.reset()
    CURRENT_PLAYER.set_game(ret)
    STATEMENTS.append(f"START {width} {height} {players} {areas}")
    STATEMENTS.append("GOTO 0 0")
    STATEMENTS.append("SETWAIT 0.25")
    return ret


def gamma_move(g: part1.Gamma, player: int, x: int, y: int, *args: Any) -> bool:
    ret = original_gamma_move(g, player, x, y)

    # the move may be outside of the board -- we should simply ignore it here
    if x < 0 or y < 0 or x >= g.board.width or y >= g.board.height:
        return ret

    STATEMENTS.append(f"GOTO {x} {y}")

    skips_needed = CURRENT_PLAYER.count_skips_to_player(player)
    if skips_needed is not None:
        skip_turns(skips_needed)

    STATEMENTS.append(f"MOVE")
    if ret:
        CURRENT_PLAYER.advance()

    return ret


def gamma_golden_move(g: part1.Gamma, player: int, x: int, y: int) -> bool:
    ret = original_gamma_golden_move(g, player, x, y)

    # the move may be outside of the board -- we should simply ignore it here
    if x < 0 or y < 0 or x >= g.board.width or y >= g.board.height:
        return ret

    STATEMENTS.append(f"GOTO {x} {y}")

    skips_needed = CURRENT_PLAYER.count_skips_to_player(player)
    if skips_needed is not None:
        skip_turns(skips_needed)

    # todo jak z tym skipowaniem? golden_possible jest uszkodzone
    # wiec python zrobi ruch a interctive pominie
    # a na koniec bedzie mismatch?
    # na teraz takie rozwiazanie:
    if skips_needed is None and ret:  # czyli python umie, a interactive nie
        exit("Can't perform this gamma move in interactive mode!")

    STATEMENTS.append(f"GOLDEN")
    if ret:
        CURRENT_PLAYER.advance()

    return ret


def main() -> None:
    part1.gamma_new = gamma_new
    part1.gamma_move = gamma_move
    part1.gamma_golden_move = gamma_golden_move
    # we don't want to delete board after the test
    # because we may need to read some metadata from it
    part1.gamma_delete = lambda a: None

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

        STATEMENTS.clear()
        CURRENT_PLAYER.reset()

        context: Dict[str, Any] = {}
        exec(test, context, context)  # to zdefiniuje board w context
        # bez tego przypisania edytor i mypy
        # nie widzi nazwy board - bo jest tworzona dynamicznie w ctx
        board = cast(part1.Gamma, context["board"])
        assert board is not None

        if len(sys.argv) > 2 and "--test" in sys.argv:
            # output expected final board
            print(part1.gamma_board(board), end="")
        else:  # normal -- compile
            print(*STATEMENTS, sep="\n")


if __name__ == "__main__":
    main()
