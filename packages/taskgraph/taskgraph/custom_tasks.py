import itertools
from typing import List
from taskgraph.task import TaskNode
from taskgraph.decorators import task


def expand_task(task_node: TaskNode, n: int) -> List[TaskNode]:
    """
    Splits a generator output from one task into multiple via `tee`,
    each wrapped in a new task node.
    """
    def make_expansion(index):
        @task
        def expand(source):
            iters = itertools.tee(source, n)
            yield from iters[index]
        return expand(task_node, task_id=f"expand_{index}")

    return [make_expansion(i) for i in range(n)]
