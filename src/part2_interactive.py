import enum
import itertools

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

GOTO kolumna wiersz
UP
DOWN
RIGHT
LEFT

SETWAIT float_czas_pomiedzy_ruchami
END
READ

END powoduje wyslanie sygnalu EOF (nie jest wymagany!)
READ moze znajdowac sie tylko na koncu (inaczej UB)
READ powoduje wczytywanie polecen z stdin (bez weryfikacji!)

wiersze puste i rozpoczynajace sie od # sa ignorowane

UWAGA!
KAZDA GRA POWINNA ZACZYNAC SIE (po START) OD
GOTO 0 0
ABY BYLA PRZENOSNA - ROZNE IMPLEMENTACJE MOGA STARTOWAC Z ROZNYCH POZYCJI!

UWAGA!
Dzialanie interpretera jest customizowalne.
Mozna latwo zmodyfikowac (i nalezy przynajmniej zweryfikowac czy 
default jest poprawny czy nie - jest on poprawny dla mojej 
implementacji [jakub molinski here]) 2 rzeczy:
1. Na jakiej pozycji rozpoczyna sie gra - metoda get_starting_position
2. Jak dzialaja ruchy strzalkami - metoda move_cursor
Maja one opisy jak dzialaja i co maja dokladnie robic zeby smigalo.
Jezeli je modyfikujesz dobrze jest na koniec odpalic mypy, zeby sprawdzic,
czy typy danych sie zgadzaja.

Czy zmodyfikujesz interpreter/kompilator w inny sposob zalezy od ciebie,
nie oczekuj pomocy, you're on your own.

Wersja 0.1a
Wersja pythona 3.8, nie gwarantuje dzialania na starszych wersjach

Licencja WTFPL
https://en.wikipedia.org/wiki/WTFPL
+ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED
"""


class Direction(enum.Enum):
    UP = enum.auto()
    DOWN = enum.auto()
    RIGHT = enum.auto()
    LEFT = enum.auto()


class InstructionType(enum.Enum):
    WAIT = enum.auto()
    VERBATIM = enum.auto()
    END = enum.auto()
    READ = enum.auto()


@dataclass()
class CompiledInstruction:
    op: InstructionType
    text: bytes = bytes()
    wait_time: float = float()


class Compiler:
    """
    Jezeli chcesz modyfikowac te klasa (wedlug instrukcji zmieniajac na
    przyklad metody get_starting_position i move_cursor), najlepiej
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

    def __init__(self) -> None:
        self.x, self.y = 0, 0
        self.wait_time = 0.01
        self.width = self.height = self.players = self.areas = 0
        self.initialized = False

    @staticmethod
    def get_starting_position(
        width: int, height: int, players: int, areas: int
    ) -> Tuple[int, int]:
        """Ta funkcja przyjmuje jako argumenty wartosci z komendy START,
        czyli te same argumenty ktore przyjmuje gamma_new.
        Musi zwrocic pare liczb calkowitych x, y.
        (x, y) to koordynaty kursora gdy rozpoczyna sie interactive mode.
        x to kolumna pola na ktore wskazuje kursor, a y to wiersz.
        Jezeli na poczatku kursor wskazuje na lewy-dolny rog to zwracasz
        0, 0; jezeli wskazuje na left-top to zwracasz (0, height - 1) itp.
        Jezeli wskazuje gdzies na srodek - musisz wyliczyc na podstawie
        argumentow pozycje tego pola.
        """
        return 0, 0

    def move_cursor(self, direction: Direction) -> None:
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
                self.y -= 1
        elif direction == Direction.DOWN:
            if self.y > 0:
                self.y += 1
        elif direction == Direction.RIGHT:
            if self.x < self.width - 1:
                self.x += 1
        else:  # Direction.LEFT
            if self.x > 0:
                self.x -= 1

    def compile_start_instruction(self, args: Sequence[str]) -> CompiledInstruction:
        self.width, self.height, self.players, self.areas = map(int, args)
        self.x, self.y = self.get_starting_position(
            self.width, self.height, self.players, self.areas
        )
        self.initialized = True

        return CompiledInstruction(
            op=InstructionType.VERBATIM, text=f"I {' '.join(args)}\n".encode("ASCII"),
        )

    def compile_statement(
        self, statement: str, *args: str
    ) -> List[CompiledInstruction]:
        compiled: List[CompiledInstruction] = []

        if statement == "START":
            if self.initialized:
                raise ValueError("Duplicate START instruction")
            compiled.append(self.compile_start_instruction(args))
        if not self.initialized:
            raise ValueError("Code must start with a START instruction")

        if statement == "END":
            raise StopIteration()

        return compiled

    def compile(self, raw_input: str) -> Iterable[CompiledInstruction]:
        self.wait_time = self.default_wait_time
        self.initialized = False

        statements = (
            map(str.strip, stripped.split())
            for line in raw_input.splitlines()
            if (stripped := line.strip()) and stripped[0] != "#"
        )

        return itertools.chain.from_iterable(
            self.compile_statement(*s) for s in statements
        )


DefaultCompiler = Compiler


def main() -> None:
    pass


if __name__ == "__main__":
    main()
