from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

from .entities import Entity, Player

Matrix = List[List[str]]


class Board(Sequence[str]):
    def __init__(self, width: int, height: int, empty_symbol: str = "."):
        self.width = width
        self.height = height
        self.empty_symbol = empty_symbol
   
        self.grid: Matrix = [[empty_symbol for _ in range(width)] for _ in range(height)]
        self.forbidden: set[str] = set()
        self.items: Dict[Tuple[int, int], Entity] = {}
        self.player: Player | None = None

    def __len__(self) -> int:
        return len(self.grid)

    def __getitem__(self, index):
        return self.grid[index]

    def __iter__(self):
        return iter(self.grid)

    def __contains__(self, value: object) -> bool:
    
        return any(value in row for row in self.grid)

    def reset(self) -> None:
    
        self.grid = [[self.empty_symbol for _ in range(self.width)] for _ in range(self.height)]
        self.items.clear()

    def add_player(self, player: Player) -> None:
        self.player = player

    def _place(self, entity: Entity) -> None:
        self.grid[entity.y][entity.x] = entity.symbol
      
        self.items[(entity.x, entity.y)] = entity

    def clear_cell(self, x: int, y: int) -> None:
        self.grid[y][x] = self.empty_symbol
     
        self.items.pop((x, y), None)

    def get_row(self, y: int) -> List[str]:
        if 0 <= y < self.height:
            return self.grid[y][:]
        return []

    def get_column(self, x: int) -> List[str]:
        if 0 <= x < self.width:
            return [row[x] for row in self.grid]
        return []

    def get_region(self, x: int, y: int, width: int, height: int) -> List[List[str]]:
        if (0 <= x < self.width and 0 <= y < self.height and
            x + width <= self.width and y + height <= self.height):
            return [row[x:x+width] for row in self.grid[y:y+height]]
        return []

    def get_all_positions(self) -> List[Tuple[int, int]]:
        return [(x, y) for y in range(self.height) for x in range(self.width)]

    def get_item_positions(self) -> Tuple[Tuple[int, int], ...]:
        return tuple(self.items.keys())

    def get_empty_positions(self) -> List[Tuple[int, int]]:
        return [
            (x, y) for x, y in self.get_all_positions()
            if self.grid[y][x] == self.empty_symbol
        ]

    def count_items_by_symbol(self) -> Dict[str, int]:
        symbol_counts = {}
        for entity in self.items.values():
            symbol = entity.symbol
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        return symbol_counts

    def move_player(self, dx: int) -> None:
        if not self.player:
            raise ValueError("Гравець не розміщений")
        new_x = min(max(self.player.x + dx, 0), self.width - 1)
        if new_x == self.player.x:
            return
        self.player.x = new_x

    def drop_items(self, items: Iterable[Entity]) -> List[Entity]:
        missed: List[Entity] = []
        new_positions: Dict[Tuple[int, int], Entity] = {}
        
        items_list = list(self.items.items())
        
        for (x, y), entity in items_list:
            self.clear_cell(x, y)
            new_y = y + 1
            if new_y >= self.height:
                missed.append(entity)
                continue
            entity = type(entity)(x, new_y, entity.symbol, getattr(entity, "points", 0))
            new_positions[(x, new_y)] = entity
        
        for entity in items:
            new_positions[(entity.x, entity.y)] = entity
        
        for (x, y), entity in new_positions.items():
            self._place(entity)
        
        return missed

    def get_items_in_row(self, y: int) -> List[Entity]:
        return [
            entity for (x, row_y), entity in self.items.items()
            if row_y == y
        ]

    def get_items_in_range(self, x_range: Tuple[int, int], y_range: Tuple[int, int]) -> List[Entity]:
        x_min, x_max = x_range
        y_min, y_max = y_range
        return [
            entity for (x, y), entity in self.items.items()
            if x_min <= x < x_max and y_min <= y < y_max
        ]

    def render(self) -> str:
        lines: List[str] = [
            " ".join([
                self.player.symbol if (self.player and self.player.x == x and self.player.y == y)
                else self.grid[y][x]
                for x in range(self.width)
            ])
            for y in range(self.height)
        ]
        return "\n".join(lines)

    def render_with_borders(self) -> str:
        border = "+" + "-" * (self.width * 2 - 1) + "+"
        lines = [border]
        for y, row in enumerate(self.grid):
            row_list = list(row)
            if self.player and self.player.y == y:
                row_list[self.player.x] = self.player.symbol
            line = "|" + " ".join(row_list) + "|"
            lines.append(line)
        lines.append(border)
        return "\n".join(lines)

