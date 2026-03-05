"""
Configuration settings for the investing strategies testing framework.
"""
from datetime import datetime, timedelta
from typing import List

# Data Configuration
DEFAULT_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'NVDA', 'META', 'BRK-B', 'JNJ', 'V',
    'SPY', 'QQQ', 'VTI', 'IWM'  # ETFs for benchmarking
]

# Time Configuration
DEFAULT_START_DATE = datetime.now() - timedelta(days=5*365)  # 5 years ago
DEFAULT_END_DATE = datetime.now()

# Initial Portfolio Configuration
INITIAL_CAPITAL = 100000.0  # $100,000
DEFAULT_COMMISSION = 0.001  # 0.1% commission per trade

# Risk Management
MAX_POSITION_SIZE = 0.2  # Max 20% of portfolio in single position
STOP_LOSS_THRESHOLD = -0.05  # 5% stop loss

# Data Directories
DATA_DIR = 'data'
RESULTS_DIR = 'results'

# Technical Analysis Parameters
SHORT_MA_PERIOD = 20
LONG_MA_PERIOD = 50
RSI_PERIOD = 14
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# Backtesting Configuration
REBALANCE_FREQUENCY = 'daily'  # daily, weekly, monthly
BENCHMARK_SYMBOL = 'SPY'