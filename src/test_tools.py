import itertools
import random

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

from gamma.gamma import Coords, Gamma
from gamma.group_areas import make_neighbor_getter
from part1 import gamma_board, gamma_delete, gamma_new

T = TypeVar("T")


class PyCVariants(TypedDict):
    c: str
    py: str


ASSERT: Dict[str, PyCVariants] = {
    "equal": {"c": "assert( {} == {} );", "py": "assert {} == {} "},
    "notequal": {"c": "assert( {} != {} );", "py": "assert {} != {}"},
    "isnull": {"c": "assert( {} == NULL );", "py": "assert {} is None"},
    "isnotnull": {"c": "assert( {} != NULL );", "py": "assert {} is not None"},
    "stringequal": {"c": "assert( strcmp({}, \n{}) == 0);", "py": "assert {} == ({})"},
}

EMPTY_LINE: PyCVariants = {"py": "\n", "c": "\n"}


def call(
    f: Callable[..., T], board: Optional[Gamma], *args: int, board_name: str = "board"
) -> Tuple[str, T]:
    ret_val = f(*args) if board is None else f(board, *args)
    rendered_args = ", ".join(str(a) for a in args)
    board_arg = "" if not board else f"{board_name}{', ' if rendered_args else ''}"
    f_name = f.__name__ if f.__name__ != 'unsafe_gamma_move' else 'gamma_move'
    return (
        f"{f_name}({board_arg}{rendered_args})",
        ret_val,
    )


def native_call(
    f: Callable[..., T], board: Optional[Gamma], *args: int, board_name: str = "board"
) -> PyCVariants:
    fn_call, _ = call(f, board, *args, board_name=board_name)
    return {"py": fn_call, "c": fn_call + ";"}


def assert_call(
    f: Callable[..., Union[bool, int]],
    board: Optional[Gamma],
    *args: int,
    assert_type: str = "equal",
    board_name: str = "board",
) -> PyCVariants:
    fn_call, ret_val = call(f, board, *args, board_name=board_name)
    ret_val = int(ret_val)  # bool -> int for compatibility with C
    return make_assert(fn_call, str(ret_val), assert_type=assert_type)


def assign_call(
    f: Callable[..., T],
    board: Optional[Gamma],
    *args: int,
    c_type: str,
    var_name: str,
    board_name: str = "board",
) -> Tuple[PyCVariants, T]:
    fn_call, ret_val = call(f, board, *args, board_name=board_name)
    statements: PyCVariants = {
        "py": f"{var_name} = {fn_call}",
        "c": f"{c_type} {var_name} = {fn_call};",
    }
    return statements, ret_val


def make_assert(val1: str, val2: str = None, assert_type: str = "equal") -> PyCVariants:
    format_arguments = (val1,) if val2 is None else (val1, val2)
    return {
        "py": ASSERT[assert_type]["py"].format(*format_arguments),
        "c": ASSERT[assert_type]["c"].format(*format_arguments),
    }


def make_statements_dispatcher(
    py_statements: List[str], c_statements: List[str]
) -> Callable[[PyCVariants], None]:
    def store(statements: PyCVariants) -> None:
        py_statements.append(statements["py"])
        c_statements.append(statements["c"])

    return store


def make_comment(text: str) -> PyCVariants:
    return {"c": f"/*\n{text}\n*/", "py": f'"""\n{text}\n"""'}


def free_memory(var_name: str) -> PyCVariants:
    return {
        "c": f"free({var_name});\n{var_name} = NULL;",
        "py": f"del {var_name}\n{var_name} = None",
    }


StatementStoreType = Callable[[PyCVariants], None]


class ScenarioType(Protocol):
    def __call__(self, store: StatementStoreType, **kwargs: Any) -> None:
        ...


def make_board(
    store: StatementStoreType,
    m: int,
    n: int,
    players: int,
    areas: int,
    name: str = "board",
) -> Gamma:
    statements, board = assign_call(
        gamma_new, None, m, n, players, areas, c_type="gamma_t*", var_name=name
    )
    store(statements)
    store(make_assert(name, assert_type="isnotnull"))
    store(EMPTY_LINE)
    assert board is not None  # to narrow return type
    return board


def delete_board(
    store: StatementStoreType, board: Gamma, board_name: str = "board"
) -> None:
    store(EMPTY_LINE)
    store(native_call(gamma_delete, board, board_name=board_name))


def cycle_players(players: int, take: int) -> Iterable[int]:
    return itertools.islice(itertools.cycle(range(1, players + 1)), take)


def get_field_neighbors(gamma: Gamma, x: int, y: int) -> Set[Coords]:
    getter = make_neighbor_getter(gamma.board.width, gamma.board.height)
    return set(getter(x, y))


def get_all_board_coords(gamma: Gamma) -> List[Coords]:
    return list(itertools.product(range(gamma.board.height), range(gamma.board.width)))


def get_edge_coords(gamma: Gamma) -> List[Coords]:
    return [
        c
        for c in get_all_board_coords(gamma)
        if len(get_field_neighbors(gamma, *c)) < 4
    ]


def get_coords_around(gamma: Gamma, x: int, y: int, r: int = 1) -> List[Coords]:
    """returns exclusive list without (x, y)
    f(r) = PI(r-1)(r-1)
    len(returned_list) ~ f(r) [not strictly true xD]
    for 0 < r =< 3: f(r+1) is almost exactly len(returned_list)
    for 3 < r < 12: f(r-1) <= len(returned_list) <= f(r)
    """

    coords = {(x, y)}

    for _ in range(r):
        new_coords = coords.copy()
        for (x, y) in coords:
            new_coords |= get_field_neighbors(gamma, x, y)
        coords = new_coords

    return list(coords - {(x, y)})


def make_random_id() -> str:
    return str(random.randint(10 ** 8, 10 ** 9 - 1))


def flatten(s: Iterable[Iterable[T]]) -> Iterable[T]:
    return itertools.chain.from_iterable(s)


def assert_board_equal(
    store: StatementStoreType, board: Gamma, board_name: str = "board"
) -> None:
    store(EMPTY_LINE)
    var_name = "board" + str(make_random_id())
    statements, rendered = assign_call(
        gamma_board, board, c_type="char*", var_name=var_name, board_name=board_name
    )
    store(statements)
    store(make_assert(var_name, assert_type="isnotnull"))
    comp_str = "\n".join(f'"{row}\\n"' for row in rendered.splitlines() if row)
    store(make_assert(var_name, comp_str, assert_type="stringequal"))
    store(free_memory(var_name))


def unsafe_gamma_move(
    g: Gamma,
    player: int,
    x: int,
    y: int,
    handler: Callable[[Gamma, int, int, int], bool] = Gamma.unsafe_move,
) -> bool:

    return handler(g, player, x, y)
