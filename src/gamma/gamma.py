from __future__ import annotations

import itertools

from typing import List, Set

from gamma.board import Board
from gamma.group_areas import Coords, make_neighbor_getter

flatten = itertools.chain.from_iterable


class Gamma:
    board: Board

    def __init__(self, width: int, height: int, players: int, areas: int) -> None:
        self.board = Board(width, height)
        self.players = players
        self.max_areas = areas
        self._golden_move_done: Set[int] = set()

    def _is_in_valid_state(self) -> bool:
        areas_by_player = self.board.get_grouped_areas()
        if Board.FREE_FIELD in areas_by_player:
            del areas_by_player[Board.FREE_FIELD]

        return all(
            len(player_areas) <= self.max_areas
            for player_areas in areas_by_player.values()
        )

    def try_move(self, player: int, column: int, row: int) -> bool:
        if self.board.board[row][column] != Board.FREE_FIELD:
            return False

        self.board.board[row][column] = player
        if self._is_in_valid_state():
            return True

        self.board.board[row][column] = Board.FREE_FIELD
        return False

    def try_golden_move(self, player: int, column: int, row: int) -> bool:
        if player in self._golden_move_done:
            return False

        field = self.board.board[row][column]
        if field == Board.FREE_FIELD or field == player:
            return False

        self.board.board[row][column] = Board.FREE_FIELD
        moved = self.try_move(player, column, row)
        if moved:
            self._golden_move_done.add(player)
        else:
            self.board.board[row][column] = field

        return moved

    def get_free_fields(self, player: int) -> int:
        grouped_areas = self.board.get_grouped_areas()
        free_coords = flatten(grouped_areas[Board.FREE_FIELD])

        player_areas = grouped_areas.get(player, [])
        if len(player_areas) < self.max_areas:
            return len(list(free_coords))

        neighbor_getter = make_neighbor_getter(self.board.board)

        return sum(
            self._can_move_to_empty_field(player_areas, list(neighbor_getter(*coord)))
            for coord in free_coords
        )

    @staticmethod
    def _can_move_to_empty_field(
        player_areas: List[Set[Coords]], neighbors: List[Coords]
    ) -> bool:
        for n in neighbors:
            if any(n in area for area in player_areas):
                return True

        return False

    def get_busy_fields(self, player: int) -> int:
        return sum(row.count(player) for row in self.board.board)

    def is_golden_possible(self, player: int) -> bool:
        if player in self._golden_move_done:
            return False

        grouped_areas = self.board.get_grouped_areas()
        return bool(set(grouped_areas.keys()) - {player, Board.FREE_FIELD})
