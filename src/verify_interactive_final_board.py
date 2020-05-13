import re
import sys


def normalize_pyte(raw_result: str) -> str:
    """ta metoda normalizacji używa emulatora terminala
    do wyrenderowania finalnej planszy
    wymaga zainstalowania paczki `pyte` z pip

    pyte nie wzpiera następujących ansi escape codes:
    Esc[s -- save cursor position
    Esc[u -- restore cursor position
    """
    import pyte

    screen = pyte.Screen(100, 30)
    stream = pyte.Stream(screen)
    stream.feed(raw_result)
    return "\n".join(map(str.strip, screen.display))


def normalize_naive(raw_result: str) -> str:
    """ta metoda normalizacji używa bardzo naiwnej metody
    usuwaia części ansi escape codes, bardzo duża szansa
    na false-negative; warto ewentualnie uzupełnić o dodatkowe
    potrzebne kody"""
    return (
        raw_result.encode("ASCII")
        .replace(b"\33[0m", b"")
        .replace(b"\33[?25h", b"")
        .replace(b"\33[2j", b"")
        .replace(b"\33[H", b"")
        .replace(b"\33[30;47m", b"")
        .replace(b"\33[K", b"")
        .replace(b"\33[7m", b"")
        .replace(b"\33[0m", b"")
        .decode("ASCII")
    )


def verify_board(raw_result: str, expected_board: str) -> bool:
    """raw result to output gamma, expected board to oczekiwana
    plansza na koniec dzialania programu; jezeli uzywasz jakiejs
    biblioteki do obslugi terminala albo rysujesz ramki itp
    to musisz zmodyfikowac te metoda tak, zeby sobie z tym poradzila
    Zwraca True jezeli wynik jest prawidlowy, wpp False

    przeprowadza normalizacje danych z gammy albo w sposob naiwny
    przez zastepowanie kodow, albo semi-inteligentnie renderujac
    caly output do finalnej postaci uzywajac emulatora terminala
    pyte -- domyslnie uzywana jest opcja naiwna
    """

    use_pyte = False

    if use_pyte:
        normalized_data = normalize_pyte(raw_result)
    else:
        normalized_data = normalize_naive(raw_result)

    matched = re.findall(r"(([\.\d]+\n)+)", normalized_data)
    try:
        final_board = [f for (f, s) in matched if f.count("\n") > 1][-1]
    except IndexError:
        print("Nie znaleziono zadnej planszy; niepoprawna normalizacja danych")
        sys.exit(2)
    else:
        return expected_board in final_board


def main(result_path: str, expected_path: str) -> int:
    with open(result_path) as f:
        result = f.read()
    with open(expected_path) as f:
        expected_board = f.read()

    return int(not verify_board(result, expected_board))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        exit("Usage: python script.py gamma_output.file expected_output.file")

    sys.exit(main(args[0], args[1]))
