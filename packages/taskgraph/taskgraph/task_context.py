import contextvars
from taskgraph.exceptions import TaskContextError

_current_task_context: contextvars.ContextVar[dict | None] = contextvars.ContextVar("_current_task_context", default=None)


def get_current_task_context() -> dict:
    ctx = _current_task_context.get()
    if ctx is None:
        raise TaskContextError("No active task context")
    return ctx


def get_global_state() -> dict:
    """Get the global state accessible to all tasks in the current graph."""
    ctx = get_current_task_context()
    return ctx["global_state"]


def set_global_state(key: str, value):
    """Set a value in the global state."""
    global_state = get_global_state()
    global_state[key] = value
    
    if global_state.get(key) != value:
        raise RuntimeError(f"Failed to set global state: {key}={value}")


def get_global_state_value(key: str, default=None):
    """Get a specific value from the global state."""
    global_state = get_global_state()
    return global_state.get(key, default)


class TaskContextManager:
    def __init__(self, task_id: str, task_state: dict, global_state: dict):
        self.task_id = task_id
        self.task_state = task_state
        if global_state is None:
            raise ValueError("global_state cannot be None")
        self.global_state = global_state
        self._token = None

    def __enter__(self):
        context = {
            "task_id": self.task_id, 
            "task_state": self.task_state,
            "global_state": self.global_state
        }
        self._token = _current_task_context.set(context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _current_task_context.reset(self._token)
