from __future__ import annotations

from typing import Callable, TypeVar

T = TypeVar("T")


def log_action(recorder: list[str]) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        return func

    return decorator


def timeit(func: Callable[..., T]) -> Callable[..., T]:
    return func

