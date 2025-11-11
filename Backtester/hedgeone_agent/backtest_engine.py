import backtrader as bt
import pandas as pd
from typing import List, Dict, Any

# Import from our package
from .strategies import STRATEGY_REGISTRY

def run_backtest_internal(strategy_id: str, data_feeds: List[pd.DataFrame], params_dict: Dict[str, Any]) -> str:
    """ Internal Backtrader runner. """
    
    StrategyClass = STRATEGY_REGISTRY.get(strategy_id)
    if not StrategyClass: return f"Error: Strategy '{strategy_id}' not found."
    if not data_feeds or all(df.empty for df in data_feeds): return "Error: No data provided."

    cerebro = bt.Cerebro()
    for df in data_feeds:
        if not df.empty:
            cerebro.adddata(bt.feeds.PandasData(dataname=df))

    cerebro.addstrategy(StrategyClass, **(params_dict or {}))
    
    start_cash = 100000.0
    cerebro.broker.setcash(start_cash)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    print(f"--- Running Backtest: {strategy_id} ---")
    results = cerebro.run()
    strategy_instance = results[0]
    
    final_value = cerebro.broker.getvalue()
    trade_analysis = strategy_instance.analyzers.trade.get_analysis() or {}
    sharpe_analysis = strategy_instance.analyzers.sharpe.get_analysis() or {}
    drawdown_analysis = strategy_instance.analyzers.drawdown.get_analysis() or {}

    total_trades = trade_analysis.get('total', {}).get('total', 0) if isinstance(trade_analysis, dict) else 0
    win_rate = (trade_analysis.get('won', {}).get('total', 0) / total_trades) * 100 if total_trades > 0 else 0
    
    sharpe_val = sharpe_analysis.get('sharperatio', 'N/A')
    # drawdown_analysis format can vary; handle safely
    drawdown_pct = 'N/A'
    try:
        if isinstance(drawdown_analysis, dict):
            drawdown_pct = drawdown_analysis.get('max', {}).get('drawdown', 'N/A')
        else:
            drawdown_pct = getattr(drawdown_analysis, 'max', {}).get('drawdown', 'N/A')
    except Exception:
        drawdown_pct = 'N/A'
    
    result_str = (
        f"Backtest for '{strategy_id}' Complete.\n"
        f"  Final Portfolio Value: ₹{final_value:,.2f}\n"
        f"  Total Return: {((final_value - start_cash) / start_cash) * 100:,.2f}%\n"
        f"  Sharpe Ratio: {sharpe_val}\n"
        f"  Max. Drawdown: {drawdown_pct}\n"
        f"  Total Trades: {total_trades}\n"
        f"  Win Rate: {win_rate:,.2f}%"
    )
    print(result_str)
    return result_str