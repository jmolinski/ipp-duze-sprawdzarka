import json
import sys

from typing import Any, Dict, List, Tuple

from test_scenarios import scenarios
from test_tools import (
    ScenarioType,
    make_statements_dispatcher,
    make_comment,
    make_random_id,
)

OUTPUT_DIR = "out/"  # TODO


def make_tests(
    scenario: ScenarioType, unique_id: str, extras: Dict[str, Any]
) -> Tuple[List[str], List[str]]:
    spython: List[str] = []
    sclang: List[str] = []
    store = make_statements_dispatcher(spython, sclang)

    store(make_comment(f"scenario: {scenario.__name__}\nuuid: {unique_id}"))
    scenario(store, **extras)

    return sclang, spython


def run_scenario(
    output_file_name: str, scenario: ScenarioType, extras: Dict[str, Any]
) -> None:
    with open("templates/c_file_template", "r") as f:
        c_file_template = f.read()
    with open("templates/py_file_template", "r") as f:
        py_file_template = f.read()

    test_id = make_random_id()
    if output_file_name == 'AUTO':
        output_file_name = test_id

    c_statements, py_statements = make_tests(scenario, test_id, extras)
    output_file_c = c_file_template.format("\n".join(c_statements))
    output_file_py = py_file_template.format("\n".join(py_statements))

    with open(OUTPUT_DIR + output_file_name + ".c", "w") as f:
        f.write(output_file_c)

    with open(OUTPUT_DIR + output_file_name + ".py", "w") as f:
        f.write(output_file_py)


def main():
    if len(sys.argv) < 3:
        print(
            "usage: python make_tests.py output_file scenario\n"
            "[without extension, will generate output_file.c and output_file.py]"
        )
        sys.exit(1)

    try:
        chosen_scenario: ScenarioType = scenarios[sys.argv[2]]
    except KeyError:
        print(
            "scenario name not recognized\n"
            f"[available scenarios {list(scenarios.keys())}]"
        )
        sys.exit(1)

    extra_arguments = {} if len(sys.argv) == 3 else json.loads(sys.argv[4])
    run_scenario(sys.argv[1], chosen_scenario, extra_arguments)


if __name__ == "__main__":
    main()
