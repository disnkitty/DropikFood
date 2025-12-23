from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple, Type

from .entities import Entity
from .items import (
    BonusFoodItem,
    FoodItem,
    ForbiddenItem,
    PowerUpItem,
    NamedMixin,
    ScorableMixin,
)


class FactoryMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry: Dict[str, Type] = {}
    
    def register(self, key: str, item_class: Type) -> None:
        self._registry[key] = item_class
    
    def create(self, key: str, *args, **kwargs) -> object:
        if key not in self._registry:
            raise ValueError(f"Unknown item type: {key}")
        return self._registry[key](*args, **kwargs)


class ConfigurableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config: Dict = {}
    
    @property
    def config(self) -> Dict:
        return self._config.copy()
    
    def load_config(self, config: Dict) -> None:
        self._config.update(config)


class RandomizableMixin:
    def __init__(self, seed: int | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rng = random.Random(seed)
    
    @property
    def rng(self) -> random.Random:
        return self._rng
    
    def set_seed(self, seed: int) -> None:
        self._rng.seed(seed)


class ItemFactory(FactoryMixin, ConfigurableMixin, RandomizableMixin):
    def __init__(self, config: Dict | None = None, seed: int | None = None):
        FactoryMixin.__init__(self)
        ConfigurableMixin.__init__(self)
        RandomizableMixin.__init__(self, seed)
        
        self.register("food", FoodItem)
        self.register("forbidden", ForbiddenItem)
        self.register("powerup", PowerUpItem)
        self.register("bonus", BonusFoodItem)
        
        if config:
            self.load_config(config)
    
    def create_random_item(
        self, 
        x: int, 
        y: int, 
        item_type: str | None = None,
        symbol: str | None = None
    ) -> Entity:
        if not self._config:
            item_type = item_type or "food"
            symbol = symbol or "?"
            return self.create(item_type, x, y, symbol, 1)
        
        if item_type is None:
            item_type = self._rng.choice(list(self._config.keys()))
        
        items_of_type = self._config.get(item_type, {})
        
        if symbol is None or symbol not in items_of_type:
            if not items_of_type:
                symbol = "?"
                item_data = {}
            else:
                symbol = self._rng.choice(list(items_of_type.keys()))
                item_data = items_of_type[symbol]
        else:
            item_data = items_of_type[symbol]
        
        name = item_data.get("name", "")
        
        if item_type == "food":
            points = 1
            return FoodItem(x, y, symbol, points, name)
        elif item_type == "forbidden":
            damage = item_data.get("damage", 999)
            return ForbiddenItem(x, y, symbol, damage, name)
        elif item_type == "powerup":
            points = item_data.get("points", 5)
            duration = item_data.get("duration", 10)
            effect = item_data.get("effect", "speed")
            return PowerUpItem(x, y, symbol, points, duration, name, effect)
        elif item_type == "bonus":
            points = 1
            return BonusFoodItem(x, y, symbol, points, name)
        else:
            return self.create(item_type, x, y, symbol)


class TrackableMixin:

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stats: Dict[str, int] = {}
    
    @property
    def stats(self) -> Dict[str, int]:
        return self._stats.copy()
    
    def increment_stat(self, key: str, amount: int = 1) -> None:
        self._stats[key] = self._stats.get(key, 0) + amount
    
    def get_stat(self, key: str, default: int = 0) -> int:
        return self._stats.get(key, default)


class ObservableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._observers: List[Callable[[str, Dict], None]] = []
    
    def attach_observer(self, observer: Callable[[str, Dict], None]) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def notify_observers(self, event: str, data: Dict | None = None) -> None:
        for observer in self._observers:
            observer(event, data or {})


class ScoreManager(TrackableMixin, ObservableMixin):
    def __init__(self):
        TrackableMixin.__init__(self)
        ObservableMixin.__init__(self)
        self._total_score: int = 0
        self._multiplier: float = 1.0
        self._combo_count: int = 0
    
    @property
    def total_score(self) -> int:
        return self._total_score
    
    @property
    def multiplier(self) -> float:
        return self._multiplier
    
    @property
    def combo_count(self) -> int:
        return self._combo_count
    
    def add_points(self, points: int, item_type: str = "unknown") -> None:
        effective_points = int(points * self._multiplier)
        self._total_score += effective_points
        self.increment_stat(f"{item_type}_collected", 1)
        self.increment_stat("total_points", effective_points)
        
        if effective_points > 0:
            self._combo_count += 1
        else:
            self._combo_count = 0
        
        self.notify_observers("score_changed", {
            "points": effective_points,
            "total": self._total_score,
            "item_type": item_type
        })
    
    def set_multiplier(self, multiplier: float) -> None:
        self._multiplier = max(1.0, multiplier)
        self.notify_observers("multiplier_changed", {"multiplier": self._multiplier})
    
    def reset_combo(self) -> None:
        self._combo_count = 0
    
    def get_stats_tuple(self) -> Tuple[int, float, int, Dict[str, int]]:
        return (self._total_score, self._multiplier, self._combo_count, self._stats.copy())


class LevelManager(ConfigurableMixin, ObservableMixin):
    def __init__(self, config: Dict | None = None):
        ConfigurableMixin.__init__(self)
        ObservableMixin.__init__(self)
        self._current_level: int = 1
        self._items_threshold: int = 0 
        self._items_collected_for_level: int = 0  
        self._levels_config: Dict = {}
        
        if config:
            self.load_config(config)
    
    @property
    def current_level(self) -> int:
        return self._current_level
    
    @property
    def items_threshold(self) -> int:
        return self._items_threshold
    
    @property
    def items_collected_for_level(self) -> int:
        return self._items_collected_for_level
    
    def load_config(self, config: Dict) -> None:
        super().load_config(config)
        self._levels_config = config.get("levels", {})
        self._update_threshold_for_current_level()
    
    def _update_threshold_for_current_level(self) -> None:
        level_config = self._levels_config.get(str(self._current_level), {})
       
        self._items_threshold = level_config.get("items_required", 5 + (self._current_level - 1) * 2)
        self._items_collected_for_level = 0
    
    def check_level_up_by_items(self, total_items_collected: int) -> bool:
        items_on_current_level = total_items_collected - self._get_total_items_for_previous_levels()
        
        if items_on_current_level >= self._items_threshold:
            self._current_level += 1
            self._update_threshold_for_current_level()
            self.notify_observers("level_up", {
                "level": self._current_level,
                "items_threshold": self._items_threshold
            })
            return True
        return False
    
    def _get_total_items_for_previous_levels(self) -> int:
        total = 0
        for level_num in range(1, self._current_level):
            level_config = self._levels_config.get(str(level_num), {})
            items_required = level_config.get("items_required", 5 + (level_num - 1) * 2)
            total += items_required
        return total
    
    def get_items_collected_on_current_level(self, total_items_collected: int) -> int:
        return total_items_collected - self._get_total_items_for_previous_levels()
    
    def check_level_up(self, score: int) -> bool:
        return False
    
    def get_level_config(self) -> Dict:
        return self._levels_config.get(str(self._current_level), {}).copy()
    
    def get_drop_chance(self) -> float:
        level_config = self.get_level_config()
        base_chance = self._config.get("base_drop_chance", 0.3)
        level_chance = level_config.get("drop_chance", base_chance)
        return min(level_chance + (self._current_level - 1) * 0.05, 0.9)
    
    def get_level_info_tuple(self) -> Tuple[int, int, Dict]:
        return (self._current_level, self._items_threshold, self.get_level_config())

