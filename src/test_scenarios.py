import itertools as it
import random
from typing import Any, Dict, List

from gamma.board import Board
from part1 import (
    gamma_busy_fields,
    gamma_free_fields,
    gamma_golden_move,
    gamma_golden_possible,
    gamma_move,
)
from test_tools import (
    EMPTY_LINE,
    Coords,
    ScenarioType,
    StatementStoreType,
    assert_board_equal,
    assert_call,
    cycle_players,
    delete_board,
    flatten,
    get_all_board_coords,
    get_coords_around,
    make_board,
    make_comment,
    unsafe_gamma_move,
)

FREE_FIELD = Board.FREE_FIELD


def fill_board_with_collisions(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move, fill board 1 player, unlimited areas"
    store(make_comment(doc))

    board = make_board(store, 10, 10, 3, 100)
    player = 2

    for _ in range(35):
        x, y = random.randint(0, 9), random.randint(0, 9)
        store(assert_call(gamma_move, board, player, x, y))

    delete_board(store, board)


def fill_board_without_collisions(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move, fill board no collisions, many players, unlimited areas"
    store(make_comment(doc))

    board = make_board(store, 10, 10, 30, 100)

    all_fields = [(x, y) for x in range(10) for y in range(10)]
    random.shuffle(all_fields)

    for (x, y) in all_fields:
        player = random.randint(1, 30)
        store(assert_call(gamma_move, board, player, x, y))

    delete_board(store, board)


def test_check_busy_fields(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "busy_fields, with collisions, many players, unlimited areas"
    store(make_comment(doc))

    board = make_board(store, 7, 13, 3, 100)

    for _ in range(7 * 13):
        x, y = random.randint(0, 6), random.randint(0, 12)
        player = random.randint(1, 3)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_busy_fields, board, player))

    delete_board(store, board)


def fill_board_with_areas_limit(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move, with collisions, many players, limited areas"
    store(make_comment(doc))

    board = make_board(store, 5, 5, 3, 4)

    for player in cycle_players(players=3, take=5 * 5 * 3):
        x, y = random.randint(0, 4), random.randint(0, 4)
        store(assert_call(gamma_move, board, player, x, y))

    if kwargs.get("print_board", False):
        assert_board_equal(store, board)

    delete_board(store, board)


def test_free_fields(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "free_fields, with collisions, many players, limited areas"
    store(make_comment(doc))

    board = make_board(store, 8, 8, 5, 8)

    for player in cycle_players(players=5, take=8 * 8 * 2):
        x, y = random.randint(0, 7), random.randint(0, 7)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_busy_fields, board, player))
        store(assert_call(gamma_free_fields, board, player))

    delete_board(store, board)


def test_golden_possible(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "golden_possible, limited areas"
    store(make_comment(doc))

    board = make_board(store, 4, 4, 8, 3)

    for player in cycle_players(players=8, take=4 * 4):
        x, y = random.randint(0, 3), random.randint(0, 3)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_golden_possible, board, player))

    delete_board(store, board)


def test_strip(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "board is either vertical or horizontal strip"
    store(make_comment(doc))

    max_size = int(kwargs.get("max_size", 64))
    players = int(kwargs.get("players", 8))
    areas = int(kwargs.get("areas", 4))
    chunk_size = int(kwargs.get("chunk_size", 32))
    tests = int(kwargs.get("tests", max_size * 4))

    width, height = 1, random.randint(1, max_size)
    if kwargs.get("horizontal", False):
        height, width = width, height

    board = make_board(store, width, height, players, areas)

    def run_checks_for_all_players() -> None:
        for p in range(1, players + 1):
            store(assert_call(gamma_golden_possible, board, p))
            store(assert_call(gamma_busy_fields, board, p))
            store(assert_call(gamma_free_fields, board, p))
            if random.randint(0, 100) < 10:
                store(
                    assert_call(
                        gamma_golden_move,
                        board,
                        player,
                        random.randint(0, width),
                        random.randint(0, height),
                    )
                )

    player_iterator = cycle_players(players=players, take=tests)
    for _ in range(round(tests / chunk_size)):
        for player in it.islice(player_iterator, chunk_size):
            x, y = random.randint(0, width), random.randint(0, height)
            store(assert_call(gamma_move, board, player, x, y))
        run_checks_for_all_players()

    delete_board(store, board)


def test_golden_move(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "golden_move, limited areas"
    store(make_comment(doc))

    players_n = 3
    board = make_board(store, 8, 8, players_n, 12)

    all_fields = get_all_board_coords(board)
    fields_to_fill = random.sample(all_fields, k=players_n * 10)

    player_fields: Dict[int, List[Coords]] = {}
    # each player picks 10 random fields
    for field, player in zip(
        fields_to_fill, cycle_players(players=players_n, take=1000)
    ):
        store(assert_call(gamma_move, board, player, *field))
        player_fields[player] = player_fields.get(player, []) + [field]

    players = list(range(1, players_n + 1))

    def can_move(p: int) -> bool:
        return bool(gamma_free_fields(board, p) or gamma_golden_possible(board, p))

    # this while can enter an infinite loop (golden_possible != golden_move)
    # so this needs to be guarded against -- thus max cycles limit
    for _ in range(25):  # max cycles
        if not any(can_move(p) for p in players):
            break

        store(EMPTY_LINE)

        for p in players:
            store(assert_call(gamma_free_fields, board, p))
            store(assert_call(gamma_busy_fields, board, p))
            store(assert_call(gamma_golden_possible, board, p))

            if gamma_free_fields(board, p):
                free_fields = list(flatten(board.board.get_grouped_areas()[FREE_FIELD]))
                field = random.choice(free_fields)
                store(assert_call(gamma_move, board, p, *field))
            else:  # gamma_golden_possible(board, p) == True
                other_player = random.choice(list(set(players) - {p}))
                field = player_fields[other_player].pop()
                store(assert_call(gamma_golden_move, board, p, *field))

    delete_board(store, board)


def test_many_boards(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move + gamma_board, a few boards at the same time"
    store(make_comment(doc))

    b1 = make_board(store, 4, 4, 4, 16, name="board1")
    b2 = make_board(store, 4, 4, 4, 16, name="board2")
    b3 = make_board(store, 4, 4, 4, 16, name="board3")

    for player in cycle_players(players=4, take=3 * 16):
        for board, name in [(b1, "board1"), (b2, "board2"), (b3, "board3")]:
            x, y = random.randint(0, 3), random.randint(0, 3)
            store(assert_call(gamma_move, board, player, x, y, board_name=name))
            if player == 1:
                assert_board_equal(store, board, board_name=name)

    delete_board(store, b1, board_name="board1")
    delete_board(store, b3, board_name="board3")
    delete_board(store, b2, board_name="board2")


def test_gamma_board(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_move + gamma_board"
    store(make_comment(doc))

    height, width = int(kwargs.get("height", 7)), int(kwargs.get("width", 7))
    moves = int(kwargs.get("moves", height * width))
    chunk_size = int(kwargs.get("chunk_size", 1))
    players, areas = int(kwargs.get("players", 5)), int(kwargs.get("areas", 9))
    board = make_board(store, height, width, players, areas)

    player_iterator = cycle_players(players=players, take=moves)

    for _ in range(round(moves / chunk_size)):
        for player in it.islice(player_iterator, chunk_size):
            x, y = random.randint(0, height - 1), random.randint(0, width - 1)
            store(assert_call(gamma_move, board, player, x, y))
        assert_board_equal(store, board)

    delete_board(store, board)


def test_random_actions(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "random actions, total chaos"
    store(make_comment(doc))

    height, width = int(kwargs.get("height", 7)), int(kwargs.get("width", 7))
    players, areas = int(kwargs.get("players", 4)), int(kwargs.get("areas", 7))

    board = make_board(store, height, width, players, areas)

    for player in cycle_players(players=players, take=height * width * 2):
        grouped_areas = board.board.get_grouped_areas()

        if random.random() < 0.85:
            # default - random field
            x, y = random.randint(0, height - 1), random.randint(0, width - 1)
            if random.random() < 0.7:
                # only empty fields
                if FREE_FIELD in grouped_areas:
                    fields = list(flatten(grouped_areas[FREE_FIELD]))
                    x, y = random.choice(fields)

            store(assert_call(gamma_move, board, player, x, y))

        if random.random() < 0.5:  # second move
            if random.random() < 0.1:  # x, y may be outside of board
                x, y = random.randint(-1, height), random.randint(-1, width)
            else:  # always within board
                x, y = random.randint(0, height - 1), random.randint(0, width - 1)
            x, y = random.randint(0, height - 1), random.randint(0, width - 1)
            store(assert_call(gamma_move, board, player, x, y))

        if random.random() < 0.1:
            store(assert_call(gamma_busy_fields, board, player))

        if random.random() < 0.1:
            store(assert_call(gamma_free_fields, board, player))

        if random.random() < 0.1:
            store(assert_call(gamma_golden_possible, board, player))

        if random.random() < 0.05:
            # default - player_to_attack is self or empty
            player_to_attack = random.choice([FREE_FIELD, player])
            if random.random() < 0.95:
                others = list(set(grouped_areas.keys()) - {FREE_FIELD, player})
                if others:
                    player_to_attack = random.choice(others)

            if player_to_attack in grouped_areas:
                other_players_fields = list(flatten(grouped_areas[player_to_attack]))
                if other_players_fields:
                    field = random.choice(other_players_fields)
                    store(assert_call(gamma_golden_move, board, player, *field))

        if random.random() < 0.05:
            assert_board_equal(store, board)

    delete_board(store, board)


def test_golden_move_complexity(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "tests golden move complexity"
    store(make_comment(doc))

    width, height = int(kwargs.get("width", 100)), int(kwargs.get("height", 100))
    players, areas = int(kwargs.get("players", 2)), int(kwargs.get("areas", 2))
    tests = int(kwargs.get("players", (height * width) ** 0.5))
    board = make_board(store, width, height, players, areas)
    board.max_areas = 1

    def can_move(p: int) -> bool:
        return bool(gamma_free_fields(board, p) or gamma_golden_possible(board, p))

    for _ in range(25):
        if not any(can_move(p) for p in range(1, players + 1)):
            break
        for p in range(1, players + 1):
            if board.get_busy_fields(p) == 0:
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                store(assert_call(gamma_move, board, p, x, y))
            else:
                for y, x in board.get_free_fields_coords(p):
                    store(assert_call(unsafe_gamma_move, board, p, x, y))

    board.max_areas = areas
    for i in range(round(tests)):
        if not any(gamma_golden_possible(board, p) for p in range(1, players + 1)):
            break

        for p in range(1, players + 1):
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            store(assert_call(gamma_golden_move, board, p, x, y))

    delete_board(store, board)


def test_golden_move_complexity_single_square(
    store: StatementStoreType, **kwargs: Any
) -> None:
    doc = (
        "tests golden move complexity,"
        "player one has whole board while player 2 has only one square"
    )
    store(make_comment(doc))

    width, height = int(kwargs.get("width", 100)), int(kwargs.get("height", 100))
    players, areas = 2, 1
    tests = int(kwargs.get("players", (height * width) ** 0.5))

    board = make_board(store, width, height, players, areas)

    store(
        assert_call(
            gamma_move,
            board,
            2,
            random.randint(0, width - 1),
            random.randint(0, height - 1),
        )
    )

    for y, x in sorted(board.get_free_fields_coords(player=1)):
        store(assert_call(unsafe_gamma_move, board, 1, x, y))

    for i in range(tests):
        if not gamma_golden_possible(board, 2):
            break
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        store(assert_call(gamma_golden_move, board, 2, x, y))

    delete_board(store, board)


def test_golden_move_complexity_many_splits(
    store: StatementStoreType, **kwargs: Any
) -> None:
    doc = (
        "gamma_golden_move complexity, "
        "attempts invalid golden moves (too many areas)"
    )
    store(make_comment(doc))

    width, height = int(kwargs.get("width", 100)), int(kwargs.get("height", 100))
    players = int(kwargs.get("players", 100))
    board = make_board(store, height, width, players, 3)
    all_fields = get_all_board_coords(board)
    random_centers = random.sample(all_fields, k=players)

    player_center_area = {
        p: (f, get_coords_around(board, *f))
        for (p, f) in zip(range(1, players + 1), random_centers)
    }

    for player, (center, neighbors) in player_center_area.items():
        x, y = center
        if board.board.board[y][x] == FREE_FIELD:
            store(assert_call(unsafe_gamma_move, board, player, *center))
            for (x, y) in neighbors:
                if board.board.board[y][x] == FREE_FIELD:
                    store(assert_call(unsafe_gamma_move, board, player, x, y))

    if bool(kwargs.get("always_fail", True)):
        for player in range(1, players + 1):
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            store(assert_call(gamma_move, board, player, x, y))

    for player in range(1, players + 1):
        field = random.choice(random_centers)
        store(assert_call(gamma_golden_move, board, player, *field))

    delete_board(store, board)


def test_free_fields_complexity(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_free_fields complexity"
    store(make_comment(doc))

    width, height = int(kwargs.get("width", 100)), int(kwargs.get("height", 100))
    players = int(kwargs.get("players", 100))
    areas = round(players ** (1 / 2))

    board = make_board(store, height, width, players, areas)
    all_fields = get_all_board_coords(board)
    random.shuffle(all_fields)

    for p in range(1, players + 1):
        for _ in range(areas - 1):
            store(assert_call(unsafe_gamma_move, board, p, *all_fields.pop()))

    for p in range(1, players + 1):
        for _ in range(2):
            store(assert_call(gamma_free_fields, board, p))

    for p in range(1, players + 1):
        store(assert_call(unsafe_gamma_move, board, p, *all_fields.pop()))

    for _ in range(3):
        for p in range(1, players + 1):
            store(assert_call(gamma_free_fields, board, p))

    delete_board(store, board)


def test_busy_fields_complexity(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "gamma_busy_fields complexity"
    store(make_comment(doc))

    width, height = int(kwargs.get("width", 100)), int(kwargs.get("height", 100))
    players = int(kwargs.get("players", 100))
    areas = round(players ** (1 / 2))

    board = make_board(store, height, width, players, areas)

    all_fields = get_all_board_coords(board)
    random.shuffle(all_fields)
    for p in range(1, players + 1):
        for _ in range(areas):
            store(assert_call(unsafe_gamma_move, board, p, *all_fields.pop()))

    for _ in range(4):
        for p in range(1, players + 1):
            store(assert_call(gamma_free_fields, board, p))

    delete_board(store, board)


scenarios: Dict[str, ScenarioType] = {
    "fill_board_with_collisions": fill_board_with_collisions,
    "fill_board_without_collisions": fill_board_without_collisions,
    "test_check_busy_fields": test_check_busy_fields,
    "fill_board_with_areas_limit": fill_board_with_areas_limit,
    "test_free_fields": test_free_fields,
    "test_golden_possible": test_golden_possible,
    "test_strip": test_strip,
    "test_golden_move": test_golden_move,
    "test_gamma_board": test_gamma_board,
    "test_many_boards": test_many_boards,
    "test_random_actions": test_random_actions,
    "test_golden_move_complexity": test_golden_move_complexity,
    "test_golden_move_complexity_single_square": test_golden_move_complexity_single_square,
    "test_golden_move_complexity_many_splits": test_golden_move_complexity_many_splits,
    "test_free_fields_complexity": test_free_fields_complexity,
    "test_busy_fields_complexity": test_busy_fields_complexity,
}

__all__ = ["scenarios"]
