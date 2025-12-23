from __future__ import annotations

from typing import Iterable

from .board import Board


def print_board(board: Board) -> None:
    header = "   " + " ".join(str(x) for x in range(board.width))
    print(header)
    for y in range(board.height):
        row_symbols = []
        for x in range(board.width):
            symbol = board.grid[y][x]
            if board.player and board.player.x == x and board.player.y == y:
                symbol = board.player.symbol
            row_symbols.append(symbol)
        line = f"{y}  " + " ".join(row_symbols)
        print(line)


def describe_actions(actions: Iterable[str]) -> str:
    return ", ".join(actions)

