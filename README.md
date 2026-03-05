# Investment Strategies Testing Framework

A comprehensive Python framework for testing different investment strategies on historical stock market data from the past 5 years.

## 🚀 Features

- **Data Management**: Automated fetching and caching of historical stock data from Yahoo Finance
- **Strategy Library**: Built-in implementations of popular trading strategies
- **Backtesting Engine**: Realistic simulation with transaction costs and risk management
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, max drawdown, alpha, beta
- **Visualizations**: Static and interactive charts for performance analysis
- **Extensible Design**: Easy to add custom strategies and indicators

## 📁 Project Structure

```
investing-algos/
├── src/
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── buy_and_hold.py
│   │   ├── moving_average.py
│   │   ├── momentum.py
│   │   └── mean_reversion.py
│   ├── data_fetcher.py
│   ├── base_strategy.py
│   ├── backtest_engine.py
│   └── visualizer.py
├── notebooks/
│   └── strategy_testing_demo.ipynb
├── data/               # Cached stock data
├── results/           # Backtest results
├── config.py
├── main.py
└── requirements.txt
```

## 🛠️ Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Built-in Strategies

1. **Buy and Hold**: Simple buy-and-hold strategy
2. **Moving Average Crossover**: Golden/Death cross signals using 20/50-day MAs
3. **Momentum Strategy**: RSI-based momentum trading with trend confirmation
4. **Mean Reversion**: Bollinger Bands-based contrarian strategy

## 🚦 Quick Start

### Option 1: Run the Demo Script
```bash
python main.py
```

### Option 2: Use the Jupyter Notebook
```bash
jupyter notebook notebooks/strategy_testing_demo.ipynb
```

### Option 3: Custom Implementation
```python
from src.data_fetcher import DataFetcher
from src.backtest_engine import BacktestEngine
from src.strategies import BuyAndHoldStrategy
from datetime import datetime, timedelta

# Initialize components
data_fetcher = DataFetcher()
engine = BacktestEngine(data_fetcher)

# Create strategy
strategy = BuyAndHoldStrategy(initial_capital=100000)

# Run backtest
results = engine.run_backtest(
    strategy=strategy,
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    start_date=datetime.now() - timedelta(days=5*365),
    end_date=datetime.now()
)

print(f"Total Return: {results['total_return']:.2f}%")
```

## 📊 Performance Metrics

The framework calculates comprehensive performance metrics:

- **Returns**: Total, annualized, and risk-adjusted returns
- **Risk Metrics**: Volatility, maximum drawdown, beta, correlation
- **Ratios**: Sharpe ratio, Calmar ratio, alpha (Jensen's alpha)
- **Trade Analytics**: Win rate, average win/loss, trade frequency

## 🎨 Visualizations

- Portfolio performance over time
- Drawdown analysis
- Returns distribution
- Strategy comparison charts
- Interactive dashboards (with Plotly)
- Trade execution analysis

## 🔧 Creating Custom Strategies

Extend the `BaseStrategy` class to implement your own trading logic:

```python
from src.base_strategy import BaseStrategy, Signal

class MyCustomStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(name="My Custom Strategy", **kwargs)
    
    def generate_signals(self, data):
        # Implement your trading logic here
        signals = pd.Series(Signal.HOLD, index=data.index)
        
        # Example: Buy when RSI < 30, Sell when RSI > 70
        rsi = self.calculate_rsi(data['Close'])
        signals[rsi < 30] = Signal.BUY
        signals[rsi > 70] = Signal.SELL
        
        return signals
```

## 📈 Example Results

```
Strategy Performance Comparison:
                        Total_Return_%  Sharpe_Ratio  Max_Drawdown_%
Buy and Hold                   45.23         1.34           -15.67
MA Crossover (20/50)           38.91         1.12           -12.45
Momentum (RSI 14)              52.67         1.51           -18.23
Mean Reversion (BB 20)         41.33         1.28           -14.12
```

## 🔄 Data Management

- Automatic data fetching from Yahoo Finance
- Intelligent caching to avoid redundant API calls
- Support for multiple timeframes and symbols
- Data validation and cleaning

## ⚙️ Configuration

Customize the framework behavior in `config.py`:

```python
# Trading Configuration
INITIAL_CAPITAL = 100000.0
DEFAULT_COMMISSION = 0.001  # 0.1% per trade
MAX_POSITION_SIZE = 0.2     # Max 20% per position

# Technical Analysis Parameters
RSI_PERIOD = 14
BOLLINGER_PERIOD = 20
SHORT_MA_PERIOD = 20
LONG_MA_PERIOD = 50
```

## 🚨 Risk Management Features

- Position sizing limits
- Transaction cost modeling
- Cash management
- Portfolio-level risk controls
- Stop-loss capabilities (customizable)

## 📋 Requirements

- Python 3.8+
- pandas
- numpy
- yfinance
- matplotlib
- seaborn
- plotly (optional, for interactive charts)
- scipy
- scikit-learn
- jupyter

## 🤝 Contributing

This framework is designed to be extensible. Areas for enhancement:

- Additional technical indicators
- Machine learning-based strategies
- Portfolio optimization algorithms
- Real-time trading capabilities
- More sophisticated risk management
- Options and derivatives support

## ⚠️ Disclaimer

This framework is for educational and research purposes only. Past performance does not guarantee future results. Always conduct thorough testing and consider consulting with financial professionals before implementing any trading strategy with real money.

## 📝 License

MIT License - see LICENSE file for details.

## 📞 Support

For questions or issues, please create an issue in the repository or refer to the comprehensive documentation in the Jupyter notebook.