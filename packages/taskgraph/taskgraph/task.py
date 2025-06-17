import inspect
from typing import Callable, Generator, Iterable, Set
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

    def execute(self) -> Generator:
        resolved_kwargs = {k: (v.execute() if isinstance(v, TaskNode) else v) for k, v in self.kwargs.items()}

        current_graph = GraphContext.current()

        def wrap_generator_with_context(result):
            with TaskContextManager(
                task_id=self.task_id, 
                task_state=current_graph.graph_state.setdefault(self.task_id, {}), 
                global_state=current_graph.global_state
            ):
                for item in result:
                    yield item

        result = self.fn(**resolved_kwargs)

        if inspect.isgenerator(result) or isinstance(result, Iterable):
            return wrap_generator_with_context(result)
        else:
            def noop_generator():
                yield result
            return wrap_generator_with_context(noop_generator())
