from __future__ import annotations

from pathlib import Path

from food_drop import Game, GameOver, load_config_from_text
from food_drop.game import DropConfig
from food_drop.io_utils import print_board
from food_drop.storage import load_scores_text, save_scores_text, save_state_binary

HIGH_SCORE = 0


def parse_config(path: str) -> DropConfig:
    cfg = load_config_from_text(path)
    allowed_pairs = cfg.get("allowed", "")
    allowed = {
        symbol: int(points)
        for symbol, points in (
            pair.split(":") for pair in allowed_pairs.split(",") if pair
        )
    }
   
    forbidden = {item for item in cfg.get("forbidden", "").split(",") if item}
    return DropConfig(
        width=int(cfg.get("width", 7)),
        height=int(cfg.get("height", 6)),
        lives=int(cfg.get("lives", 3)),
        allowed_items=allowed,
        forbidden_items=forbidden,
        drop_rate=int(cfg.get("drop_rate", 1)),
        drop_chance=float(cfg.get("drop_chance", 0.3)),
        items_config_path=cfg.get("items_config", "config/items_config.txt"),
        levels_config_path=cfg.get("levels_config", "config/levels_config.txt"),
    )


def input_move(prompt: str, /, *, allowed=("A", "D", "", "Q")) -> str:
    def normalize(s):
        return s.strip().upper()

    while True:
        raw = input(prompt)
        move = normalize(raw)
        if move == "":
            return ""
        if move in allowed:
            return move
        print("Невірна клавіша, використовуйте A (вліво), D (вправо) або Q (вихід).")


def demo_game() -> None:
    global HIGH_SCORE

    config_path = Path("config/sample_config.txt")
    config = parse_config(str(config_path))
    game = Game(config)

    print("=== Food Drop ===")
    print("Керування: A – вліво, D – вправо, Enter – стояти на місці, Q – вийти.")
    print()

    if game.item_factory and getattr(game.item_factory, "_config", None):
        print("Символи предметів:")
        for item_type, items in game.item_factory._config.items():
            for sym, data in items.items():
                name = data.get("name", "")
                points = data.get("points") if item_type in ("food", "bonus", "powerup") else data.get("damage")
                type_label = item_type
                extra = f"{points} pts" if item_type in ("food","bonus","powerup") else f"damage:{points}"
                forbidden_mark = " (ЗАБОРОНЕНО)" if sym in config.forbidden_items else ""
                print(f"  {sym} — {name} [{type_label}] {extra}{forbidden_mark}")
        print()
        if config.forbidden_items:
            print(f"Примітка: {' '.join(sorted(config.forbidden_items))} — заборонено ловити; якщо зловите, гра завершиться; пропуск безпечний.")
            print()

    tick = 0
    while True:
        tick += 1
        print(f"\nХід #{tick}")
        items_collected = len([i for i in game.game_state.collected_items if i == "food"])
        items_needed = game.level_manager.items_threshold
        items_on_level = game.level_manager.get_items_collected_on_current_level(items_collected)
        print(f"Рівень: {game.level}")
        print(f"Зібрано предметів: {items_collected} (на рівні: {items_on_level}/{items_needed})")
        print(f"Пропущено предметів: {game.game_state.missed_count}/3")
        print_board(game.board)

        move_key = input_move("Ваш хід (A/D/Enter/Q): ")
        if move_key == "Q":
            print("Ви вийшли з гри.")
            break

        direction = ""
        if move_key == "A":
            direction = "L"
        elif move_key == "D":
            direction = "R"

        try:
            game.run(moves=[direction], max_ticks=1)
        except GameOver as exc:
            print(f"Гру завершено: {exc}")
            print("Кінцеве поле:")
            print_board(game.board)
            break

    final_score = game.score
    if final_score > HIGH_SCORE:
        HIGH_SCORE = final_score
    
    stats = game.get_statistics()
    print(f"\nВаш підсумковий рахунок: {final_score}, рекорд: {HIGH_SCORE}")
    print(f"Рівень досягнуто: {stats.get('current_level', 1)}")
    print(f"Предметів зібрано: {stats.get('items_collected', 0)}")
    print(f"Предметів пропущено: {stats.get('items_missed', 0)}")
    print(f"Успішність: {stats.get('success_rate', 0.0):.1%}")
    
    scores_file = "saves/scores.txt"
    save_scores_text(scores_file, ("Player", final_score), ("HighScore", HIGH_SCORE))
    print(f"Результати збережено у {scores_file}")

    score_history = load_scores_text(scores_file)
    save_state_binary("saves/last_state.bin", score_history)
    print("Двоїчний файл збережено у saves/last_state.bin")


if __name__ == "__main__":
    demo_game()

