class TaskContextError(RuntimeError):
    """Errors related to the task context."""

class DuplicateTaskIdError(ValueError):
    """Raised when multiple tasks have the same task_id."""

class NoTaskIdError(ValueError):
    """Raised when a task has no task_id."""
    