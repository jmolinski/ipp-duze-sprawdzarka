from part1 import gamma_golden_move, gamma_golden_possible, gamma_move, gamma_new

g = gamma_new(2, 2, 2, 1)
assert g is not None
assert gamma_move(g, 1, 0, 0)
assert gamma_move(g, 2, 1, 1)
assert gamma_golden_possible(g, 1)
assert not gamma_golden_move(g, 1, 1, 1)
