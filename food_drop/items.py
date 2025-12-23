from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .entities import Entity


class CollectibleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_collected: bool = False
    
    @property
    def is_collected(self) -> bool:
        return self._is_collected
    
    def collect(self) -> None:
        self._is_collected = True


class ScorableMixin:
    def __init__(self, points: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._points: int = points
    
    @property
    def points(self) -> int:
        return self._points
    
    @points.setter
    def points(self, value: int) -> None:
        if value < 0:
            raise ValueError("Points cannot be negative")
        self._points = value


class DangerousMixin:
    def __init__(self, damage: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._damage: int = damage
    
    @property
    def damage(self) -> int:
        return self._damage
    
    @damage.setter
    def damage(self, value: int) -> None:
        if value < 0:
            raise ValueError("Damage cannot be negative")
        self._damage = value


class TimedMixin:
    def __init__(self, duration: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._duration: int = duration
        self._timer: int = duration
    
    @property
    def duration(self) -> int:
        return self._duration
    
    @property
    def timer(self) -> int:
        return self._timer
    
    @timer.setter
    def timer(self, value: int) -> None:
        self._timer = max(0, value)
    
    def tick(self) -> bool:
        self._timer -= 1
        return self._timer > 0


class NamedMixin:
    def __init__(self, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name: str = name
    
    @property
    def name(self) -> str:
        return self._name if self._name else self.symbol


@dataclass(eq=True)
class FoodItem(Entity, CollectibleMixin, ScorableMixin, NamedMixin):
    def __init__(self, x: int, y: int, symbol: str, points: int = 1, name: str = ""):
        Entity.__init__(self, x, y, symbol)
        CollectibleMixin.__init__(self)
        ScorableMixin.__init__(self, points)
        NamedMixin.__init__(self, name)
    
    def as_tuple(self) -> Tuple[int, int, str, int]:
        return (self.x, self.y, self.symbol, self.points)


@dataclass(eq=True)
class ForbiddenItem(Entity, CollectibleMixin, DangerousMixin, NamedMixin):
    def __init__(self, x: int, y: int, symbol: str, damage: int = 999, name: str = ""):
        Entity.__init__(self, x, y, symbol)
        CollectibleMixin.__init__(self)
        DangerousMixin.__init__(self, damage)
        NamedMixin.__init__(self, name)
    
    def as_tuple(self) -> Tuple[int, int, str, int]:
        return (self.x, self.y, self.symbol, self.damage)


@dataclass(eq=True)
class PowerUpItem(Entity, CollectibleMixin, ScorableMixin, TimedMixin, NamedMixin):
    def __init__(
        self, 
        x: int, 
        y: int, 
        symbol: str, 
        points: int = 5,
        duration: int = 10,
        name: str = "",
        effect_type: str = "speed"
    ):
        Entity.__init__(self, x, y, symbol)
        CollectibleMixin.__init__(self)
        ScorableMixin.__init__(self, points)
        TimedMixin.__init__(self, duration)
        NamedMixin.__init__(self, name)
        self.effect_type: str = effect_type
    
    def as_tuple(self) -> Tuple[int, int, str, int, int, str]:
        return (self.x, self.y, self.symbol, self.points, self.duration, self.effect_type)


@dataclass(eq=True)
class BonusFoodItem(FoodItem, ScorableMixin):
    
    
    def __init__(self, x: int, y: int, symbol: str, points: int = 10, name: str = ""):
       
        Entity.__init__(self, x, y, symbol)
        CollectibleMixin.__init__(self)
        ScorableMixin.__init__(self, points)
        NamedMixin.__init__(self, name)
        self._bonus_multiplier: float = 1.5
    
    @property
    def bonus_multiplier(self) -> float:
        return self._bonus_multiplier
    
    @property
    def effective_points(self) -> int:
        return int(self.points * self._bonus_multiplier)
    
    def as_tuple(self) -> Tuple[int, int, str, int, float]:
        return (self.x, self.y, self.symbol, self.points, self._bonus_multiplier)

