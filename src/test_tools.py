from typing import Callable, Dict, Optional, Tuple, TypedDict, TypeVar, Union

from gamma.gamma import Gamma

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


def call(
    f: Callable[..., T], board: Optional[Gamma], *args: int, board_name: str = "board"
) -> Tuple[str, T]:
    ret_val = f(*args) if board is None else f(board, *args)
    rendered_args = ", ".join(str(a) for a in args)
    return (
        f"{f.__name__}({board_name + ', ' if board else ''} {rendered_args})",
        ret_val,
    )


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
