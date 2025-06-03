from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from taskgraph.graph import Graph


class GraphContext:
    _current: List["Graph"] = []

    @classmethod
    def push(cls, graph: "Graph"):
        cls._current.append(graph)

    @classmethod
    def pop(cls):
        cls._current.pop()

    @classmethod
    def current(cls) -> "Graph":
        if not cls._current:
            raise RuntimeError("No active graph context.")
        return cls._current[-1]
