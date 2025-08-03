import pytest
import json
from candles.types import TimeseriesObject, Timeframe
from candles.globals import BASE_INITIAL_TIMESTAMP
from candles.exceptions import TimeseriesValidationError


class TestTimeseriesObject:
    """Test suite for TimeseriesObject class"""
    
    @pytest.fixture
    def valid_timeframe(self):
        """Fixture providing a valid timeframe"""
        return Timeframe._5m
    
    @pytest.fixture
    def valid_base_timeframe(self):
        """Fixture providing a valid base timeframe"""
        return Timeframe._1m
    
    @pytest.fixture
    def valid_timestamp(self, valid_timeframe):
        """Fixture providing a valid timestamp aligned with timeframe"""
        return BASE_INITIAL_TIMESTAMP + valid_timeframe.ms
    
    def test_valid_creation(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test successful creation of TimeseriesObject with valid parameters"""
        obj = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            complete=True
        )
        
        assert obj.base_timeframe == valid_base_timeframe
        assert obj.timeframe == valid_timeframe
        assert obj.timestamp == valid_timestamp
        assert obj.complete is True
    
    def test_default_complete_value(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that complete defaults to True"""
        obj = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp
        )
        assert obj.complete is True
    
    def test_timestamp_type_validation(self, valid_base_timeframe, valid_timeframe):
        """Test that timestamp must be an integer"""
        with pytest.raises(TypeError):
            TimeseriesObject(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=123.45
            )
        
        with pytest.raises(TypeError):
            TimeseriesObject(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp="123"
            )
    
    def test_complete_type_validation(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that complete must be a boolean"""
        with pytest.raises(TypeError):
            TimeseriesObject(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                complete="true"
            )
        
        with pytest.raises(TypeError):
            TimeseriesObject(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                complete=1
            )
    
    def test_timestamp_before_base_validation(self, valid_base_timeframe, valid_timeframe):
        """Test that timestamp cannot be before BASE_INITIAL_TIMESTAMP"""
        invalid_timestamp = BASE_INITIAL_TIMESTAMP - 1
        with pytest.raises(TimeseriesValidationError):
            TimeseriesObject(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=invalid_timestamp
            )
    
    def test_timestamp_alignment_validation(self, valid_base_timeframe, valid_timeframe):
        """Test that timestamp must be aligned with timeframe"""
        # Timestamp not aligned with timeframe
        misaligned_timestamp = BASE_INITIAL_TIMESTAMP + 30000  # Half of MOCK_TIMEFRAME_MS
        with pytest.raises(TimeseriesValidationError):
            TimeseriesObject(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=misaligned_timestamp
            )
    
    def test_repr_method(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test the __repr__ method returns valid JSON"""
        obj = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            complete=False
        )
        
        repr_str = repr(obj)
        # Should be valid JSON
        parsed = json.loads(repr_str)
        
        # Verify contents (note: dataclass __dict__ may not include complex objects directly)
        assert 'timestamp' in repr_str
        assert 'complete' in repr_str
    
    def test_copy_method_no_changes(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test copy method with no parameter changes"""
        original = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            complete=True
        )
        
        copied = original.copy()
        
        assert copied.base_timeframe == original.base_timeframe
        assert copied.timeframe == original.timeframe
        assert copied.timestamp == original.timestamp
        assert copied.complete == original.complete
        assert copied is not original  # Different objects
    
    def test_copy_method_with_changes(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test copy method with parameter updates"""
        original = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            complete=True
        )
        
        new_timestamp = valid_timestamp + valid_timeframe.ms
        copied = original.copy(timestamp=new_timestamp, complete=False)
        
        assert copied.timestamp == new_timestamp
        assert copied.complete is False
        assert copied.base_timeframe == original.base_timeframe
        assert copied.timeframe == original.timeframe
    
    def test_start_timestamp_property(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that start_timestamp property returns timestamp"""
        obj = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp
        )
        
        assert obj.start_timestamp == valid_timestamp
    
    def test_end_timestamp_property(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that end_timestamp property returns timestamp + timeframe.ms"""
        obj = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp
        )
        
        expected_end = valid_timestamp + valid_timeframe.ms
        assert obj.end_timestamp == expected_end
    
    def test_frozen_dataclass(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that TimeseriesObject is immutable (frozen dataclass)"""
        obj = TimeseriesObject(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp
        )
        
        with pytest.raises(AttributeError):
            obj.timestamp = valid_timestamp + 1000