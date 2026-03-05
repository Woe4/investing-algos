"""
Simple buy and hold strategy - buy at the beginning and hold until the end.
"""
import pandas as pd
import numpy as np
from ..base_strategy import BaseStrategy, Signal


class BuyAndHoldStrategy(BaseStrategy):
    """
    Simple buy and hold strategy.
    Buys at the first available opportunity and holds until the end.
    """
    
    def __init__(self, initial_capital: float = 100000.0, **kwargs):
        super().__init__(
            name="Buy and Hold",
            initial_capital=initial_capital,
            **kwargs
        )
        self.has_bought = False
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate buy signal on first day, then hold.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with Signal values
        """
        signals = pd.Series(Signal.HOLD, index=data.index)
        
        # Buy on the first date
        if not data.empty and not self.has_bought:
            signals.iloc[0] = Signal.BUY
            self.has_bought = True
        
        return signals
    
    def reset(self):
        """Reset strategy state."""
        super().reset()
        self.has_bought = False