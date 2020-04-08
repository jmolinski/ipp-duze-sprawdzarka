import itertools

from typing import Callable, Dict, Generator, Iterable, List, Mapping, Set, Tuple

from gamma.board_defaultdict import make_empty_board
from gamma.unionfind import UnionFind  # type: ignore

Coords = Tuple[int, int]
ListOfAreas = List[Set[Coords]]

FREE_FIELD = -1


def make_neighbor_getter(
    width: int, height: int
) -> Callable[[int, int], Iterable[Coords]]:
    def neighbors(x: int, y: int) -> Generator[Coords, None, None]:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                yield nx, ny

    return neighbors


def encode(coords: Coords) -> int:
    return (coords[0] << 32) + coords[1]


def decode(encoded: int) -> Coords:
    return encoded >> 32, encoded % (1 << 32)


def group_areas_by_player(
    board: Mapping[int, Mapping[int, int]], width: int, height: int
) -> Dict[int, ListOfAreas]:
    areas_by_player: Dict[int, ListOfAreas] = {}
    get_neighbors = make_neighbor_getter(width, height)

    all_fields = set(itertools.product(range(height), range(width)))
    uf = UnionFind()

    occupied_fields = set()

    for y, row in board.items():
        for x, field in row.items():
            occupied_fields.add((y, x))
            uf.add(encode((y, x)))

    rows = list(board.items())
    for y, row in rows:
        fields = list(row.items())
        for x, field in fields:
            for (nx, ny) in get_neighbors(x, y):
                if board[y][x] == board[ny][nx] and board[y][x] != FREE_FIELD:
                    uf.union(encode((y, x)), encode((ny, nx)))

    if occupied_fields:
        for component in uf.components():
            lc = list(map(decode, component))
            x, y = lc[0]
            player = board[x][y]
            areas = areas_by_player.get(player, [])
            lc_set = set(lc)
            areas.append(lc_set)
            areas_by_player[player] = areas
            occupied_fields |= lc_set

    free_fields = all_fields - occupied_fields
    if free_fields:
        areas_by_player[FREE_FIELD] = [free_fields]

    return areas_by_player


def main() -> None:
    board1 = make_empty_board(3, 3, free_field=-1)
    board1_data = {
        0: {0: 1, 1: 1, 2: 2},
        1: {0: 3, 1: 1, 2: 1},
        2: {1: 1, 2: 2},
    }

    board2 = make_empty_board(2, 2, free_field=-1)
    board2_data = {
        0: {0: 1, 1: 2},
        1: {0: 3, 1: 4},
    }

    board3 = make_empty_board(8, 1, free_field=-1)
    board3_data = {0: {0: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 3, 6: 2, 7: 1, 8: 1}}

    for board, board_data in [
        (board1, board1_data),
        (board2, board2_data),
        (board3, board3_data),
    ]:
        for y, row in board_data.items():
            for x, field in row.items():
                board[y][x] = field

    assert group_areas_by_player(board1, 3, 3) == {
        1: [{(0, 1), (1, 2), (2, 1), (0, 0), (1, 1)}],
        2: [{(0, 2)}, {(2, 2)}],
        3: [{(1, 0)}],
        -1: [{(2, 0)}],
    }
    assert group_areas_by_player(board2, 2, 2) == {
        1: [{(0, 0)}],
        2: [{(0, 1)}],
        3: [{(1, 0)}],
        4: [{(1, 1)}],
    }
    assert group_areas_by_player(board3, 9, 1) == {
        1: [{(0, 1), (0, 2), (0, 0)}, {(0, 4)}, {(0, 7), (0, 8)}],
        2: [{(0, 3)}, {(0, 6)}],
        3: [{(0, 5)}],
    }


if __name__ == "__main__":
    main()

main()
