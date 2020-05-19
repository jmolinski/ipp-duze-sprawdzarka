#!/usr/bin/env bash

function substitute_dir_name(){
  file="$1"
  new_dir="$2"
  echo "$new_dir${file#"$c_tests_path"}"
}

c_tests_path="$(realpath "$1")"
tests_path="$(realpath "$2")"
out_path="$(realpath "$3")"

shopt -s nullglob
#doesn't names with words that have spaces in it
for f in $(find "$c_tests_path" -type f -name "*.c" -print0 | xargs -0); do
  helper_py_test_path="$(substitute_dir_name "$f" "$tests_path")"
  py_test_path="${helper_py_test_path%.c}.py"
  out_file_path="$(substitute_dir_name "$f" "$out_path")"

  echo "$f" "$py_test_path" "$out_file_path"
  mkdir -p "$(dirname "$out_file_path")"
  python part1_to_part3.py "$py_test_path" "$f" > "$out_file_path" || exit 1

done
