import os
import re
import sys

from typing import Optional


def preprocess_c_code(text: str) -> str:
    no_comments = remove_comments(text)
    no_includes = remove_includes(no_comments)
    merged_lines = merge_lines(no_includes)

    return re.sub(r" +", " ", merged_lines)


def remove_includes(text: str) -> str:
    return "\n".join(line for line in text.split("\n") if "#include" not in line)


def merge_lines(text: str) -> str:
    buffer = []

    res = []
    for line in text.split("\n"):
        buffer.append(line)
        if ";" in line:
            res.append(" ".join(buffer))
            buffer = []

    return "\n".join(res)


def remove_comments(text: str) -> str:
    text_without_block_comments = re.sub(r"/\*(.|\n|\r)*?\*/", "", text)
    text_without_line_comments = re.sub(r"//.*", "", text_without_block_comments)
    return text_without_line_comments


def check_exclamation_mark(text: str) -> str:
    return text.replace("!", "not ")


def check_null(text: str) -> str:
    if "NULL" in text:
        return "None"
    return text


def process_assertion(line: str) -> str:
    l_side = ""
    operand = ""
    match = re.findall(r"(?<=assert\().*(?=\) *;)", line)
    if match is None:
        return ""
    if not len(match):
        return ""
    text = match[0]

    if "==" in text:
        operand = "is" if "NULL" in text else "=="
    elif "!=" in text:
        operand = "is not" if "NULL" in text else "!="

    split = list(map(check_null, map(check_exclamation_mark, re.split(r"[!=]=", text))))
    if len(split) == 2:
        l_side = check_null(split[0])
        r_side = check_null(split[1])
    else:
        r_side = split[0]

    return " ".join(["assert", l_side, operand, r_side])


def get_name(text: str) -> str:
    name = ""
    split = list(filter(lambda s: s != "", text.split(" ")))
    if split:
        if split[-1] == "[]":
            if len(split) > 1:
                name = split[-2]
        else:
            name = split[-1]

    return re.sub(r"\*|(\[\])", "", name)


def process_assignment(line: str) -> str:
    split = line.split("=")
    name = ""
    value = ""
    if len(split) == 2:
        name = get_name(split[0])
        value = split[1].split(";")[0]
    return " ".join([name, "=", value])


def process_gamma_deletion(line: str) -> str:
    match = re.search(r"gamma_delete\(.*\)", line)
    if match is None:
        return ""
    return match.group()


def process_line(line: str) -> str:
    if "assert" in line:
        return process_assertion(line)
    elif "=" in line:
        return process_assignment(line)
    elif "gamma_delete" in line:
        return process_gamma_deletion(line)
    return ""


def gen_py(file_name: str) -> str:
    res = []
    with open(file_name, "r") as f:
        code = preprocess_c_code(f.read())
    for line in code.split("\n"):
        processed = process_line(line)
        if processed:
            res += [processed]

    return "\n".join(res)


def convert_file(
    file_name: str, out_dir_name: str, out_file_name: Optional[str] = None
) -> bool:
    if file_name[-2:] != ".c":
        return False

    with open("templates/py_file_template", "r") as t:
        template = t.read()

    py_code = gen_py(file_name)
    strcmp = (
        "def strcmp(str1: str, str2: str) -> int: return (str1 > str2) - (str1 < str2)"
    )

    final = re.sub(r" +", " ", "\n".join([strcmp, "", py_code]))

    if out_file_name is None:
        out_file_name = os.path.basename(file_name)[:-1] + "py"

    out_name = "/".join([out_dir_name, out_file_name])

    if not os.path.exists(os.path.dirname(out_name)):
        os.makedirs(os.path.dirname(out_name))

    with open(out_name, "w") as f:
        f.write(template.format(final))

    return True


def convert(in_dir: str, out_dir: str) -> None:
    if os.path.isdir(in_dir):
        for name in os.listdir(in_dir):
            print(name, out_dir)
            full_name = "/".join([in_dir, name])
            if os.path.isfile(full_name):
                if name.endswith(".c"):
                    convert_file(full_name, out_dir)
            elif os.path.isdir(full_name):
                convert(full_name, "/".join([out_dir, name]))
    else:
        raise NotAFolderException()


class NotAFolderException(Exception):
    pass


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 3:
        print(
            "usage: python convert_to_py.py <input_directory_path> "
            "<output_directory_path>\n "
        )
        sys.exit(1)

    try:
        convert(*sys.argv[1:])
    except NotAFolderException:
        print("It's not a folder")
