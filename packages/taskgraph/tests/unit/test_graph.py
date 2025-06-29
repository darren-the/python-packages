import pytest
from taskgraph.graph import Graph
from taskgraph.task import TaskNode, SourceNode
from taskgraph.context import GraphContext


class TestGraph:
    def test_graph_creation(self):
        """Test Graph constructor"""
        graph = Graph("test_graph")
        
        assert graph.name == "test_graph"
        assert graph.nodes == []
        assert graph.graph_state == {}
        assert graph.global_state == {}
        assert graph._on_execute_end_hooks == []

    def test_graph_creation_with_state(self):
        """Test Graph constructor with initial state"""
        graph_state = {"task1": {"key": "value"}}
        global_state = {"global_key": "global_value"}
        
        graph = Graph("test", graph_state, global_state)
        
        assert graph.graph_state == graph_state
        assert graph.global_state == global_state

    def test_add_node(self):
        """Test adding nodes to graph"""
        graph = Graph("test")
        node = TaskNode("task", lambda: None, {}, "task_id")
        
        graph.add_node(node)
        
        assert len(graph.nodes) == 1
        assert graph.nodes[0] == node

    def test_state_property_getter(self):
        """Test state property getter"""
        graph = Graph("test")
        graph.graph_state = {"task1": {"key": "value"}}
        graph.global_state = {"global": "value"}
        
        state = graph.state
        
        expected = {
            "graph_state": {"task1": {"key": "value"}},
            "global_state": {"global": "value"}
        }
        assert state == expected

    def test_state_property_setter(self):
        """Test state property setter"""
        graph = Graph("test")
        new_state = {
            "graph_state": {"task1": {"key": "value"}},
            "global_state": {"global": "value"}
        }
        
        graph.state = new_state
        
        assert graph.graph_state == {"task1": {"key": "value"}}
        assert graph.global_state == {"global": "value"}

    def test_state_property_setter_invalid_type(self):
        """Test state property setter with invalid type"""
        graph = Graph("test")
        
        with pytest.raises(ValueError, match="State must be a dictionary"):
            graph.state = "not a dict"

    def test_update_state(self):
        """Test updating existing state"""
        graph = Graph("test")
        graph.graph_state = {"task1": {"existing": "value"}}
        graph.global_state = {"existing_global": "value"}
        
        update = {
            "graph_state": {"task2": {"new": "value"}},
            "global_state": {"new_global": "value"}
        }
        
        graph.update_state(update)
        
        assert graph.graph_state == {
            "task1": {"existing": "value"},
            "task2": {"new": "value"}
        }
        assert graph.global_state == {
            "existing_global": "value",
            "new_global": "value"
        }

    def test_add_on_execute_end_hook(self):
        """Test adding execution end hooks"""
        graph = Graph("test")
        
        def hook1(g):
            pass
        def hook2(g):
            pass
        
        graph.add_on_execute_end_hook(hook1)
        graph.add_on_execute_end_hook(hook2)
        
        assert len(graph._on_execute_end_hooks) == 2
        assert hook1 in graph._on_execute_end_hooks
        assert hook2 in graph._on_execute_end_hooks

    def test_remove_on_execute_end_hook(self):
        """Test removing execution end hooks"""
        graph = Graph("test")
        
        def hook1(g):
            pass
        def hook2(g):
            pass
        
        graph.add_on_execute_end_hook(hook1)
        graph.add_on_execute_end_hook(hook2)
        graph.remove_on_execute_end_hook(hook1)
        
        assert len(graph._on_execute_end_hooks) == 1
        assert hook1 not in graph._on_execute_end_hooks
        assert hook2 in graph._on_execute_end_hooks

    def test_clear_on_execute_end_hooks(self):
        """Test clearing all execution end hooks"""
        graph = Graph("test")
        
        def hook1(g):
            pass
        def hook2(g):
            pass
        
        graph.add_on_execute_end_hook(hook1)
        graph.add_on_execute_end_hook(hook2)
        graph.clear_on_execute_end_hooks()
        
        assert len(graph._on_execute_end_hooks) == 0

    def test_get_source_nodes(self):
        """Test finding source nodes in graph"""
        graph = Graph("test")
        
        source1 = SourceNode("source1", lambda: (yield 1), {}, "s1")
        source2 = SourceNode("source2", lambda: (yield 2), {}, "s2")
        task1 = TaskNode("task1", lambda x: x, {}, "t1")
        
        graph.add_node(source1)
        graph.add_node(task1)
        graph.add_node(source2)
        
        sources = graph._get_source_nodes()
        
        assert len(sources) == 2
        assert source1 in sources
        assert source2 in sources
        assert task1 not in sources

    def test_is_reachable_from_simple_chain(self):
        """Test reachability check with simple chain"""
        graph = Graph("test")
        
        source = SourceNode("source", lambda: (yield 1), {}, "source")
        task1 = TaskNode("task1", lambda x: x, {}, "task1")
        task2 = TaskNode("task2", lambda x: x, {}, "task2")
        
        task1.set_upstream(source)
        task2.set_upstream(task1)
        
        assert graph._is_reachable_from(task1, source)
        assert graph._is_reachable_from(task2, source)
        assert not graph._is_reachable_from(source, task1)

    def test_is_reachable_from_unreachable(self):
        """Test reachability check with unreachable nodes"""
        graph = Graph("test")
        
        source1 = SourceNode("source1", lambda: (yield 1), {}, "s1")
        source2 = SourceNode("source2", lambda: (yield 2), {}, "s2")
        task1 = TaskNode("task1", lambda x: x, {}, "task1")
        task2 = TaskNode("task2", lambda x: x, {}, "task2")
        
        task1.set_upstream(source1)
        task2.set_upstream(source2)
        
        assert not graph._is_reachable_from(task2, source1)
        assert not graph._is_reachable_from(task1, source2)

    def test_topological_sort_simple_chain(self):
        """Test topological sort with simple chain"""
        graph = Graph("test")
        
        source = SourceNode("source", lambda: (yield 1), {}, "source")
        task1 = TaskNode("task1", lambda x: x, {}, "task1")
        task2 = TaskNode("task2", lambda x: x, {}, "task2")
        
        task1.set_upstream(source)
        task2.set_upstream(task1)
        
        order = graph._topological_sort_from_source(source)
        
        assert order == [source, task1, task2]

    def test_topological_sort_parallel_tasks(self):
        """Test topological sort with parallel tasks"""
        graph = Graph("test")
        
        source = SourceNode("source", lambda: (yield 1), {}, "source")
        task1 = TaskNode("task1", lambda x: x, {}, "task1")
        task2 = TaskNode("task2", lambda x: x, {}, "task2")
        
        task1.set_upstream(source)
        task2.set_upstream(source)
        
        order = graph._topological_sort_from_source(source)
        
        assert order[0] == source
        assert task1 in order
        assert task2 in order
        assert len(order) == 3

    def test_execute_no_sources_raises_error(self):
        """Test execute raises error when no source nodes"""
        graph = Graph("test")
        task = TaskNode("task", lambda: None, {}, "task")
        graph.add_node(task)
        
        with pytest.raises(ValueError, match="Graph has no source nodes"):
            graph.execute()
