import itertools
from typing import List
from taskgraph.task import TaskNode, SourceNode
from taskgraph.decorators import task

# Note: expand_task is less relevant in the new model since sources 
# naturally distribute to multiple downstream tasks
def expand_task(task_node: TaskNode, n: int) -> List[TaskNode]:
    """
    DEPRECATED: This function is less relevant in the new source/task model.
    In the new model, sources naturally distribute to multiple downstream tasks.
    
    If you need to split processing, create multiple task nodes that depend 
    on the same upstream node instead.
    """
    raise DeprecationWarning(
        "expand_task is deprecated in the new source/task model. "
        "Create multiple task nodes that depend on the same upstream node instead."
    )
