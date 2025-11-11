import backtrader as bt
import numpy as np

# --- 3. RAG METADATA (Replaces strategy_metadata.json) ---
STRATEGY_METADATA_LIST = [
    {
        "strategy_id": "SmaCrossStrategy",
        "description": "A simple trend-following strategy. It buys when a short-term moving average (n1) crosses above a long-term one (n2) and sells on the reverse cross. Best for simple, trending markets. Also known as a 'Golden Cross' or 'Death Cross'.",
        "parameters": [
            {"name": "n1", "type": "int", "description": "The period for the fast moving average, e.g., 50"},
            {"name": "n2", "type": "int", "description": "The period for the slow moving average, e.g., 200"}
        ]
    },
    {
        "strategy_id": "RsiStrategy",
        "description": "A mean-reversion strategy. It buys when the Relative Strength Index (RSI) crosses below an 'oversold' level (e.g., 30) and sells when it crosses above an 'overbought' level (e.g., 70).",
        "parameters": [
            {"name": "period", "type": "int", "description": "The lookback period for the RSI, typically 14."},
            {"name": "oversold", "type": "int", "description": "The RSI level considered oversold, typically 30."},
            {"name": "overbought", "type": "int", "description": "The RSI level considered overbought, typically 70."}
        ]
    },
    {
        "strategy_id": "MultiInstrumentSignal",
        "description": "A complex multi-asset strategy. It trades one target instrument (e.g., Nifty) based on the average performance of a basket of other 'signal' instruments (e.g., 10 stocks). All signal symbols must be provided first, and the target trade symbol last.",
        "parameters": []
    },
    {
        "strategy_id": "BollingerBandsReversion",
        "description": "A mean-reversion strategy. It buys when the price touches or crosses below the lower Bollinger Band and sells when it touches or crosses above the upper Bollinger Band.",
        "parameters": [
            {"name": "period", "type": "int", "description": "The lookback period for the moving average, typically 20."},
            {"name": "devfactor", "type": "float", "description": "The number of standard deviations for the bands, typically 2.0."}
        ]
    },
    {
        "strategy_id": "MACDStrategy",
        "description": "A trend-following strategy based on the Moving Average Convergence Divergence (MACD). It buys when the MACD line crosses above the signal line and sells when it crosses below.",
        "parameters": [
            {"name": "fast_ema", "type": "int", "description": "The period for the fast EMA, typically 12."},
            {"name": "slow_ema", "type": "int", "description": "The period for the slow EMA, typically 26."},
            {"name": "signal_ema", "type": "int", "description": "The period for the signal line EMA, typically 9."}
        ]
    },
    {
        "strategy_id": "StochasticStrategy",
        "description": "A momentum oscillator strategy. It buys when the %K line crosses above the %D line in the oversold region (e.g., below 20) and sells when it crosses below in the overbought region (e.g., above 80).",
        "parameters": [
            {"name": "k_period", "type": "int", "description": "The lookback period for %K, typically 14."},
            {"name": "d_period", "type": "int", "description": "The smoothing period for %D, typically 3."},
            {"name": "oversold", "type": "int", "description": "The oversold level, typically 20."},
            {"name": "overbought", "type": "int", "description": "The overbought level, typically 80."}
        ]
    },
    {
        "strategy_id": "DonchianChannelBreakout",
        "description": "A trend-following breakout strategy (like Turtle Trading). It buys when the price breaks above the upper channel (N-period high) and sells when it breaks below the lower channel (N-period low).",
        "parameters": [
            {"name": "period", "type": "int", "description": "The lookback period for the channel, typically 20."}
        ]
    },
    {
        "strategy_id": "EmaCrossStrategy",
        "description": "A simple trend-following strategy using Exponential Moving Averages (EMAs), which are faster to react than SMAs. Buys when the fast EMA (n1) crosses above the slow EMA (n2).",
        "parameters": [
            {"name": "n1", "type": "int", "description": "The period for the fast EMA, e.g., 12."},
            {"name": "n2", "type": "int", "description": "The period for the slow EMA, e.g., 26."}
        ]
    },
    {
        "strategy_id": "ATRTrailingStopStrategy",
        "description": "A trend-following strategy that uses an Average True Range (ATR) based trailing stop-loss. It buys on a signal (e.g., new high) and holds until the price crosses below the trailing stop.",
        "parameters": [
            {"name": "atr_period", "type": "int", "description": "The lookback period for the ATR, typically 14."},
            {"name": "atr_multiplier", "type": "float", "description": "The multiplier for the ATR value, e.g., 3.0."}
        ]
    },
    {
        "strategy_id": "OpeningRangeBreakout",
        "description": "An intraday strategy. It buys if the price breaks above the high of the first N minutes (e.g., 15) and sells/shorts if it breaks below the low. (Note: Requires intraday data).",
        "parameters": [
            {"name": "minutes", "type": "int", "description": "The opening range period in minutes, e.g., 15 or 30."}
        ]
    }
]

# --- 5. BACKTESTING STRATEGY CLASSES (copy your classes exactly) ---
class SmaCross(bt.Strategy):
    params = (('n1', 20), ('n2', 50))
    def __init__(self):
        self.sma_fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.n1)
        self.sma_slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.n2)
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)
    def next(self):
        if not self.position and self.crossover > 0: self.buy()
        elif self.position and self.crossover < 0: self.sell()

class RsiStrategy(bt.Strategy):
    params = (('period', 14), ('oversold', 30), ('overbought', 70))
    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.period)
    def next(self):
        if not self.position and self.rsi < self.params.oversold: self.buy()
        elif self.position and self.rsi > self.params.overbought: self.sell()

class MultiInstrumentSignal(bt.Strategy):
    def __init__(self):
        self.trade_data = self.datas[-1]
        self.signal_datas = self.datas[:-1]
    def next(self):
        returns = []
        for d in self.signal_datas:
            if len(d) > 1:
                daily_return = (d.close[0] - d.close[-1]) / d.close[-1]
                returns.append(daily_return)
        if not returns: return
        avg_return = np.mean(returns)
        if avg_return < -0.005 and not self.getposition(self.trade_data): self.sell(data=self.trade_data)
        elif avg_return > 0.005 and not self.getposition(self.trade_data): self.buy(data=self.trade_data)
        elif abs(avg_return) < 0.001 and self.getposition(self.trade_data): self.close(data=self.trade_data)

class BollingerBandsReversion(bt.Strategy):
    params = (('period', 20), ('devfactor', 2.0))
    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)
    def next(self):
        if not self.position and self.data.close < self.bbands.lines.bot: self.buy()
        elif self.position and self.data.close > self.bbands.lines.top: self.sell()

class MACDStrategy(bt.Strategy):
    params = (('fast_ema', 12), ('slow_ema', 26), ('signal_ema', 9))
    def __init__(self):
        self.macd = bt.indicators.MACD(self.data.close, period_me1=self.params.fast_ema, period_me2=self.params.slow_ema, period_signal=self.params.signal_ema)
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
    def next(self):
        if not self.position and self.crossover > 0: self.buy()
        elif self.position and self.crossover < 0: self.sell()

class StochasticStrategy(bt.Strategy):
    params = (('k_period', 14), ('d_period', 3), ('oversold', 20), ('overbought', 80))
    def __init__(self):
        self.stoch = bt.indicators.Stochastic(self.data, period=self.params.k_period, period_d=self.params.d_period)
    def next(self):
        if not self.position and self.stoch.percK < self.params.oversold and self.stoch.percD < self.params.oversold and self.stoch.percK > self.stoch.percD:
            self.buy()
        elif self.position and self.stoch.percK > self.params.overbought and self.stoch.percD > self.params.overbought and self.stoch.percK < self.stoch.percD:
            self.sell()

class DonchianChannelBreakout(bt.Strategy):
    params = (('period', 20),)
    def __init__(self):
        self.donchian = bt.indicators.DonchianChannels(self.data, period=self.params.period)
    def next(self):
        if not self.position and self.data.close[0] > self.donchian.dch[0]: self.buy()
        elif self.position and self.data.close[0] < self.donchian.dcl[0]: self.sell()

class EmaCrossStrategy(bt.Strategy):
    params = (('n1', 12), ('n2', 26))
    def __init__(self):
        self.ema_fast = bt.indicators.EMA(self.data.close, period=self.params.n1)
        self.ema_slow = bt.indicators.EMA(self.data.close, period=self.params.n2)
        self.crossover = bt.indicators.CrossOver(self.ema_fast, self.ema_slow)
    def next(self):
        if not self.position and self.crossover > 0: self.buy()
        elif self.position and self.crossover < 0: self.sell()

class ATRTrailingStopStrategy(bt.Strategy):
    params = (('atr_period', 14), ('atr_multiplier', 3.0))
    def __init__(self):
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.trailing_stop = 0
        self.is_long = False
    def next(self):
        if not self.is_long:
            if self.data.close > bt.indicators.Highest(self.data.high, period=20)[-1]:
                self.buy()
                self.trailing_stop = self.data.close - (self.atr[0] * self.params.atr_multiplier)
                self.is_long = True
        else:
            new_stop = self.data.close - (self.atr[0] * self.params.atr_multiplier)
            self.trailing_stop = max(self.trailing_stop, new_stop)
            if self.data.close < self.trailing_stop:
                self.sell()
                self.is_long = False

class OpeningRangeBreakout(bt.Strategy):
    params = (('minutes', 15),)
    def __init__(self):
        pass
    def next(self):
        pass

# --- 6. STRATEGY DISPATCHER "REGISTRY" ---
STRATEGY_REGISTRY = {
    "SmaCrossStrategy": SmaCross,
    "RsiStrategy": RsiStrategy,
    "MultiInstrumentSignal": MultiInstrumentSignal,
    "BollingerBandsReversion": BollingerBandsReversion,
    "MACDStrategy": MACDStrategy,
    "StochasticStrategy": StochasticStrategy,
    "DonchianChannelBreakout": DonchianChannelBreakout,
    "EmaCrossStrategy": EmaCrossStrategy,
    "ATRTrailingStopStrategy": ATRTrailingStopStrategy,
    "OpeningRangeBreakout": OpeningRangeBreakout,
}