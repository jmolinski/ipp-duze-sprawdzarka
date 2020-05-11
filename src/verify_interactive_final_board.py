import re
import sys


def verify_board(raw_result: str, expected_board: str) -> bool:
    """raw result to output gamma, expected board to oczekiwana
    plansza na koniec dzialania programu; jezeli uzywasz jakiejs
    biblioteki do obslugi terminala albo rysujesz ramki itp
    to musisz zmodyfikowac te metoda tak, zeby sobie z tym poradzila
    Zwraca True jezeli wynik jest prawidlowy, wpp False"""
    result = raw_result.encode("ASCII").replace(b"\33[0m", b"").decode("ASCII")
    final_board = re.findall(r"(([\.\d]+\n)+)", result)[-1][0]
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
