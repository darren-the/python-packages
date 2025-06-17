import functools
from typing import Callable, TypeVar, ParamSpec, Union, List, overload
from taskgraph.context import GraphContext
from taskgraph.task import TaskNode
from taskgraph.graph import Graph
from taskgraph.exceptions import DuplicateTaskIdError, NoTaskIdError

P = ParamSpec('P')
R = TypeVar('R')

@overload
def graph(fn: Callable[P, R]) -> Callable[P, Graph]: ...

@overload
def graph(
    *,
    on_execute_end: Union[Callable[[Graph], None], List[Callable[[Graph], None]]] = None,
    graph_state: dict = None,
    global_state: dict = None
) -> Callable[[Callable[P, R]], Callable[P, Graph]]: ...

def graph(
    fn: Callable = None,
    *,
    on_execute_end: Union[Callable, List[Callable]] = None,
    graph_state: dict = None,
    global_state: dict = None
):
    """
    Decorator for graph functions with optional parameters.
    
    Usage:
        @graph
        def my_graph(): ...
        
        @graph(on_execute_end=my_hook)
        def my_graph(): ...
        
        @graph(on_execute_end=[hook1, hook2])
        def my_graph(): ...
    """
    def decorator(func: Callable) -> Callable[..., Graph]:
        @functools.wraps(func)
        def wrapper(**kwargs) -> Graph:
            g = Graph(
                name=func.__name__, 
                graph_state=graph_state or {}, 
                global_state=global_state or {}
            )
            
            # add hooks if provided
            if on_execute_end is not None:
                if callable(on_execute_end):
                    g.add_on_execute_end_hook(on_execute_end)
                elif isinstance(on_execute_end, (list, tuple)):
                    for hook in on_execute_end:
                        if callable(hook):
                            g.add_on_execute_end_hook(hook)
            
            GraphContext.push(g)
            try:
                func(**kwargs)
            finally:
                GraphContext.pop()
            return g
        return wrapper
    
    if fn is None:
        return decorator  # called as @graph(...)
    else:
        return decorator(fn)  # called as @graph


def task(fn: Callable[P, R]) -> Callable[P, TaskNode]:
    @functools.wraps(fn)
    def wrapper(**kwargs: P.kwargs):
        current_graph = GraphContext.current()

        task_id = kwargs.pop("task_id", None)
        if task_id is None:
            raise NoTaskIdError(f"Task '{fn.__name__}' requires a 'task_id' argument.")
        if task_id in [node.task_id for node in current_graph.nodes]:
            raise DuplicateTaskIdError(f"Duplicate task_id '{task_id}' detected in graph '{current_graph.name}'")
        name = fn.__name__
        node = TaskNode(name=name, fn=fn, kwargs=kwargs, task_id=task_id)

        current_graph.add_node(node)

        for val in kwargs.values():
            if isinstance(val, TaskNode):
                node.set_upstream(val)

        return node
    return wrapper
