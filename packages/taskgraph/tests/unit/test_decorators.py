import pytest
from taskgraph.decorators import task, source, graph
from taskgraph.task import TaskNode, SourceNode
from taskgraph.graph import Graph
from taskgraph.context import GraphContext
from taskgraph.exceptions import NoTaskIdError, DuplicateTaskIdError


class TestTaskDecorator:
    def test_task_decorator_creates_task_node(self):
        """Test @task decorator creates TaskNode"""
        @task
        def test_task(value):
            return value * 2
        
        # Create a graph context for the decorator
        graph = Graph("test")
        GraphContext.push(graph)
        try:
            node = test_task(task_id="test", value=5)
            assert isinstance(node, TaskNode)
            assert node.name == "test_task"
            assert node.task_id == "test"
        finally:
            GraphContext.pop()

    def test_task_decorator_no_task_id_raises_error(self):
        """Test @task raises error when task_id missing"""
        @task
        def test_task():
            pass
        
        graph = Graph("test")
        GraphContext.push(graph)
        try:
            with pytest.raises(NoTaskIdError):
                test_task()
        finally:
            GraphContext.pop()

    def test_task_decorator_adds_to_graph(self):
        """Test @task adds node to current graph"""
        @task
        def test_task():
            pass
        
        graph = Graph("test")
        GraphContext.push(graph)
        try:
            node = test_task(task_id="test")
            assert len(graph.nodes) == 1
            assert graph.nodes[0] == node
        finally:
            GraphContext.pop()

    def test_task_decorator_builds_dependencies(self):
        """Test @task builds dependencies from kwargs"""
        @task
        def task1():
            pass
            
        @task 
        def task2(upstream):
            pass
        
        graph = Graph("test")
        GraphContext.push(graph)
        try:
            node1 = task1(task_id="task1")
            node2 = task2(task_id="task2", upstream=node1)
            
            assert node1 in node2.upstream
            assert node2 in node1.downstream
        finally:
            GraphContext.pop()


class TestSourceDecorator:
    def test_source_decorator_creates_source_node(self):
        """Test @source decorator creates SourceNode"""
        @source
        def test_source():
            yield 1
        
        graph = Graph("test")
        GraphContext.push(graph)
        try:
            node = test_source(task_id="test")
            assert isinstance(node, SourceNode)
            assert node.name == "test_source"
            assert node.task_id == "test"
        finally:
            GraphContext.pop()

    def test_source_decorator_no_task_id_raises_error(self):
        """Test @source raises error when task_id missing"""
        @source
        def test_source():
            yield 1
        
        graph = Graph("test")
        GraphContext.push(graph)
        try:
            with pytest.raises(NoTaskIdError):
                test_source()
        finally:
            GraphContext.pop()


class TestGraphDecorator:
    def test_graph_decorator_creates_graph(self):
        """Test @graph decorator creates Graph"""
        @graph
        def test_graph():
            pass
        
        result = test_graph()
        assert isinstance(result, Graph)
        assert result.name == "test_graph"

    def test_graph_decorator_with_kwargs(self):
        """Test @graph updates global_state with kwargs"""
        @graph
        def test_graph(param1, param2):
            pass
        
        result = test_graph(param1="value1", param2="value2")
        assert result.global_state["param1"] == "value1"
        assert result.global_state["param2"] == "value2"

    def test_graph_decorator_with_hooks(self):
        """Test @graph with execution hooks"""
        def hook1(g):
            pass
        def hook2(g):
            pass
        
        @graph(on_execute_end=[hook1, hook2])
        def test_graph():
            pass
        
        result = test_graph()
        assert len(result._on_execute_end_hooks) == 2
        assert hook1 in result._on_execute_end_hooks
        assert hook2 in result._on_execute_end_hooks

    def test_graph_decorator_with_single_hook(self):
        """Test @graph with single execution hook"""
        def hook(g):
            pass
        
        @graph(on_execute_end=hook)
        def test_graph():
            pass
        
        result = test_graph()
        assert len(result._on_execute_end_hooks) == 1
        assert hook in result._on_execute_end_hooks

    def test_graph_decorator_with_initial_states(self):
        """Test @graph with initial states"""
        graph_state = {"task1": {"key": "value"}}
        global_state = {"global": "value"}
        
        @graph(graph_state=graph_state, global_state=global_state)
        def test_graph():
            pass
        
        result = test_graph()
        assert result.graph_state == graph_state
        assert result.global_state == global_state

    def test_duplicate_task_id_detection(self):
        """Test duplicate task_id detection within graph"""
        @task
        def task1():
            pass
            
        @task
        def task2():
            pass
        
        @graph
        def duplicate_graph():
            task1(task_id="duplicate")
            task2(task_id="duplicate")  # Should fail
        
        with pytest.raises(DuplicateTaskIdError):
            duplicate_graph()
