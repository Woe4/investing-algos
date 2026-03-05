"""
Mean reversion strategy using Bollinger Bands.
"""
import pandas as pd
import numpy as np
from ..base_strategy import BaseStrategy, Signal


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using Bollinger Bands.
    
    Buy when price touches lower Bollinger Band (oversold).
    Sell when price touches upper Bollinger Band (overbought).
    """
    
    def __init__(self, bb_period: int = 20, bb_std: float = 2.0,
                 volume_threshold: float = 1.2, initial_capital: float = 100000.0, **kwargs):
        super().__init__(
            name=f"Mean Reversion (BB {bb_period})",
            initial_capital=initial_capital,
            **kwargs
        )
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.volume_threshold = volume_threshold
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> tuple:
        """Calculate Bollinger Bands."""
        middle = prices.rolling(window=self.bb_period).mean()
        std = prices.rolling(window=self.bb_period).std()
        upper = middle + (std * self.bb_std)
        lower = middle - (std * self.bb_std)
        return upper, middle, lower
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate signals based on Bollinger Bands mean reversion.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Series with Signal values
        """
        if len(data) < self.bb_period + 5:
            return pd.Series(Signal.HOLD, index=data.index)
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(data['Close'])
        
        # Calculate volume moving average
        volume_ma = data['Volume'].rolling(window=self.bb_period).mean()
        
        # Calculate RSI for additional confirmation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Initialize signals
        signals = pd.Series(Signal.HOLD, index=data.index)
        
        for i in range(1, len(data)):
            if (pd.isna(bb_upper.iloc[i]) or pd.isna(bb_lower.iloc[i]) or 
                pd.isna(volume_ma.iloc[i])):
                continue
            
            current_price = data['Close'].iloc[i]
            prev_price = data['Close'].iloc[i-1]
            current_volume = data['Volume'].iloc[i]
            avg_volume = volume_ma.iloc[i]
            current_rsi = rsi.iloc[i] if not pd.isna(rsi.iloc[i]) else 50
            
            # Buy signal: price near lower band with volume confirmation
            if (current_price <= bb_lower.iloc[i] and 
                prev_price > bb_lower.iloc[i-1] and
                current_volume > avg_volume * self.volume_threshold and
                current_rsi < 35):  # Additional RSI confirmation
                signals.iloc[i] = Signal.BUY
            
            # Sell signal: price near upper band or back to middle
            elif (current_price >= bb_upper.iloc[i] or
                  (current_price >= bb_middle.iloc[i] and 
                   prev_price < bb_middle.iloc[i-1] and
                   current_rsi > 65)):
                signals.iloc[i] = Signal.SELL
        
        return signals