import json
import logging
from typing import List, Callable, Dict, Set
from collections import deque
from taskgraph.context import GraphContext
from taskgraph.task import TaskNode, SourceNode
from taskgraph.exceptions import TaskContextError


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

    def update_state(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError("State must be a dictionary")
        self.graph_state.update(value.get("graph_state", {}))
        self.global_state.update(value.get("global_state", {}))

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
            node_type = "source" if isinstance(node, SourceNode) else "task"
            lines.append(f'  "{node.task_id}" [label="{node.task_id}\\n({node_type})"];')
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
        
        nodes_data = []
        for node in sorted_nodes:
            nodes_data.append({
                "id": node.task_id,
                "type": "source" if isinstance(node, SourceNode) else "task"
            })
            
        graph_data = {
            "graph": self.name,
            "nodes": nodes_data,
            "edges": edges
        }
        return json.dumps(graph_data, indent=2 if pretty else None)

    def _get_source_nodes(self) -> List[SourceNode]:
        """Get all source nodes in the graph"""
        return [node for node in self.nodes if isinstance(node, SourceNode)]

    def _topological_sort_from_source(self, source_node: SourceNode) -> List[TaskNode]:
        """
        Get topological ordering of nodes reachable from the given source node
        """
        visited = set()
        result = []
        
        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            
            # Visit all downstream nodes first
            for downstream in node.downstream:
                dfs(downstream)
            
            result.append(node)
        
        dfs(source_node)
        return list(reversed(result))

    def _propagate_from_source(self, source_node: SourceNode):
        """
        Execute the subgraph starting from a source node, propagating each generated value
        """
        # Get execution order for this source's subgraph
        execution_order = self._topological_sort_from_source(source_node)
        
        # Generate values from source and propagate each one
        for value in source_node.generate():
            self._propagate_value(source_node, value, execution_order)

    def _propagate_value(self, source_node: SourceNode, value, execution_order: List[TaskNode]):
        """
        Propagate a single value through the execution order
        """
        # Track outputs from each node for this value
        node_outputs = {source_node.task_id: value}
        
        # Execute each node in topological order
        for node in execution_order:
            if node == source_node:
                continue  # Source already produced its value
                
            # Skip nodes that don't depend on this source
            if not self._is_reachable_from(node, source_node):
                continue
            
            # Resolve input arguments for this node
            resolved_kwargs = {}
            for param_name, param_value in node.kwargs.items():
                if isinstance(param_value, (TaskNode, SourceNode)):
                    # This parameter comes from another node's output
                    if param_value.task_id not in node_outputs:
                        # This shouldn't happen with proper topological ordering
                        raise RuntimeError(f"Node {node.task_id} depends on {param_value.task_id} but no output available")
                    resolved_kwargs[param_name] = node_outputs[param_value.task_id]
                else:
                    # This is a literal value
                    resolved_kwargs[param_name] = param_value
            
            # Execute the node
            try:
                result = node.execute_single(**resolved_kwargs)
                node_outputs[node.task_id] = result
            except Exception as e:
                raise RuntimeError(f"Error executing node {node.task_id}: {e}") from e

    def _is_reachable_from(self, target_node: TaskNode, source_node: SourceNode) -> bool:
        """
        Check if target_node is reachable from source_node by following downstream edges
        """
        visited = set()
        queue = deque([source_node])
        
        while queue:
            current = queue.popleft()
            if current == target_node:
                return True
            if current in visited:
                continue
            visited.add(current)
            queue.extend(current.downstream)
        
        return False

    def execute(self):
        """Execute the graph using the new source-driven model"""
        GraphContext.push(self)
        try:
            # Find all source nodes
            source_nodes = self._get_source_nodes()
            
            if not source_nodes:
                raise ValueError("Graph has no source nodes. Add at least one @source decorated function.")
            
            # Execute each source's subgraph
            for source_node in source_nodes:
                self._propagate_from_source(source_node)
                
        finally:
            GraphContext.pop()
            self._call_execute_end_hooks()

    def _call_execute_end_hooks(self):
        """Call all registered execute end hooks"""
        for hook in self._on_execute_end_hooks:
            try:
                hook(self)
            except TaskContextError as e:
                raise TaskContextError(
                    f"Task context was accessed inside the hook '{hook.__name__}'. "
                    "However, the graph instance parameter can be used to access context directly."
                )
            except Exception as e:
                raise
