from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .entities import Player
from .items import PowerUpItem


@dataclass
class GameState:
    
    score: int = 0
    lives: int = 3
    level: int = 1
    tick_count: int = 0
    missed_count: int = 0
    collected_items: List[str] = field(default_factory=list)
    active_powerups: Dict[str, PowerUpItem] = field(default_factory=dict)
    
    def as_tuple(self) -> Tuple[int, int, int, int, int, Tuple[str, ...], Tuple[str, ...]]:
        return (
            self.score,
            self.lives,
            self.level,
            self.tick_count,
            self.missed_count,
            tuple(self.collected_items),
            tuple(self.active_powerups.keys())
        )
    
    def from_tuple(self, data: Tuple) -> None:
        (self.score, self.lives, self.level, self.tick_count, 
         self.missed_count, items, powerups) = data
        self.collected_items = list(items)
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "lives": self.lives,
            "level": self.level,
            "tick_count": self.tick_count,
            "missed_count": self.missed_count,
            "collected_items": self.collected_items[:],  
            "active_powerups": list(self.active_powerups.keys())
        }
    
    def from_dict(self, data: Dict) -> None:
        self.score = data.get("score", 0)
        self.lives = data.get("lives", 3)
        self.level = data.get("level", 1)
        self.tick_count = data.get("tick_count", 0)
        self.missed_count = data.get("missed_count", 0)
        self.collected_items = data.get("collected_items", [])
    
    def update_from_player(self, player: Player) -> None:
        self.score = player.score
        self.lives = player.lives
    
    def get_recent_items(self, count: int = 10) -> List[str]:
        return self.collected_items[-count:] if self.collected_items else []
    
    def get_statistics_summary(self) -> Dict[str, int | float]:
        return {
            "total_score": self.score,
            "remaining_lives": self.lives,
            "current_level": self.level,
            "items_collected": len(self.collected_items),
            "items_missed": self.missed_count,
            "success_rate": (
                len(self.collected_items) / (len(self.collected_items) + self.missed_count)
                if (len(self.collected_items) + self.missed_count) > 0
                else 0.0
            )
        }

