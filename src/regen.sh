#!/usr/bin/env bash

shopt -s nullglob
for f in out/generated_batch/*.in; do python part2.py <$f 1> "${f%.*}.out" 2> "${f%.*}.err"; done
