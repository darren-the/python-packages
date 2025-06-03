import json
import pickle
from typing import List, Callable
from taskgraph.context import GraphContext
from taskgraph.task import TaskNode


class Graph:
    def __init__(self, name: str, graph_state: dict[str, dict] = None, global_state: dict = None):
        self.name = name
        self.nodes: List[TaskNode] = []
        self.graph_state = graph_state or {}
        self.global_state = global_state or {}
        self._on_execute_end_hooks: List[Callable] = []

    @property
    def state(self) -> dict:
        return  {
            "graph_state": self.graph_state,
            "global_state": self.global_state
        }
    
    @state.setter
    def state(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("State must be a dictionary")
        self.graph_state = value.get("graph_state", {})
        self.global_state = value.get("global_state", {})

    def add_node(self, node: TaskNode):
        self.nodes.append(node)

    def add_on_execute_end_hook(self, hook: Callable):
        """
        Add a hook function to be called when graph execution finishes.
        Hook function signature: hook(graph: Graph) -> None
        """
        self._on_execute_end_hooks.append(hook)

    def remove_on_execute_end_hook(self, hook: Callable):
        """Remove a previously added hook"""
        if hook in self._on_execute_end_hooks:
            self._on_execute_end_hooks.remove(hook)

    def clear_on_execute_end_hooks(self):
        """Clear all execution end hooks"""
        self._on_execute_end_hooks.clear()

    def to_graphviz(self) -> str:
        lines = [f"digraph {self.name} {{"]
        for node in self.nodes:
            lines.append(f'  "{node.task_id}";')
            for upstream in node.upstream:
                lines.append(f'  "{upstream.task_id}" -> "{node.task_id}";')
        lines.append("}")
        return "\n".join(lines)

    def to_json(self, pretty: bool = False) -> str:
        sorted_nodes = sorted(self.nodes, key=lambda node: node.task_id)
        edges = []
        for node in sorted_nodes:
            for upstream_node in node.upstream:
                edges.append({
                    "from": upstream_node.task_id,
                    "to": node.task_id
                })
        graph_data = {
            "graph": self.name,
            "nodes": [node.task_id for node in sorted_nodes],
            "edges": edges
        }
        return json.dumps(graph_data, indent=2 if pretty else None)

    def execute(self):
        """Execute the graph and call end hooks when finished"""
        GraphContext.push(self)
        try:
            # assumes linear run. Add topological sort if needed
            for node in self.nodes:
                for _ in node.execute():
                    pass
        finally:
            GraphContext.pop()
            self._call_execute_end_hooks()

    def _call_execute_end_hooks(self):
        """Call all registered execute end hooks"""
        for hook in self._on_execute_end_hooks:
            try:
                hook(self)
            except Exception as e:
                print(f"Warning: Hook {hook.__name__} failed with error: {e}")
    
    # def save_state(self, path: str):
    #     with open(path, "wb") as f:
    #         pickle.dump(self.state, f)

    # def load_state(self, path: str):
    #     with open(path, "rb") as f:
    #         state_data = pickle.load(f)
    #         self.graph_state = state_data.get("graph_state", {})
    #         self.global_state = state_data.get("global_state", {})
