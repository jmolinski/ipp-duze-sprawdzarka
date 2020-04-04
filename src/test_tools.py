import itertools

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)

from gamma.gamma import Gamma
from part1 import gamma_delete, gamma_new

T = TypeVar("T")


class PyCVariants(TypedDict):
    c: str
    py: str


ASSERT: Dict[str, PyCVariants] = {
    "equal": {"c": "assert( {} == {} );", "py": "assert {} == {} "},
    "notequal": {"c": "assert( {} != {} );", "py": "assert {} != {}"},
    "isnull": {"c": "assert( {} == NULL );", "py": "assert {} is None"},
    "isnotnull": {"c": "assert( {} != NULL );", "py": "assert {} is not None"},
}

EMPTY_LINE: PyCVariants = {"py": "\n", "c": "\n"}


def call(
    f: Callable[..., T], board: Optional[Gamma], *args: int, board_name: str = "board"
) -> Tuple[str, T]:
    ret_val = f(*args) if board is None else f(board, *args)
    rendered_args = ", ".join(str(a) for a in args)
    board_arg = "" if not board else f"{board_name}{', ' if rendered_args else ''}"
    return (
        f"{f.__name__}({board_arg}{rendered_args})",
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
