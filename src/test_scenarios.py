import random
from typing import Any, Dict, List

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
    assert_call,
    cycle_players,
    delete_board,
    flatten,
    get_all_board_coords,
    make_board,
    make_comment,
)


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

    delete_board(store, board)


def test_free_fields(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "free_fields, with collisions, many players, limited areas"
    store(make_comment(doc))

    board = make_board(store, 8, 8, 5, 8)

    for player in cycle_players(players=5, take=8 * 8 * 2):
        x, y = random.randint(0, 4), random.randint(0, 4)
        store(assert_call(gamma_move, board, player, x, y))
        store(assert_call(gamma_busy_fields, board, player))
        store(assert_call(gamma_free_fields, board, player))

    delete_board(store, board)


def test_golden_possible(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "golden_possible, limited areas"
    store(make_comment(doc))

    board = make_board(store, 4, 4, 8, 3)

    for player in cycle_players(players=8, take=4 * 4):
        x, y = random.randint(0, 4), random.randint(0, 4)
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

    def end_chunk() -> None:
        for p in range(1,players+1):
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
        x, y = random.randint(0, width), random.randint(0, height)
        store(assert_call(gamma_move, board, player, x, y))
        if i % chunk_size == 0 and i != 0:
            end_chunk()
    end_chunk()

    delete_board(store, board)


def test_golden_move(store: StatementStoreType, **kwargs: Any) -> None:
    doc = "golden_move, limited areas"
    store(make_comment(doc))

    players_n = 3
    board = make_board(store, 8, 8, players_n, 12)

    all_fields = get_all_board_coords(board)
    fields_to_fill = random.sample(all_fields, k=players_n * 10)
    remaining_fields = list(set(all_fields) - set(fields_to_fill))

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
                free_fields = list(
                    flatten(board.board.get_grouped_areas()[board.board.FREE_FIELD])
                )
                field = random.choice(free_fields)
                store(assert_call(gamma_move, board, p, *field))
            else:  # gamma_golden_possible(board, p) == True
                other_player = random.choice(list(set(players) - {p}))
                field = player_fields[other_player].pop()
                store(assert_call(gamma_golden_move, board, p, *field))

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
}

__all__ = ["scenarios"]
