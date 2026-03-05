"""
Moving average crossover strategy.
"""
import pandas as pd
import numpy as np
from ..base_strategy import BaseStrategy, Signal


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover Strategy.
    
    Buy when short MA crosses above long MA.
    Sell when short MA crosses below long MA.
    """
    
    def __init__(self, short_window: int = 20, long_window: int = 50, 
                 initial_capital: float = 100000.0, **kwargs):
        super().__init__(
            name=f"MA Crossover ({short_window}/{long_window})",
            initial_capital=initial_capital,
            **kwargs
        )
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on moving average crossover.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with Signal values
        """
        if len(data) < self.long_window:
            return pd.Series(Signal.HOLD, index=data.index)
        
        # Calculate moving averages
        short_ma = data['Close'].rolling(window=self.short_window).mean()
        long_ma = data['Close'].rolling(window=self.long_window).mean()
        
        # Initialize signals
        signals = pd.Series(Signal.HOLD, index=data.index)
        
        # Generate crossover signals
        for i in range(1, len(data)):
            if pd.isna(short_ma.iloc[i]) or pd.isna(long_ma.iloc[i]):
                continue
                
            current_short = short_ma.iloc[i]
            current_long = long_ma.iloc[i]
            prev_short = short_ma.iloc[i-1]
            prev_long = long_ma.iloc[i-1]
            
            # Golden cross: short MA crosses above long MA
            if prev_short <= prev_long and current_short > current_long:
                signals.iloc[i] = Signal.BUY
            # Death cross: short MA crosses below long MA
            elif prev_short >= prev_long and current_short < current_long:
                signals.iloc[i] = Signal.SELL
        
        return signals