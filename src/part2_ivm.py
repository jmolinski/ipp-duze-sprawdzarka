import enum
import itertools
import sys
import time

from dataclasses import dataclass
from typing import Final, Iterable, List, Sequence, Tuple

__doc__ = """
Ten plik zawiera kompilator jezyka wysokiego poziomu
do kodow obslugiwanych przez implementacje w c
oraz implementacje interpretera
wspierane polecenia:

START szerokosc wysokosc graczy obszarow
MOVE
GOLDEN
SKIPTURN
SKIPTURNS ile_razy

GOTO kolumna wiersz
UP
DOWN
RIGHT
LEFT

SETWAIT float_czas_pomiedzy_ruchami
END

END powoduje wyslanie sygnalu EOF (nie jest wymagany!)
UP/DOWN/RIGHT/LEFT moga powodowac problemy z przenosnoscia
(a raczej: moga byc trudne do zrozumienia) kiedy wykonywane
sa na granicach planszy. Jezeli chcesz zeby twoj skrypt byl 
przenosny bezpieczniej jest uzywac instrukcji GOTO, w 
przeciwnym wypadku musisz uwazac zeby nie "uderzac w sciane".

wiersze puste i rozpoczynajace sie od # sa ignorowane

Skrypt przyjmuje dodatkowe opcje konfiguracyjne:
--compile-only   wypisuje skompilowane instrukcje i konczy dzialanie 
--nowait         wylacza wszystkie instrukcje wait
--debug          wyswietla dodatkowe informacje pomocne przy debuggowaniu

UWAGA!
KAZDA GRA POWINNA ZACZYNAC SIE (po START) OD
GOTO 0 0
ABY BYLA PRZENOSNA - ROZNE IMPLEMENTACJE MOGA STARTOWAC Z ROZNYCH POZYCJI!

UWAGA!
Dzialanie interpretera jest customizowalne.
Mozna latwo zmodyfikowac (i nalezy przynajmniej zweryfikowac czy 
default jest poprawny czy nie - jest on poprawny dla mojej 
implementacji [jakub molinski here]) 2 rzeczy:
1. Na jakiej pozycji rozpoczyna sie gra - metoda _get_starting_position
2. Jak dzialaja ruchy strzalkami - metoda _move_cursor
Maja one opisy jak dzialaja i co maja dokladnie robic zeby smigalo.
Jezeli je modyfikujesz dobrze jest na koniec odpalic mypy, zeby sprawdzic,
czy typy danych sie zgadzaja.

Czy zmodyfikujesz interpreter/kompilator w inny sposob zalezy od ciebie,
nie oczekuj pomocy, you're on your own.

Wersja 2020.05.02.22.48
Wersja pythona 3.8, nie gwarantuje dzialania na starszych wersjach

Licencja WTFPL
https://en.wikipedia.org/wiki/WTFPL
+ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED
"""


class Direction(enum.Enum):
    UP = "UP"
    DOWN = "DOWN"
    RIGHT = "RIGHT"
    LEFT = "LEFT"


class InstructionType(enum.Enum):
    WAIT = enum.auto()
    VERBATIM = enum.auto()
    NOOP = enum.auto()


@dataclass()
class CompiledInstruction:
    op: InstructionType
    text: bytes = bytes()
    wait_time: float = float()


class Compiler:
    """
    Jezeli chcesz modyfikowac te klasa (wedlug instrukcji zmieniajac na
    przyklad metody _get_starting_position i _move_cursor), najlepiej
    zrobic klase ktora dziedziczy po Compiler i nadpisac globalna
    zmienna DefaultCompiler

    class MyCompiler(Compiler):
        def move_cursor(self, direction: Direction) -> None:
            ...

    DefaultCompiler = MyCompiler
    """

    x: int
    y: int
    width: int
    height: int
    players: int
    areas: int
    wait_time: float
    initialized: bool = False
    default_wait_time: Final[float] = 0.01
    debug: bool = False

    def __init__(self, debug: bool = False) -> None:
        self.x, self.y = 0, 0
        self.wait_time = 0.01
        self.width = self.height = self.players = self.areas = 0
        self.initialized = False
        self.debug = debug

    @staticmethod
    def _get_starting_position(
        width: int, height: int, players: int, areas: int
    ) -> Tuple[int, int]:
        """Ta funkcja przyjmuje jako argumenty wartosci z komendy START,
        czyli te same argumenty ktore przyjmuje gamma_new.
        Musi zwrocic pare liczb calkowitych x, y.
        (x, y) to koordynaty kursora [pola na planszy, nie znaku w buforze
        terminala! gdy rozpoczyna sie interactive mode].
        x to kolumna pola na ktore wskazuje kursor, a y to wiersz.
        Jezeli na poczatku kursor wskazuje na left-bottom rog to zwracasz
        0, 0; jezeli wskazuje na left-top to zwracasz (0, height - 1) itp.
        Jezeli wskazuje gdzies na srodek - musisz wyliczyc na podstawie
        argumentow pozycje tego pola.
        """
        return 0, 0

    def _move_cursor(self, direction: Direction) -> None:
        """Ta funkcja przesuwa kursor na inne pole, zgodnie z kierunkiem
        oznaczajacym ktora strzalka ma zostac zasymulowana. Domyslna
        implementacja odpowiada implementacji ze 'sztywnymi scianami',
        czyli kiedy po dotarciu do sciany proba przesuniecia sie za nia
        jest ignorowana. Jezeli chcesz zeby zamiast tego na przyklad
        kursor zostal przeteleportowany na druga strone planszy,
        musisz zmodyfikowac te metode.
        argument direction to enum klasy Direction
        pozycje kursora modyfikuje sie zmieniajac wartosci przypisane
        do nazw self.x, self.y - x oznacza kolumne, y wiersz.
        self.width i self.height oznaczaja odpowiednio szerokosc i
        wysokosc planszy. Nie modyfikuj tych wartosci.
        Metoda niczego nie zwraca.
        """
        if direction == Direction.UP:
            if self.y < self.height - 1:
                self.y += 1
        elif direction == Direction.DOWN:
            if self.y > 0:
                self.y -= 1
        elif direction == Direction.RIGHT:
            if self.x < self.width - 1:
                self.x += 1
        elif direction == Direction.LEFT:
            if self.x > 0:
                self.x -= 1

    def _compile_start_instruction(self, args: Sequence[str]) -> CompiledInstruction:
        self.width, self.height, self.players, self.areas = map(int, args)
        self.x, self.y = self._get_starting_position(
            self.width, self.height, self.players, self.areas
        )
        self.initialized = True

        return CompiledInstruction(
            op=InstructionType.VERBATIM, text=f"I {' '.join(args)}\n".encode("ASCII"),
        )

    def _compile_goto(self, column: int, row: int) -> List[CompiledInstruction]:
        if column >= self.width or row >= self.height:
            raise ValueError(f"GOTO outside board: {column} {row}")

        instructions: List[CompiledInstruction] = []

        while self.x < column:
            instructions.append(self._compile_arrow_move(Direction.RIGHT))
        while self.x > column:
            instructions.append(self._compile_arrow_move(Direction.LEFT))
        while self.y < row:
            instructions.append(self._compile_arrow_move(Direction.UP))
        while self.y > row:
            instructions.append(self._compile_arrow_move(Direction.DOWN))

        if not instructions:  # already there
            return [CompiledInstruction(op=InstructionType.NOOP)]
        return instructions

    def _compile_arrow_move(self, direction: Direction) -> CompiledInstruction:
        code = {
            Direction.UP: 65,
            Direction.DOWN: 66,
            Direction.RIGHT: 67,
            Direction.LEFT: 68,
        }

        if self.debug:
            print(direction)
            print(self.x, self.y)

        self._move_cursor(direction)

        if self.debug:
            print(self.x, self.y)

        return CompiledInstruction(
            op=InstructionType.VERBATIM, text=bytes([27, 91, code[direction]])
        )

    def _compile_user_move(self, statement: str) -> CompiledInstruction:
        code = {"MOVE": b" ", "GOLDEN": b"G"}
        return CompiledInstruction(op=InstructionType.VERBATIM, text=code[statement])

    def _compile_skip_turns(self, statement: str, *args: str) -> CompiledInstruction:
        times = 1 if statement == "SKIPTURN" else int(args[0])
        return CompiledInstruction(op=InstructionType.VERBATIM, text=b"C" * times)

    def _compile_statement(
        self, statement: str, *args: str
    ) -> List[CompiledInstruction]:
        compiled: List[CompiledInstruction] = []

        if statement == "START":
            if self.initialized:
                raise ValueError("Duplicate START instruction")
            compiled.append(self._compile_start_instruction(args))
        if not self.initialized:
            raise ValueError("Code must start with a START instruction")

        if statement == "END":
            return []
        if statement == "SETWAIT":
            self.wait_time = float(args[0])
            return [CompiledInstruction(op=InstructionType.NOOP)]
        if statement in {"SKIPTURNS", "SKIPTURN"}:
            compiled.append(self._compile_skip_turns(statement, *args))
        if statement in {"MOVE", "GOLDEN"}:
            compiled.append(self._compile_user_move(statement))
        if statement == "GOTO":
            compiled.extend(self._compile_goto(int(args[0]), int(args[1])))
        if statement in {"UP", "DOWN", "LEFT", "RIGHT"}:
            compiled.append(self._compile_arrow_move(Direction(statement)))

        if not compiled:
            raise ValueError(f"Invalid instruction: {statement}")

        if self.wait_time:
            compiled.append(
                CompiledInstruction(op=InstructionType.WAIT, wait_time=self.wait_time)
            )

        return compiled

    def compile(self, raw_input: str) -> Iterable[CompiledInstruction]:
        self.wait_time = self.default_wait_time
        self.initialized = False

        statements = (
            map(str.strip, stripped.split())
            for line in raw_input.splitlines()
            if (stripped := line.strip()) and stripped[0] != "#"
        )

        compiled_statements = itertools.chain.from_iterable(
            itertools.takewhile(bool, (self._compile_statement(*s) for s in statements))
        )

        return filter(lambda c: c.op != InstructionType.NOOP, compiled_statements)


DefaultCompiler = Compiler


class Interpreter:
    no_wait: bool

    def __init__(self, no_wait: bool = False) -> None:
        self.no_wait = no_wait

    def _run_instruction(self, instruction: CompiledInstruction) -> None:
        if instruction.op == InstructionType.VERBATIM:
            sys.stdout.buffer.write(instruction.text)
            sys.stdout.flush()
        if instruction.op == InstructionType.WAIT:
            if not self.no_wait:
                time.sleep(instruction.wait_time)

    def run(self, instructions: Iterable[CompiledInstruction]) -> None:
        for instruction in instructions:
            self._run_instruction(instruction)

        end_of_transmission = 4
        self._run_instruction(
            CompiledInstruction(
                op=InstructionType.VERBATIM, text=bytes([end_of_transmission])
            )
        )


def main(debug: bool, no_wait: bool, compile_only: bool) -> None:
    raw_input = sys.stdin.read()
    if compile_only:
        print(*Compiler(debug=debug).compile(raw_input), sep="\n", flush=True)
        exit(0)

    Interpreter(no_wait=no_wait).run(DefaultCompiler(debug=debug).compile(raw_input))


if __name__ == "__main__":
    if len(sys.argv) > 1 and any("help" in p.lower() for p in sys.argv[1:]):
        print(__doc__)
        exit(0)

    no_wait = len(sys.argv) > 1 and any("nowait" in p.lower() for p in sys.argv[1:])
    debug = len(sys.argv) > 1 and any("debug" in p.lower() for p in sys.argv[1:])
    compile_only = len(sys.argv) > 1 and any(
        "compile-only" in p.lower() for p in sys.argv[1:]
    )

    main(debug, no_wait, compile_only)
