from candles.types import Candle, Timeframe
from candles.operations import calculate_rsi


CANDLES = [
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750377600000, complete=True, open=104790, close=104820, high=104940, low=104670),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750381200000, complete=True, open=104840, close=104900, high=104920, low=104530),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750384800000, complete=True, open=104930, close=104760, high=104940, low=104640),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750388400000, complete=True, open=104760, close=104740, high=104830, low=104650),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750392000000, complete=True, open=104740, close=104390, high=104740, low=104370),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750395600000, complete=True, open=104390, close=104700, high=104700, low=104390),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750399200000, complete=True, open=104700, close=104820, high=104850, low=104700),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750402800000, complete=True, open=104810, close=105880, high=105880, low=104750),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750406400000, complete=True, open=105880, close=106080, high=106580, low=105870),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750410000000, complete=True, open=106110, close=106070, high=106110, low=105870),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750413600000, complete=True, open=106040, close=106070, high=106250, low=105950),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750417200000, complete=True, open=106070, close=106100, high=106140, low=105920),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750420800000, complete=True, open=106090, close=106110, high=106170, low=105980),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750424400000, complete=True, open=106120, close=105740, high=106210, low=105470),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750428000000, complete=True, open=105760, close=104020, high=105820, low=103910),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750431600000, complete=True, open=104020, close=104320, high=104650, low=103960),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750435200000, complete=True, open=104340, close=103750, high=104360, low=103730),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750438800000, complete=True, open=103770, close=103360, high=103850, low=102490),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750442400000, complete=True, open=103350, close=103260, high=103470, low=103140),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750446000000, complete=True, open=103250, close=103420, high=103570, low=103100),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750449600000, complete=True, open=103390, close=103780, high=103890, low=103390),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750453200000, complete=True, open=103810, close=103610, high=103810, low=103460),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750456800000, complete=True, open=103630, close=103170, high=103630, low=103070),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750460400000, complete=True, open=103200, close=103360, high=103410, low=103080),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750464000000, complete=True, open=103370, close=103250, high=103420, low=103200),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750467600000, complete=True, open=103250, close=103590, high=103590, low=103230),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750471200000, complete=True, open=103590, close=103610, high=103620, low=103490),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750474800000, complete=True, open=103610, close=103620, high=103810, low=103610),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750478400000, complete=True, open=103620, close=103530, high=103650, low=103440),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750482000000, complete=True, open=103510, close=103560, high=103620, low=103480),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750485600000, complete=True, open=103560, close=103700, high=103730, low=103460),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750489200000, complete=True, open=103710, close=103570, high=103730, low=103490),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750492800000, complete=True, open=103590, close=103930, high=103930, low=103590),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750496400000, complete=True, open=103920, close=103970, high=104060, low=103800),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750500000000, complete=True, open=103990, close=103970, high=104120, low=103920),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750503600000, complete=True, open=103970, close=103980, high=104000, low=103880),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750507200000, complete=True, open=103990, close=103930, high=104000, low=103900),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750510800000, complete=True, open=103930, close=103710, high=104000, low=103670),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750514400000, complete=True, open=103710, close=103660, high=103910, low=103500),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750518000000, complete=True, open=103670, close=103700, high=103790, low=103430),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750521600000, complete=True, open=103690, close=103630, high=103780, low=103600),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750525200000, complete=True, open=103620, close=103300, high=103710, low=103290),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750528800000, complete=True, open=103290, close=102770, high=103510, low=102770),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750532400000, complete=True, open=102760, close=102360, high=102830, low=102310),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750536000000, complete=True, open=102360, close=102920, high=103010, low=102320),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750539600000, complete=True, open=102920, close=101580, high=102920, low=101220),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750543200000, complete=True, open=101570, close=101910, high=102100, low=101560),
    Candle(base_timeframe=Timeframe._1h, timeframe=Timeframe._1h, timestamp=1750546800000, complete=True, open=101920, close=102220, high=102410, low=101020)
]


def test_calculate_rsi():
    prev_rsi = None
    for candle in CANDLES:
        rsi = calculate_rsi(candle, prev_rsi)
        prev_rsi = rsi
    assert rsi.value == 37.26
