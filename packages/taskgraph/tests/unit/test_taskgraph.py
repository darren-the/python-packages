import pytest
from taskgraph.decorators import task, graph
from taskgraph.task_context import (
    get_current_task_context,
    set_global_state,
    get_global_state_value,
    get_global_state
)
from taskgraph.graph import Graph
from taskgraph.exceptions import TaskContextError, DuplicateTaskIdError, NoTaskIdError


def test_basic_graph():
    test_output = []
    @task
    def task_a():
        for a in range(3):
            yield a
    @task
    def task_b(iterable_a):
        for a in iterable_a:
            test_output.append(a * 2)
    @graph
    def basic_graph():
        a = task_a(task_id='task_a')
        b = task_b(task_id='task_b', iterable_a=a)
    graph_instance = basic_graph()
    graph_instance.execute()
    assert test_output == [0, 2, 4]
    assert list(graph_instance.nodes[0].downstream)[0] == graph_instance.nodes[1]
    assert list(graph_instance.nodes[1].upstream)[0] == graph_instance.nodes[0]


def test_task_context():
    @task
    def task_a():
        ctx = get_current_task_context()
        for a in range(3):
            ctx["task_state"]["a_value"] = a
            yield a
    @graph
    def basic_graph():
        a = task_a(task_id='task_a')
    graph_instance = basic_graph()
    graph_instance.execute()
    assert graph_instance.graph_state == {'task_a': {'a_value': 2}}


def test_task_context_no_gen():
    """Task context is only accessible in generator-type tasks."""
    @task
    def task_a():
        x = "hello world"
        set_global_state("hello", x)
        return x
    @graph
    def basic_graph():
        a = task_a(task_id="task_a")
    graph_instance = basic_graph()
    with pytest.raises(TaskContextError):
        graph_instance.execute()


def test_global_state():
    test_output = []
    @task
    def task_a():
        for a in range(3):
            set_global_state("a_value", a)
            yield a
    @task
    def task_b(iterable_a):
        for a in iterable_a:
            a_value = get_global_state_value("a_value")
            test_output.append(a_value)
    @graph
    def basic_graph():
        a = task_a(task_id='task_a')
        b = task_b(task_id='task_b', iterable_a=a)
    graph_instance = basic_graph()
    graph_instance.execute()
    assert test_output == [0, 1, 2]


def test_execute_end_hook():
    test_output = []
    @task
    def task_a():
        for a in range(3):
            set_global_state("a_value", a)
            yield a
    def basic_hook(graph_instance: Graph):
        test_output.append(graph_instance.global_state["a_value"])
    @graph(on_execute_end=basic_hook)
    def basic_graph():
        a = task_a(task_id='task_a')
    graph_instance = basic_graph()
    graph_instance.execute()
    assert test_output == [2]


def test_execute_end_hook_no_context():
    def basic_hook(graph_instance: Graph):
        get_global_state()
    @graph(on_execute_end=basic_hook)
    def basic_graph():
        pass
    graph_instance = basic_graph()
    with pytest.raises(TaskContextError):
        graph_instance.execute()


def test_no_task_id():
    @task
    def task_a():
        for a in range(3):
            yield a
    @graph
    def basic_graph():
        a = task_a()
    with pytest.raises(NoTaskIdError):
        graph_instance = basic_graph()


def test_duplicate_task_id():
    @task
    def task_a():
        pass
    @task
    def task_b():
        pass
    @graph
    def basic_graph():
        a = task_a(task_id='task_a')
        b = task_b(task_id='task_a')

    with pytest.raises(DuplicateTaskIdError):
        graph_instance = basic_graph()
