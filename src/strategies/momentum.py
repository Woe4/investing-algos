"""
Momentum strategy based on price momentum and RSI.
"""
import pandas as pd
import numpy as np
from ..base_strategy import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy.
    
    Buy when:
    - RSI is oversold (< 30) and starting to recover
    - Price shows positive momentum
    
    Sell when:
    - RSI is overbought (> 70)
    - Price shows negative momentum
    """
    
    def __init__(self, rsi_period: int = 14, momentum_period: int = 10,
                 rsi_oversold: float = 30, rsi_overbought: float = 70,
                 initial_capital: float = 100000.0, **kwargs):
        super().__init__(
            name=f"Momentum (RSI {rsi_period})",
            initial_capital=initial_capital,
            **kwargs
        )
        self.rsi_period = rsi_period
        self.momentum_period = momentum_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_momentum(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate price momentum."""
        return prices.pct_change(periods=period)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on momentum and RSI.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with Signal values
        """
        if len(data) < max(self.rsi_period, self.momentum_period) + 5:
            return pd.Series(Signal.HOLD, index=data.index)
        
        # Calculate indicators
        rsi = self.calculate_rsi(data['Close'], self.rsi_period)
        momentum = self.calculate_momentum(data['Close'], self.momentum_period)
        short_ma = data['Close'].rolling(window=5).mean()
        
        # Initialize signals
        signals = pd.Series(Signal.HOLD, index=data.index)
        
        for i in range(2, len(data)):
            if pd.isna(rsi.iloc[i]) or pd.isna(momentum.iloc[i]):
                continue
            
            current_rsi = rsi.iloc[i]
            prev_rsi = rsi.iloc[i-1]
            current_momentum = momentum.iloc[i]
            current_price = data['Close'].iloc[i]
            current_ma = short_ma.iloc[i]
            
            # Buy conditions
            if (current_rsi > self.rsi_oversold and 
                prev_rsi <= self.rsi_oversold and 
                current_momentum > 0 and
                current_price > current_ma):
                signals.iloc[i] = Signal.BUY
            
            # Sell conditions
            elif (current_rsi > self.rsi_overbought or
                  current_momentum < -0.05 or  # Strong negative momentum
                  (current_rsi > 60 and current_momentum < 0)):
                signals.iloc[i] = Signal.SELL
        
        return signals