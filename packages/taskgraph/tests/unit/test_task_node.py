import pytest
from taskgraph.task import TaskNode, SourceNode
from taskgraph.context import GraphContext
from taskgraph.graph import Graph
from taskgraph.task_context import TaskContextManager


class TestTaskNode:
    def test_task_node_creation(self):
        """Test TaskNode constructor sets attributes correctly"""
        def dummy_fn():
            return "test"
        
        kwargs = {"param1": "value1", "param2": 42}
        node = TaskNode("test_task", dummy_fn, kwargs, "test_id")
        
        assert node.name == "test_task"
        assert node.task_id == "test_id"
        assert node.fn == dummy_fn
        assert node.kwargs == kwargs
        assert len(node.upstream) == 0
        assert len(node.downstream) == 0

    def test_task_node_default_task_id(self):
        """Test TaskNode uses name as default task_id"""
        def dummy_fn():
            pass
        
        node = TaskNode("test_task", dummy_fn, {})
        assert node.task_id == "test_task"

    def test_set_upstream_single(self):
        """Test setting single upstream dependency"""
        def fn1():
            pass
        def fn2():
            pass
        
        node1 = TaskNode("task1", fn1, {}, "id1")
        node2 = TaskNode("task2", fn2, {}, "id2")
        
        node2.set_upstream(node1)
        
        assert node1 in node2.upstream
        assert node2 in node1.downstream
        assert len(node2.upstream) == 1
        assert len(node1.downstream) == 1

    def test_set_upstream_multiple(self):
        """Test setting multiple upstream dependencies"""
        def fn1():
            pass
        def fn2():
            pass
        def fn3():
            pass
        
        node1 = TaskNode("task1", fn1, {}, "id1")
        node2 = TaskNode("task2", fn2, {}, "id2")
        node3 = TaskNode("task3", fn3, {}, "id3")
        
        node3.set_upstream(node1)
        node3.set_upstream(node2)
        
        assert node1 in node3.upstream
        assert node2 in node3.upstream
        assert node3 in node1.downstream
        assert node3 in node2.downstream
        assert len(node3.upstream) == 2

    def test_execute_single_with_context(self):
        """Test execute_single creates proper task context"""
        executed_context = None
        
        def test_fn(value):
            nonlocal executed_context
            from taskgraph.task_context import get_current_task_context
            executed_context = get_current_task_context()
            return value * 2
        
        node = TaskNode("test", test_fn, {}, "test_id")
        
        # Mock graph context
        graph = Graph("test_graph")
        graph.graph_state = {"test_id": {"state_key": "state_value"}}
        graph.global_state = {"global_key": "global_value"}
        
        GraphContext.push(graph)
        try:
            result = node.execute_single(value=5)
            
            assert result == 10
            assert executed_context is not None
            assert executed_context["task_id"] == "test_id"
            assert executed_context["task_state"]["state_key"] == "state_value"
            assert executed_context["global_state"]["global_key"] == "global_value"
        finally:
            GraphContext.pop()

    def test_execute_single_exception_propagation(self):
        """Test that exceptions in task functions are propagated"""
        def failing_fn():
            raise ValueError("Test error")
        
        node = TaskNode("test", failing_fn, {}, "test_id")
        graph = Graph("test_graph")
        
        GraphContext.push(graph)
        try:
            with pytest.raises(ValueError, match="Test error"):
                node.execute_single()
        finally:
            GraphContext.pop()


class TestSourceNode:
    def test_source_node_inherits_from_task_node(self):
        """Test SourceNode is a subclass of TaskNode"""
        def dummy_fn():
            yield 1
        
        node = SourceNode("source", dummy_fn, {}, "source_id")
        
        assert isinstance(node, TaskNode)
        assert node.name == "source"
        assert node.task_id == "source_id"

    def test_generate_with_generator_function(self):
        """Test generate method with generator function"""
        def gen_fn():
            for i in range(3):
                yield i * 2
        
        node = SourceNode("source", gen_fn, {}, "source_id")
        graph = Graph("test_graph")
        
        GraphContext.push(graph)
        try:
            result = list(node.generate())
            assert result == [0, 2, 4]
        finally:
            GraphContext.pop()

    def test_generate_with_non_generator_raises_error(self):
        """Test generate raises error for non-generator functions"""
        def not_gen_fn():
            return [1, 2, 3]  # Returns list, not generator
        
        node = SourceNode("source", not_gen_fn, {}, "source_id")
        graph = Graph("test_graph")
        
        GraphContext.push(graph)
        try:
            with pytest.raises(ValueError, match="must return a generator"):
                list(node.generate())
        finally:
            GraphContext.pop()

    def test_generate_with_context(self):
        """Test generate creates proper task context"""
        executed_context = None
        
        def gen_fn():
            nonlocal executed_context
            from taskgraph.task_context import get_current_task_context
            executed_context = get_current_task_context()
            yield "test_value"
        
        node = SourceNode("source", gen_fn, {}, "source_id")
        graph = Graph("test_graph")
        graph.graph_state = {"source_id": {"source_state": "value"}}
        graph.global_state = {"global_state": "value"}
        
        GraphContext.push(graph)
        try:
            result = list(node.generate())
            
            assert result == ["test_value"]
            assert executed_context["task_id"] == "source_id"
            assert executed_context["task_state"]["source_state"] == "value"
            assert executed_context["global_state"]["global_state"] == "value"
        finally:
            GraphContext.pop()
