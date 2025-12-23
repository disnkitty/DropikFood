from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Dict, Tuple


def load_config_from_text(path: str) -> Dict[str, str]:
    config: Dict[str, str] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        config[key.strip()] = value.strip()
    return config


def save_scores_text(path: str, *scores: Tuple[str, int]) -> None:
    lines = [f"{name}:{points}" for name, points in scores]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def load_scores_text(path: str) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", maxsplit=1)
        scores[name] = int(value)
    return scores


def save_state_binary(path: str, state: dict) -> None:
    Path(path).write_bytes(pickle.dumps(state))


def load_state_binary(path: str) -> dict:
    return pickle.loads(Path(path).read_bytes())


def save_state_json(path: str, state: dict) -> None:
    Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_items_config(path: str) -> Dict[str, Dict[str, str | int]]:
    items_config: Dict[str, Dict[str, Dict[str, str | int]]] = {}
    
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        parts = line.split(":")
        if len(parts) < 4:
            continue
        
        item_type = parts[0].strip()
        symbol = parts[1].strip()
        name = parts[2].strip()
        points_or_damage = int(parts[3].strip()) if parts[3].strip().isdigit() else 0
        duration = int(parts[4].strip()) if len(parts) > 4 and parts[4].strip().isdigit() else 0
        effect = parts[5].strip() if len(parts) > 5 else "normal"
        
        if item_type not in items_config:
            items_config[item_type] = {}
        
        items_config[item_type][symbol] = {
            "name": name,
            "symbol": symbol,
            "points" if item_type in ("food", "bonus", "powerup") else "damage": points_or_damage,
            "duration": duration,
            "effect": effect
        }
    
    return items_config


def load_levels_config(path: str) -> Dict[str, Dict[str, int | float | str]]:
    levels_config: Dict[str, Dict[str, int | float | str]] = {}
    
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        parts = line.split(":")
        if len(parts) < 3:
            continue
        
        level = parts[0].strip()
        items_required = int(parts[1].strip()) if parts[1].strip().isdigit() else 5
        drop_chance = float(parts[2].strip()) if parts[2].strip().replace(".", "").isdigit() else 0.3
        description = parts[3].strip() if len(parts) > 3 else f"Level {level}"
        
        levels_config[level] = {
            "items_required": items_required,
            "drop_chance": drop_chance,
            "description": description
        }
    
    return levels_config