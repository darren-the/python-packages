import pytest
from taskgraph.task_context import (
    TaskContextManager, 
    get_current_task_context,
    get_global_state,
    set_global_state,
    get_global_state_value
)
from taskgraph.exceptions import TaskContextError


class TestTaskContextManager:
    def test_context_manager_enter_exit(self):
        """Test TaskContextManager enter and exit"""
        task_state = {"task_key": "task_value"}
        global_state = {"global_key": "global_value"}
        
        with TaskContextManager("test_id", task_state, global_state):
            ctx = get_current_task_context()
            assert ctx["task_id"] == "test_id"
            assert ctx["task_state"] == task_state
            assert ctx["global_state"] == global_state

    def test_context_manager_cleans_up(self):
        """Test context is cleaned up after exit"""
        task_state = {"task_key": "task_value"}
        global_state = {"global_key": "global_value"}
        
        with TaskContextManager("test_id", task_state, global_state):
            pass  # Context should be active here
            
        # Context should be cleaned up now
        with pytest.raises(TaskContextError):
            get_current_task_context()

    def test_context_manager_none_global_state_raises_error(self):
        """Test TaskContextManager raises error for None global_state"""
        with pytest.raises(ValueError, match="global_state cannot be None"):
            TaskContextManager("test_id", {}, None)

    def test_nested_context_managers(self):
        """Test nested context managers work correctly"""
        task_state1 = {"task1": "value1"}
        global_state1 = {"global1": "value1"}
        task_state2 = {"task2": "value2"}
        global_state2 = {"global2": "value2"}
        
        with TaskContextManager("test1", task_state1, global_state1):
            ctx1 = get_current_task_context()
            assert ctx1["task_id"] == "test1"
            
            with TaskContextManager("test2", task_state2, global_state2):
                ctx2 = get_current_task_context()
                assert ctx2["task_id"] == "test2"
                assert ctx2["task_state"] == task_state2
            
            # Should restore outer context
            ctx1_restored = get_current_task_context()
            assert ctx1_restored["task_id"] == "test1"


class TestTaskContextFunctions:
    def test_get_current_task_context_no_context(self):
        """Test get_current_task_context raises error when no context"""
        with pytest.raises(TaskContextError, match="No active task context"):
            get_current_task_context()

    def test_get_global_state(self):
        """Test get_global_state returns global state"""
        global_state = {"key": "value"}
        
        with TaskContextManager("test", {}, global_state):
            result = get_global_state()
            assert result == global_state
            assert result is global_state  # Should be same object

    def test_set_global_state(self):
        """Test set_global_state updates global state"""
        global_state = {}
        
        with TaskContextManager("test", {}, global_state):
            set_global_state("new_key", "new_value")
            assert global_state["new_key"] == "new_value"

    def test_set_global_state_validation(self):
        """Test set_global_state validates the update worked"""
        # Create a read-only dict-like object that fails to set
        class ReadOnlyDict(dict):
            def __setitem__(self, key, value):
                pass  # Silently fail to set
                
            def get(self, key, default=None):
                return None  # Always return None
        
        global_state = ReadOnlyDict()
        
        with TaskContextManager("test", {}, global_state):
            with pytest.raises(RuntimeError, match="Failed to set global state"):
                set_global_state("key", "value")

    def test_get_global_state_value(self):
        """Test get_global_state_value retrieves values"""
        global_state = {"existing_key": "existing_value"}
        
        with TaskContextManager("test", {}, global_state):
            # Test existing key
            result = get_global_state_value("existing_key")
            assert result == "existing_value"
            
            # Test non-existing key with default
            result = get_global_state_value("missing_key", "default")
            assert result == "default"
            
            # Test non-existing key without default
            result = get_global_state_value("missing_key")
            assert result is None