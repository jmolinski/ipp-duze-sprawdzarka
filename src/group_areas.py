from typing import Callable, Dict, Generator, Iterable, List, Set, Tuple

from src.unionfind import UnionFind  # type: ignore

Coords = Tuple[int, int]
ListOfAreas = List[Set[Coords]]


def make_neighbor_getter(
    matrix: List[List[int]],
) -> Callable[[int, int], Iterable[Coords]]:
    def neighbors(x: int, y: int) -> Generator[Coords, None, None]:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(matrix) and 0 <= ny < len(matrix[0]):
                yield nx, ny

    return neighbors


def encode(coords: Coords) -> int:
    return (coords[0] << 32) + coords[1]


def decode(encoded: int) -> Coords:
    return encoded >> 32, encoded % (1 << 32)


def group_areas_by_player(matrix: List[List[int]]) -> Dict[int, ListOfAreas]:
    areas_by_player: Dict[int, ListOfAreas] = {}
    get_neighbors = make_neighbor_getter(matrix)

    uf = UnionFind()
    for x, row in enumerate(matrix):
        for y, field in enumerate(row):
            uf.add(encode((x, y)))
    for x, row in enumerate(matrix):
        for y, field in enumerate(row):
            for n in get_neighbors(x, y):
                if matrix[x][y] == matrix[n[0]][n[1]]:
                    uf.union(encode((x, y)), encode(n))

    for component in uf.components():
        lc = list(map(decode, component))
        x, y = lc[0]
        player = matrix[x][y]
        areas = areas_by_player.get(player, [])
        areas.append(set(lc))
        areas_by_player[player] = areas

    return areas_by_player


def main() -> None:
    board1 = [
        [1, 1, 2],
        [3, 1, 1],
        [-1, 1, 2],
    ]
    board2 = [[1, 2], [3, 4]]
    board3 = [[1, 1, 1, 2, 1, 3, 2, 1, 1]]

    assert group_areas_by_player(board1) == {
        1: [{(0, 1), (1, 2), (2, 1), (0, 0), (1, 1)}],
        2: [{(0, 2)}, {(2, 2)}],
        3: [{(1, 0)}],
        -1: [{(2, 0)}],
    }
    assert group_areas_by_player(board2) == {
        1: [{(0, 0)}],
        2: [{(0, 1)}],
        3: [{(1, 0)}],
        4: [{(1, 1)}],
    }
    assert group_areas_by_player(board3) == {
        1: [{(0, 1), (0, 2), (0, 0)}, {(0, 4)}, {(0, 7), (0, 8)}],
        2: [{(0, 3)}, {(0, 6)}],
        3: [{(0, 5)}],
    }


if __name__ == "__main__":
    main()
