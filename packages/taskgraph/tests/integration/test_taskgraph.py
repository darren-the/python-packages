import pytest
from taskgraph.decorators import task, source, graph
from taskgraph.task_context import (
    get_current_task_context,
    set_global_state,
    get_global_state_value,
    get_global_state
)
from taskgraph.graph import Graph
from taskgraph.exceptions import TaskContextError, DuplicateTaskIdError, NoTaskIdError


def test_basic_source_task_graph():
    """Test basic source -> task flow"""
    test_output = []
    
    @source
    def numbers_source():
        for i in range(3):
            yield i
    
    @task
    def double_task(number):
        doubled = number * 2
        test_output.append(doubled)
        return doubled
    
    @graph
    def basic_graph():
        nums = numbers_source(task_id='numbers')
        double_task(task_id='doubler', number=nums)
    
    graph_instance = basic_graph()
    graph_instance.execute()
    
    assert test_output == [0, 2, 4]


def test_multiple_tasks_from_source():
    """Test source feeding multiple parallel tasks"""
    test_output_a = []
    test_output_b = []
    
    @source
    def numbers_source():
        for i in range(3):
            yield i
    
    @task
    def double_task(number):
        doubled = number * 2
        test_output_a.append(doubled)
        return doubled
    
    @task
    def triple_task(number):
        tripled = number * 3
        test_output_b.append(tripled)
        return tripled
    
    @graph
    def parallel_graph():
        nums = numbers_source(task_id='numbers')
        double_task(task_id='doubler', number=nums)
        triple_task(task_id='tripler', number=nums)
    
    graph_instance = parallel_graph()
    graph_instance.execute()
    
    assert test_output_a == [0, 2, 4]
    assert test_output_b == [0, 3, 6]


def test_chained_tasks():
    """Test source -> task -> task chain"""
    test_output = []
    
    @source
    def numbers_source():
        for i in range(3):
            yield i
    
    @task
    def double_task(number):
        return number * 2
    
    @task
    def add_ten_task(number):
        result = number + 10
        test_output.append(result)
        return result
    
    @graph
    def chain_graph():
        nums = numbers_source(task_id='numbers')
        doubled = double_task(task_id='doubler', number=nums)
        add_ten_task(task_id='add_ten', number=doubled)
    
    graph_instance = chain_graph()
    graph_instance.execute()
    
    assert test_output == [10, 12, 14]  # (0*2)+10, (1*2)+10, (2*2)+10


def test_task_state_persistence():
    """Test that task state persists across invocations"""
    test_output = []
    
    @source
    def numbers_source():
        for i in range(5):
            yield i
    
    @task
    def accumulator_task(number):
        ctx = get_current_task_context()
        task_state = ctx["task_state"]
        task_state.setdefault("total", 0)
        
        task_state["total"] += number
        test_output.append(task_state["total"])
        return task_state["total"]
    
    @graph
    def stateful_graph():
        nums = numbers_source(task_id='numbers')
        accumulator_task(task_id='accumulator', number=nums)
    
    graph_instance = stateful_graph()
    graph_instance.execute()
    
    assert test_output == [0, 1, 3, 6, 10]  # Running sum: 0, 0+1, 1+2, 3+3, 6+4
    assert graph_instance.graph_state['accumulator']['total'] == 10


def test_global_state():
    """Test global state sharing between tasks"""
    test_output = []
    
    @source
    def numbers_source():
        for i in range(3):
            yield i
    
    @task
    def setter_task(number):
        set_global_state("current_number", number)
        return number
    
    @task
    def getter_task(set_number):
        current = get_global_state_value("current_number", -1)
        test_output.append(current)
        return current
    
    @graph
    def global_state_graph():
        nums = numbers_source(task_id='numbers')
        set_nums = setter_task(task_id='setter', number=nums)
        getter_task(task_id='getter', set_number=set_nums)
    
    graph_instance = global_state_graph()
    graph_instance.execute()
    
    # Note: execution order matters here. The setter should run before getter
    # for each value due to topological ordering
    assert test_output == [0, 1, 2]


def test_multiple_sources():
    """Test graph with multiple independent sources"""
    test_output = []
    
    @source
    def letters_source():
        for letter in ['a', 'b', 'c']:
            yield letter
    
    @source
    def numbers_source():
        for i in range(2):
            yield i
    
    @task
    def letter_task(letter):
        test_output.append(f"letter: {letter}")
        return letter
    
    @task
    def number_task(number):
        test_output.append(f"number: {number}")
        return number
    
    @graph
    def multi_source_graph():
        letters = letters_source(task_id='letters')
        numbers = numbers_source(task_id='numbers')
        letter_task(task_id='letter_processor', letter=letters)
        number_task(task_id='number_processor', number=numbers)
    
    graph_instance = multi_source_graph()
    graph_instance.execute()
    
    # Should contain all letters and all numbers
    assert 'letter: a' in test_output
    assert 'letter: b' in test_output
    assert 'letter: c' in test_output
    assert 'number: 0' in test_output
    assert 'number: 1' in test_output


def test_execute_end_hook():
    """Test that execution end hooks work with new model"""
    test_output = []
    
    @source
    def numbers_source():
        for i in range(3):
            yield i
    
    @task
    def accumulator_task(number):
        ctx = get_current_task_context()
        task_state = ctx["task_state"]
        task_state.setdefault("total", 0)
        task_state["total"] += number
        set_global_state("final_total", task_state["total"])
        return task_state["total"]
    
    def end_hook(graph_instance: Graph):
        final_total = graph_instance.global_state.get("final_total", 0)
        test_output.append(f"Final total: {final_total}")
    
    @graph(on_execute_end=end_hook)
    def hook_graph():
        nums = numbers_source(task_id='numbers')
        accumulator_task(task_id='accumulator', number=nums)
    
    graph_instance = hook_graph()
    graph_instance.execute()
    
    assert test_output == ["Final total: 3"]  # 0+1+2 = 3


def test_no_source_error():
    """Test that graphs without sources raise an error"""
    @task
    def orphan_task():
        return "lonely"
    
    @graph
    def no_source_graph():
        orphan_task(task_id='orphan')
    
    graph_instance = no_source_graph()
    
    with pytest.raises(ValueError, match="Graph has no source nodes"):
        graph_instance.execute()


def test_duplicate_task_id_error():
    """Test that duplicate task IDs are caught"""
    @source
    def numbers_source():
        yield 1
    
    @task
    def task_a(number):
        return number
    
    @task 
    def task_b(number):
        return number
    
    @graph
    def duplicate_id_graph():
        nums = numbers_source(task_id='numbers')
        task_a(task_id='duplicate_id', number=nums)
        task_b(task_id='duplicate_id', number=nums)  # This should fail
    
    with pytest.raises(DuplicateTaskIdError):
        duplicate_id_graph()


def test_no_task_id_error():
    """Test that missing task IDs are caught"""
    @source
    def numbers_source():
        yield 1
    
    @graph
    def no_id_graph():
        numbers_source()  # Missing task_id
    
    with pytest.raises(NoTaskIdError):
        no_id_graph()


def test_graphviz_output():
    """Test that GraphViz output includes source/task types"""
    @source
    def numbers_source():
        yield 1
    
    @task
    def process_task(number):
        return number * 2
    
    @graph
    def simple_graph():
        nums = numbers_source(task_id='source')
        process_task(task_id='processor', number=nums)
    
    graph_instance = simple_graph()
    graphviz = graph_instance.to_graphviz()
    
    assert 'source\\n(source)' in graphviz
    assert 'processor\\n(task)' in graphviz
    assert '"source" -> "processor"' in graphviz


def test_json_output():
    """Test that JSON output includes node types"""
    @source
    def numbers_source():
        yield 1
    
    @task
    def process_task(number):
        return number * 2
    
    @graph
    def simple_graph():
        nums = numbers_source(task_id='source')
        process_task(task_id='processor', number=nums)
    
    graph_instance = simple_graph()
    json_output = graph_instance.to_json()
    
    import json
    data = json.loads(json_output)
    
    assert len(data['nodes']) == 2
    source_node = next(n for n in data['nodes'] if n['id'] == 'source')
    task_node = next(n for n in data['nodes'] if n['id'] == 'processor')
    
    assert source_node['type'] == 'source'
    assert task_node['type'] == 'task'
