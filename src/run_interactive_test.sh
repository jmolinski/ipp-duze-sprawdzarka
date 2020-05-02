#!/usr/bin/env bash

if [[ $# != 2 ]]; then
  echo "Sposób uzytkowania: $0 <ścieżka/do/gamma> <ścieżka/do/pliku/z/testem.ivml>" >&2
  exit 1
fi

gamma_executable=$(realpath "$1")
plik_testowany=$(realpath "$2")

if ! [[ -x "$gamma_executable" ]]; then
  echo "Podany plik wykonywalny gamma nie istnieje"
  exit 1
fi

if ! [[ -f "$plik_testowany" ]]; then
  echo "Podany test nie istnieje"
  exit 1
fi

native_gamma_input=$(mktemp)
gamma_output=$(mktemp)
trap 'rm -f "native_gamma_input"' INT TERM HUP EXIT
trap 'rm -f "gamma_output"' INT TERM HUP EXIT

plik_z_prawidlowym_wynikiem=${plik_testowany//.ivml/.vmr}

python3 -u part2_ivm.py --nowait < "$plik_testowany" 1> "$native_gamma_input"
"$gamma_executable" < "$native_gamma_input" > "$gamma_output"
err=$?

if [[ $err != 0 ]]; then
  exit 1
else
  python3 verify_interactive_final_board.py "$gamma_output" "$plik_z_prawidlowym_wynikiem"
  err=$?

  if [[ $err != 0 ]]; then
    exit 1
  else
    exit 0
  fi
fi