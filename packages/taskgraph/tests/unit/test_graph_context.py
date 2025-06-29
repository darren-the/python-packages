import pytest
from taskgraph.context import GraphContext
from taskgraph.graph import Graph


class TestGraphContext:
    def test_push_and_current(self):
        """Test pushing graph to context and retrieving current"""
        graph = Graph("test")
        
        GraphContext.push(graph)
        try:
            current = GraphContext.current()
            assert current == graph
        finally:
            GraphContext.pop()

    def test_pop(self):
        """Test popping graph from context"""
        graph1 = Graph("test1")
        graph2 = Graph("test2")
        
        GraphContext.push(graph1)
        GraphContext.push(graph2)
        
        assert GraphContext.current() == graph2
        GraphContext.pop()
        assert GraphContext.current() == graph1
        GraphContext.pop()

    def test_current_no_context_raises_error(self):
        """Test current() raises error when no context"""
        # Ensure context is clean
        GraphContext._current.clear()
        
        with pytest.raises(RuntimeError, match="No active graph context"):
            GraphContext.current()

    def test_nested_contexts(self):
        """Test nested graph contexts work correctly"""
        graph1 = Graph("outer")
        graph2 = Graph("inner")
        
        GraphContext.push(graph1)
        try:
            assert GraphContext.current() == graph1
            
            GraphContext.push(graph2)
            try:
                assert GraphContext.current() == graph2
            finally:
                GraphContext.pop()
                
            assert GraphContext.current() == graph1
        finally:
            GraphContext.pop()
