from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Callable, Dict, Generator, Iterable, List, Tuple

from .board import Board
from .entities import Player
from .game_state import GameState
from .items import (
    BonusFoodItem,
    FoodItem,
    ForbiddenItem,
    PowerUpItem,
)
from .managers import ItemFactory, LevelManager, ScoreManager


class GameOver(Exception):
    pass


@dataclass
class DropConfig:
    width: int
    height: int
    lives: int
    allowed_items: Dict[str, int]
    forbidden_items: set[str]
    drop_rate: int = 1
    drop_chance: float = 0.5
    items_config_path: str | None = None
    levels_config_path: str | None = None


def make_scoring_rule(bonus_every: int = 5) -> Callable[[int], int]:
    counter = 0

    def score_for(points: int) -> int:
        nonlocal counter
        counter += 1
        return points

    return score_for


def item_stream(
    config: DropConfig,
    item_factory: ItemFactory | None = None
) -> Generator[List[FoodItem | ForbiddenItem | PowerUpItem | BonusFoodItem], None, None]:
    if item_factory and item_factory._config:
        symbols_and_types: List[Tuple[str, str]] = [
            (symbol, item_type)
            for item_type in ("food", "forbidden")
            if item_type in item_factory._config
            for symbol in item_factory._config[item_type].keys()
        ]
        
        while True:
            items: List[FoodItem | ForbiddenItem | PowerUpItem | BonusFoodItem] = []
            if random.random() < config.drop_chance:
                for _ in range(config.drop_rate):
                    if symbols_and_types:
                        symbol, item_type = random.choice(symbols_and_types)
                        x = random.randrange(0, config.width)
                        items.append(item_factory.create_random_item(x, 0, item_type, symbol))
            yield items
    else:
        symbols = list(config.allowed_items.keys() | config.forbidden_items)
        while True:
            items: List[FoodItem] = []
            if random.random() < config.drop_chance:
                for _ in range(config.drop_rate):
                    symbol = random.choice(symbols)
                    if symbol in config.forbidden_items:
                        items.append(ForbiddenItem(
                            x=random.randrange(0, config.width),
                            y=0,
                            symbol=symbol,
                            damage=999
                        ))
                    else:
                        items.append(FoodItem(
                            x=random.randrange(0, config.width),
                            y=0,
                            symbol=symbol,
                            points=1
                        ))
            yield items


class Game:
    def __init__(self, config: DropConfig):
        self.config = config
        self.board = Board(config.width, config.height)
        self.game_state = GameState()
        
        self.score_manager = ScoreManager()
        self.level_manager = LevelManager()
        
        self.item_factory: ItemFactory | None = None
        if config.items_config_path:
            from .storage import load_items_config
            items_config = load_items_config(config.items_config_path)
            factory_config: Dict[str, Dict[str, Dict]] = {}
            for item_type, items in items_config.items():
                factory_config[item_type] = items
            self.item_factory = ItemFactory(config=factory_config)
        
        if config.levels_config_path:
            from .storage import load_levels_config
            levels_config = load_levels_config(config.levels_config_path)
            self.level_manager.load_config({
                "levels": levels_config,
                "base_drop_chance": config.drop_chance
            })
        
        
        start_x = config.width // 2
        self.player = Player(start_x, config.height - 1)
        self.player.lives = config.lives
        self.board.forbidden = config.forbidden_items
        self.board.add_player(self.player)
        self._score_rule = make_scoring_rule()
        
        self.score_manager.attach_observer(self._on_score_changed)
        self.level_manager.attach_observer(self._on_level_up)
    
    def _on_score_changed(self, event: str, data: Dict) -> None:
        self.game_state.collected_items.append(data.get("item_type", "unknown"))
    
    def _on_level_up(self, event: str, data: Dict) -> None:
        self.game_state.level = data.get("level", 1)
    
    @property
    def lives(self) -> int:
        return self.player.lives
    
    @property
    def score(self) -> int:
        return self.score_manager.total_score
    
    @property
    def level(self) -> int:
        return self.level_manager.current_level
    
    def _apply_move(self, move: str) -> None:
        if move == "L":
            self.board.move_player(-1)
        elif move == "R":
            self.board.move_player(1)
    
    def _handle_collisions(
        self, 
        missed: Iterable[FoodItem | ForbiddenItem | PowerUpItem | BonusFoodItem]
    ) -> None:
        for item in missed:
            if isinstance(item, ForbiddenItem):
              
                continue

            if isinstance(item, FoodItem) or isinstance(item, BonusFoodItem):
                self.game_state.missed_count += 1
            
    
    def _capture_items(self) -> None:
        pos = (self.player.x, self.player.y) 
        if pos not in self.board.items:
            return
        
        item = self.board.items[pos]
        
        if isinstance(item, ForbiddenItem):
            self.player.lives = 0
            self.board.clear_cell(*pos) 
            raise GameOver("Caught forbidden item - game over!")
        
        if isinstance(item, FoodItem) or isinstance(item, BonusFoodItem):
        
            points = 1
            item.collect()
            self.score_manager.add_points(points, "food")
            self.player.score = self.score_manager.total_score
            self.game_state.update_from_player(self.player)
            self.board.clear_cell(*pos)
        
        
        elif isinstance(item, PowerUpItem):
            points = 1
            item.collect()
            self.score_manager.add_points(points, "powerup")
            self.player.score = self.score_manager.total_score
            
           
            
            self.game_state.update_from_player(self.player)
            self.board.clear_cell(*pos)
        
        items_collected = len([i for i in self.game_state.collected_items if i == "food"])
        self.level_manager.check_level_up_by_items(items_collected)
        
        if self.item_factory is None:
            self.config.drop_chance = self.level_manager.get_drop_chance()
    
    def _update_powerups(self) -> None:
        expired: List[str] = []
        for key, powerup in list(self.game_state.active_powerups.items()):
            if not powerup.tick():
                expired.append(key)
        
        for key in expired:
            if key == "multiplier":
                self.score_manager.set_multiplier(1.0)
            del self.game_state.active_powerups[key]
    
    def _tick(
        self, 
        new_items: List[FoodItem | ForbiddenItem | PowerUpItem | BonusFoodItem],
        move: str | None
    ) -> None:
        if move:
            self._apply_move(move)
        
        self._update_powerups()
        
        missed = self.board.drop_items(new_items)
        self._capture_items()
        self._handle_collisions(missed)
        
        self.game_state.tick_count += 1
        
        if self.game_state.missed_count >= 3:
            raise GameOver("Пропущено 3 предмета - гра закінчена!")
        
        if self.player.lives <= 0:
            raise GameOver("Out of lives - game over!")
    
    def run(
        self, 
        moves: Iterable[str] | None = None, 
        max_ticks: int = 20
    ) -> dict:
        move_iter = iter(moves) if moves is not None else itertools.repeat("")
        
        current_drop_chance = (
            self.level_manager.get_drop_chance() 
            if self.level_manager._config 
            else self.config.drop_chance
        )
        
        current_config = DropConfig(
            width=self.config.width,
            height=self.config.height,
            lives=self.config.lives,
            allowed_items=self.config.allowed_items,
            forbidden_items=self.config.forbidden_items,
            drop_rate=self.config.drop_rate,
            drop_chance=current_drop_chance,
            items_config_path=self.config.items_config_path,
            levels_config_path=self.config.levels_config_path
        )
        
        stream = item_stream(current_config, self.item_factory)
        
        for tick in range(max_ticks):
            move = next(move_iter, "")
            new_items = next(stream)
            self._tick(new_items, move)
        
        stats_tuple = self.score_manager.get_stats_tuple()
        level_info_tuple = self.level_manager.get_level_info_tuple()
        
        return {
            "score": self.score_manager.total_score,
            "lives": self.player.lives,
            "level": self.level_manager.current_level,
            "stats": stats_tuple,
            "level_info": level_info_tuple,
            "game_state": self.game_state.to_dict(),
        }
    
    def get_statistics(self) -> Dict[str, int | float | Dict]:
        return {
            **self.game_state.get_statistics_summary(),
            "score_manager_stats": self.score_manager.stats,
            "level": self.level_manager.current_level,
            "items_on_board": len(self.board.items),
            "item_positions": self.board.get_item_positions(),  
        }
