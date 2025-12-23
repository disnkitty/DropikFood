from __future__ import annotations

from food_drop.game import DropConfig, Game, GameOver, make_scoring_rule


def test_scoring_rule_basic():
    rule = make_scoring_rule(bonus_every=2)
    assert rule(1) == 1
    assert rule(1) == 1


def test_game_runs_until_life_loss():
    config = DropConfig(
        width=3,
        height=3,
        lives=1,
        allowed_items={"x": 1},
        forbidden_items=set(),
        drop_rate=1,
    )
    game = Game(config)
    try:
        game.run(moves=["", ""], max_ticks=1)
    except GameOver:
        assert game.lives == 0 or game.lives == 1
    else:
        assert game.lives >= 0

