from __future__ import annotations

from typing import Optional

from gamma.gamma import Gamma


def gamma_new(width: int, height: int, players: int, areas: int) -> Optional[Gamma]:
    if width * height < 1 or players < 1 or areas < 1:
        return None
    return Gamma(width, height, players, areas)


def gamma_delete(g: Gamma) -> None:
    del g  # fails if double-deallocation


def gamma_move(g: Gamma, player: int, x: int, y: int) -> bool:
    if x < 0 or y < 0 or g.board.width <= x or g.board.height <= y:
        return False
    if player < 1 or player > g.players:
        return False

    return Gamma.try_move(g, player, x, y)


def gamma_golden_move(g: Gamma, player: int, x: int, y: int) -> bool:
    if x < 0 or y < 0 or g.board.width <= x or g.board.height <= y:
        return False
    if player < 1 or player > g.players:
        return False

    return Gamma.try_golden_move(g, player, x, y)


def gamma_busy_fields(g: Gamma, player: int) -> int:
    return g.get_busy_fields(player)


def gamma_free_fields(g: Gamma, player: int) -> int:
    return g.get_free_fields(player)


def gamma_golden_possible(g: Gamma, player: int) -> bool:
    return g.is_golden_possible(player)


def gamma_board(g: Gamma) -> str:
    return g.board.print()


gamma_t = gamma = Gamma
