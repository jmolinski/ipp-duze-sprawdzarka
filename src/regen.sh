#!/usr/bin/env bash

shopt -s nullglob
for f in $(find . -type f -name "*.in" -print0 | xargs -0); do
  echo "$f"
  python part2.py <"$f" > "${f%.*}.out" 2> "${f%.*}.err"
done
