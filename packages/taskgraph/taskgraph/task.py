import inspect
from typing import Callable, Generator, Set
from taskgraph.context import GraphContext
from taskgraph.task_context import TaskContextManager


class TaskState:
    def __init__(self):
        self.data = {}


class TaskNode:
    def __init__(self, name: str, fn: Callable, kwargs, task_id: str = None):
        self.name = name
        self.task_id = task_id or name
        self.fn = fn
        self.kwargs = kwargs

        self.state = TaskState()

        self.upstream: Set["TaskNode"] = set()
        self.downstream: Set["TaskNode"] = set()

    def set_upstream(self, node: "TaskNode"):
        self.upstream.add(node)
        node.downstream.add(self)

    def execute_single(self, **resolved_kwargs):
        """Execute this task with resolved input values"""
        current_graph = GraphContext.current()
        
        with TaskContextManager(
            task_id=self.task_id, 
            task_state=current_graph.graph_state.setdefault(self.task_id, {}), 
            global_state=current_graph.global_state
        ):
            return self.fn(**resolved_kwargs)

    def execute(self) -> Generator:
        """Legacy method for backward compatibility - should not be used in new model"""
        raise NotImplementedError("TaskNode.execute() is deprecated. Use execute_single() instead.")


class SourceNode(TaskNode):
    def __init__(self, name: str, fn: Callable, kwargs, task_id: str = None):
        super().__init__(name, fn, kwargs, task_id)

    def generate(self):
        """Generate values from this source"""
        current_graph = GraphContext.current()
        
        with TaskContextManager(
            task_id=self.task_id,
            task_state=current_graph.graph_state.setdefault(self.task_id, {}),
            global_state=current_graph.global_state
        ):
            result = self.fn(**self.kwargs)
            if inspect.isgenerator(result):
                yield from result
            else:
                raise ValueError(f"Source function '{self.name}' must return a generator")
