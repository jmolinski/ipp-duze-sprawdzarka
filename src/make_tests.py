import sys

from typing import Callable, List, Tuple

import test_scenarios

from test_tools import StatementStoreType, make_statements_dispatcher

ScenarioType = Callable[[StatementStoreType], None]


def make_tests(scenario: ScenarioType) -> Tuple[List[str], List[str]]:
    spython: List[str] = []
    sclang: List[str] = []

    scenario(make_statements_dispatcher(spython, sclang))

    return sclang, spython


def main(output_file_name: str, scenario: ScenarioType) -> None:
    with open("c_file_template", "r") as f:
        c_file_template = f.read()
    with open("py_file_template", "r") as f:
        py_file_template = f.read()

    c_statements, py_statements = make_tests(scenario)
    output_file_c = c_file_template.format("\n".join(c_statements))
    output_file_py = py_file_template.format("\n".join(py_statements))

    with open(output_file_name + ".c", "w") as f:
        f.write(output_file_c)

    with open(output_file_name + ".py", "w") as f:
        f.write(output_file_py)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "usage: python make_tests.py output_file scenario\n"
            "[without extension, will generate output_file.c and output_file.py]"
        )
        sys.exit(1)

    try:
        chosen_scenario: ScenarioType = getattr(test_scenarios, sys.argv[2])
    except AttributeError:
        available_scenarios = test_scenarios.__all__
        print(
            "scenario name not recognized\n"
            f"[available scenarios {available_scenarios}]"
        )
        sys.exit(1)

    main(sys.argv[1], chosen_scenario)
