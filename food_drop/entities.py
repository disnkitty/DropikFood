from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple


class SerializableMixin:
    def to_tuple(self) -> tuple[Any, ...]:
        return tuple(self.__dict__.values())


class NamedMixin:
    def __init__(self, name: str = "Гравець"):
        self.name = name


@dataclass(eq=True)
class Entity(SerializableMixin):
    x: int
    y: int
    symbol: str = "."

    def __iter__(self):
        yield from (self.x, self.y)

    def __len__(self) -> int:
        return 3

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(pos=({self.x},{self.y}), symbol='{self.symbol}')"


class Player(Entity, NamedMixin):
    def __init__(self, x: int, y: int, symbol: str = "U", name: str = "Гравець"):
        Entity.__init__(self, x, y, symbol)
        NamedMixin.__init__(self, name)
        self._score: int = 0
        self._lives: int = 3

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        if value < 0:
            raise ValueError("Рахунок не може бути відʼємним")
        self._score = value

    @property
    def lives(self) -> int:
        return self._lives

    @lives.setter
    def lives(self, value: int) -> None:
        self._lives = max(0, value)


