"""
Base strategy class for implementing trading strategies.
"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Signal(Enum):
    """Trading signals."""
    BUY = 1
    SELL = -1
    HOLD = 0


class Position:
    """Represents a position in a stock."""
    
    def __init__(self, symbol: str, shares: int, entry_price: float, 
                 entry_date: pd.Timestamp):
        self.symbol = symbol
        self.shares = shares
        self.entry_price = entry_price
        self.entry_date = entry_date
        
    @property
    def market_value(self) -> float:
        """Current market value of the position."""
        return abs(self.shares) * self.entry_price
    
    @property
    def is_long(self) -> bool:
        """Whether this is a long position."""
        return self.shares > 0
    
    @property
    def is_short(self) -> bool:
        """Whether this is a short position."""
        return self.shares < 0


class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    
    All strategies must implement the generate_signals method.
    """
    
    def __init__(self, name: str, initial_capital: float = 100000.0,
                 commission: float = 0.001, max_position_size: float = 0.2):
        """
        Initialize the base strategy.
        
        Args:
            name: Name of the strategy
            initial_capital: Initial capital amount
            commission: Commission rate per trade
            max_position_size: Maximum position size as fraction of portfolio
        """
        self.name = name
        self.initial_capital = initial_capital
        self.commission = commission
        self.max_position_size = max_position_size
        
        # Portfolio tracking
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.portfolio_value = initial_capital
        
        # Performance tracking
        self.trades = []
        self.portfolio_history = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on market data.
        
        Args:
            data: DataFrame with OHLCV data for a single stock
            
        Returns:
            Series with Signal values indexed by date
        """
        pass
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate common technical indicators.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional technical indicator columns
        """
        df = data.copy()
        
        # Moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / df['BB_Width']
        
        # Volume indicators
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Price momentum
        df['Returns'] = df['Close'].pct_change()
        df['Returns_5d'] = df['Close'].pct_change(periods=5)
        df['Returns_20d'] = df['Close'].pct_change(periods=20)
        
        # Volatility
        df['Volatility_20d'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
        
        return df
    
    def calculate_position_size(self, symbol: str, price: float) -> int:
        """
        Calculate optimal position size based on risk management rules.
        
        Args:
            symbol: Stock symbol
            price: Current stock price
            
        Returns:
            Number of shares to trade
        """
        max_investment = self.portfolio_value * self.max_position_size
        max_shares = int(max_investment / price)
        
        # Consider available cash
        available_shares = int(self.cash / price)
        
        return min(max_shares, available_shares)
    
    def execute_trade(self, symbol: str, signal: Signal, price: float, 
                     date: pd.Timestamp, shares: Optional[int] = None) -> bool:
        """
        Execute a trade based on the signal.
        
        Args:
            symbol: Stock symbol
            signal: Trading signal
            price: Execution price
            date: Trade date
            shares: Number of shares (calculated automatically if None)
            
        Returns:
            True if trade was executed, False otherwise
        """
        if signal == Signal.HOLD:
            return False
            
        if shares is None:
            shares = self.calculate_position_size(symbol, price)
            
        if shares <= 0:
            return False
            
        # Adjust shares based on signal
        if signal == Signal.SELL:
            shares = -shares
            
        # Calculate trade cost
        trade_value = abs(shares) * price
        commission_cost = trade_value * self.commission
        
        # Check if we have enough cash for buying
        if signal == Signal.BUY and (trade_value + commission_cost) > self.cash:
            return False
            
        # Execute the trade
        if symbol in self.positions:
            # Modify existing position
            old_position = self.positions[symbol]
            new_shares = old_position.shares + shares
            
            if new_shares == 0:
                # Close position
                del self.positions[symbol]
            else:
                # Update position
                self.positions[symbol].shares = new_shares
        else:
            # Create new position
            if shares > 0:  # Only create position for buys
                self.positions[symbol] = Position(symbol, shares, price, date)
        
        # Update cash
        if signal == Signal.BUY:
            self.cash -= (trade_value + commission_cost)
        else:  # SELL
            self.cash += (trade_value - commission_cost)
        
        # Record the trade
        self.trades.append({
            'Date': date,
            'Symbol': symbol,
            'Signal': signal.name,
            'Shares': shares,
            'Price': price,
            'Value': trade_value,
            'Commission': commission_cost,
            'Cash_After': self.cash
        })
        
        return True
    
    def update_portfolio_value(self, current_prices: Dict[str, float]):
        """
        Update current portfolio value based on current prices.
        
        Args:
            current_prices: Dictionary mapping symbols to current prices
        """
        positions_value = 0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                positions_value += position.shares * current_price
        
        self.portfolio_value = self.cash + positions_value
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary."""
        return {
            'Total_Value': self.portfolio_value,
            'Cash': self.cash,
            'Positions_Value': self.portfolio_value - self.cash,
            'Number_of_Positions': len(self.positions),
            'Total_Trades': len(self.trades)
        }
    
    def reset(self):
        """Reset strategy to initial state."""
        self.cash = self.initial_capital
        self.positions = {}
        self.portfolio_value = self.initial_capital
        self.trades = []
        self.portfolio_history = []