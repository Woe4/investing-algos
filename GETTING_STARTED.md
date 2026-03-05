# Getting Started Guide

## 🚀 Quick Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Quick Test**:
   ```bash
   python quick_test.py
   ```

3. **Run Full Demo**:
   ```bash
   python main.py
   ```

4. **Open Jupyter Notebook**:
   ```bash
   jupyter notebook notebooks/strategy_testing_demo.ipynb
   ```

## 📝 Basic Usage

### Fetch Historical Data
```python
from src.data_fetcher import DataFetcher
from datetime import datetime, timedelta

fetcher = DataFetcher()
data = fetcher.get_stock_data(
    'AAPL', 
    datetime.now() - timedelta(days=365),
    datetime.now()
)
```

### Test a Strategy  
```python
from src.strategies import BuyAndHoldStrategy
from src.backtest_engine import BacktestEngine

# Create strategy
strategy = BuyAndHoldStrategy(initial_capital=100000)

# Run backtest
engine = BacktestEngine(fetcher)
results = engine.run_backtest(
    strategy, 
    ['AAPL', 'MSFT'], 
    start_date, 
    end_date
)
```

### Visualize Results
```python
from src.visualizer import PerformanceVisualizer

viz = PerformanceVisualizer()
viz.plot_portfolio_performance(results)
viz.plot_drawdown_analysis(results)
```

## 🎯 Available Strategies

- `BuyAndHoldStrategy`: Simple buy and hold
- `MovingAverageCrossoverStrategy`: MA crossover signals  
- `MomentumStrategy`: RSI-based momentum trading
- `MeanReversionStrategy`: Bollinger Bands mean reversion

## 🔧 Custom Strategy Example

```python
from src.base_strategy import BaseStrategy, Signal
import pandas as pd

class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        signals = pd.Series(Signal.HOLD, index=data.index)
        
        # Your trading logic here
        # Example: Buy when price > 20-day MA
        ma20 = data['Close'].rolling(20).mean()
        signals[data['Close'] > ma20] = Signal.BUY
        signals[data['Close'] < ma20] = Signal.SELL
        
        return signals
```

## 📊 Key Features

✅ **Data Management**: Automatic caching, Yahoo Finance integration  
✅ **Backtesting**: Realistic trading costs, portfolio tracking  
✅ **Performance Metrics**: Sharpe ratio, drawdowns, alpha/beta  
✅ **Visualization**: Charts, interactive dashboards  
✅ **Extensible**: Easy to add custom strategies  

## 🚨 Next Steps

1. Run the quick test to verify everything works
2. Explore the Jupyter notebook for detailed examples  
3. Try modifying existing strategies
4. Create your own custom strategy
5. Test on different time periods and symbols

## 💡 Tips

- Start with small capital amounts for testing
- Use 1-2 years of data initially to speed up testing  
- Check the `data/` folder for cached files
- Results are saved in `results/` folder
- Use `force_refresh=True` to get fresh data

## 🆘 Common Issues

**Import Errors**: Make sure you're in the project directory  
**Data Fetch Fails**: Check internet connection, try different symbols  
**Slow Performance**: Reduce date range or number of symbols  
**Memory Issues**: Use smaller datasets or clear cache

Happy testing! 🎉