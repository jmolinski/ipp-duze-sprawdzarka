import sys

from typing import List, Optional

from part1tovm import PlayerPointer
from part1 import Gamma, gamma_board, gamma_golden_move, gamma_move, gamma_new


class Interpreter:
    x: int = 0
    y: int = 0
    g: Optional[Gamma] = None
    player: Optional[PlayerPointer] = None

    def react_to_array_key(self, direction: str) -> None:
        vectors = {"DOWN": (0, -1), "UP": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
        dx, dy = vectors[direction]
        x, y = self.x + dx, self.y + dy

        assert self.g is not None
        if x < 0 or y < 0 or x >= self.g.board.width or y >= self.g.board.height:
            exit("Wyjscie strzalka poza plansze, zagrozenie kompatybilnosci")

        self.x, self.y = x, y

    def run_statement(self, s: str) -> bool:
        tokens = [t.strip() for t in s.split()]
        cmd = tokens[0]

        if cmd == "START":
            self.g = gamma_new(*map(int, tokens[1:]))
            assert self.g is not None
            self.player = PlayerPointer(game=self.g)

        assert self.g is not None
        assert self.player is not None
        if cmd == "GOTO":
            self.x, self.y = map(int, tokens[1:])
        if cmd == "END":
            return False
        if cmd == "MOVE":
            ret = gamma_move(self.g, self.player.current, self.x, self.y)
            if ret:
                self.player.advance()
        if cmd == "GOLDEN":
            ret = gamma_golden_move(self.g, self.player.current, self.x, self.y)
            if ret:
                self.player.advance()
        if cmd == "SKIPTURN":
            self.player.advance()
        if cmd == "SKIPTURNS":
            for _ in range(int(tokens[1])):
                self.player.advance()
        if cmd in {"UP", "DOWN", "LEFT", "RIGHT"}:
            self.react_to_array_key(cmd)

        return True

    def run(self, statements: List[str]) -> None:
        for s in statements:
            ret = self.run_statement(s)
            if not ret:
                break


def main() -> None:
    statements = sys.stdin.read().splitlines()
    statements = [s.strip() for s in statements if s.strip() and s[0] != "#"]
    interpreter = Interpreter()
    interpreter.run(statements)
    assert interpreter.g is not None
    print(gamma_board(interpreter.g), end="")


if __name__ == "__main__":
    main()
