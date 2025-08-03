class NothingToImputeError(ValueError):
    """Raised when attempting to impute candles that are not missing."""

class CandleValidationError(ValueError):
    """Raised when a candle fails validation checks."""

class TimeseriesValidationError(ValueError):
    """Raised when a timeseries object fails validation checks."""
    