import pytest
from candles.types import Candle, TimeseriesObject, Timeframe
from candles.globals import BASE_INITIAL_TIMESTAMP
from candles.exceptions import CandleValidationError, TimeseriesValidationError


class TestCandle:
    """Test suite for Candle class"""
    
    @pytest.fixture
    def valid_timeframe(self):
        """Fixture providing a valid timeframe"""
        return Timeframe._1h
    
    @pytest.fixture
    def valid_base_timeframe(self):
        """Fixture providing a valid base timeframe"""
        return Timeframe._5m
    
    @pytest.fixture
    def valid_timestamp(self, valid_timeframe):
        """Fixture providing a valid timestamp"""
        return BASE_INITIAL_TIMESTAMP + valid_timeframe.ms * 10
    
    def test_valid_candle_creation(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test successful creation of Candle with valid OHLC data"""
        candle = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            complete=True
        )
        
        assert candle.open == 100.0
        assert candle.high == 110.0
        assert candle.low == 95.0
        assert candle.close == 105.0
    
    def test_default_ohlc_values(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that OHLC values default to 0"""
        candle = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp
        )
        
        assert candle.open == 0
        assert candle.high == 0
        assert candle.low == 0
        assert candle.close == 0
    
    def test_price_type_validation(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that price values must be numeric"""
        with pytest.raises(TypeError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                open="100.0"  # String instead of numeric
            )
        
        with pytest.raises(TypeError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                high=None
            )
    
    def test_negative_price_validation(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that price values cannot be negative"""
        with pytest.raises(CandleValidationError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                open=-10.0
            )
        
        with pytest.raises(CandleValidationError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                low=-5.0
            )
    
    def test_ohlc_relationship_validation_open_outside_range(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that open price must be within high-low range"""
        with pytest.raises(CandleValidationError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                open=120.0,  # Above high
                high=110.0,
                low=90.0,
                close=100.0
            )
        
        with pytest.raises(CandleValidationError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                open=80.0,   # Below low
                high=110.0,
                low=90.0,
                close=100.0
            )
    
    def test_ohlc_relationship_validation_close_outside_range(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that close price must be within high-low range"""
        with pytest.raises(CandleValidationError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                open=100.0,
                high=110.0,
                low=90.0,
                close=120.0  # Above high
            )
        
        with pytest.raises(CandleValidationError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=valid_timestamp,
                open=100.0,
                high=110.0,
                low=90.0,
                close=80.0   # Below low
            )
    
    def test_valid_ohlc_relationships(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test various valid OHLC relationships"""
        # Open and close at extremes
        candle1 = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=90.0,   # At low
            high=110.0,
            low=90.0,
            close=110.0  # At high
        )
        assert candle1.open == 90.0
        
        # All prices equal
        candle2 = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0
        )
        assert candle2.high == candle2.low == 100.0
        
        # Open and close in middle
        candle3 = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=100.0,
            high=110.0,
            low=90.0,
            close=95.0
        )
        assert 90.0 <= candle3.open <= 110.0
        assert 90.0 <= candle3.close <= 110.0
    
    def test_integer_prices_accepted(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that integer prices are accepted"""
        candle = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=100,    # Integer
            high=110,    # Integer
            low=90,      # Integer
            close=105    # Integer
        )
        
        assert candle.open == 100
        assert candle.high == 110
        assert candle.low == 90
        assert candle.close == 105
    
    def test_zero_prices_valid(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that zero prices are valid"""
        candle = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=0.0,
            high=0.0,
            low=0.0,
            close=0.0
        )
        
        assert candle.open == 0.0
        assert candle.high == 0.0
        assert candle.low == 0.0
        assert candle.close == 0.0
    
    def test_candle_copy_with_price_updates(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test copying candle with price updates"""
        original = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0
        )
        
        updated = original.copy(open=95.0, close=102.0)
        
        assert updated.open == 95.0
        assert updated.close == 102.0
        assert updated.high == 110.0  # Unchanged
        assert updated.low == 90.0    # Unchanged
        assert updated.timestamp == original.timestamp
    
    def test_candle_inherits_timestamp_validation(self, valid_base_timeframe, valid_timeframe):
        """Test that Candle inherits timestamp validation from TimeseriesObject"""
        with pytest.raises(TypeError):
            Candle(
                base_timeframe=valid_base_timeframe,
                timeframe=valid_timeframe,
                timestamp=123.45,
                open=100.0,
                high=100.0,
                low=100.0,
                close=100.0
            )
    
    def test_candle_frozen_dataclass(self, valid_base_timeframe, valid_timeframe, valid_timestamp):
        """Test that Candle is immutable"""
        candle = Candle(
            base_timeframe=valid_base_timeframe,
            timeframe=valid_timeframe,
            timestamp=valid_timestamp,
            open=100.0,
            high=110.0,
            low=90.0,
            close=105.0
        )
        
        with pytest.raises(AttributeError):
            candle.open = 120.0
        
        with pytest.raises(AttributeError):
            candle.timestamp = valid_timestamp + 1000
