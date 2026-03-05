"""
Data fetching and management module for stock market data.
"""
import os
import pandas as pd
import yfinance as yf
from typing import List, Dict, Optional
from datetime import datetime
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Class for fetching and caching stock market data."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_stock_data(self, symbol: str, start_date: datetime, 
                      end_date: datetime, force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch stock data for a given symbol and date range.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for data
            end_date: End date for data
            force_refresh: Whether to force refresh cached data
            
        Returns:
            DataFrame with OHLCV data
        """
        # Create cache filename
        cache_file = os.path.join(
            self.data_dir, 
            f"{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pkl"
        )
        
        # Try to load from cache first
        if os.path.exists(cache_file) and not force_refresh:
            try:
                logger.info(f"Loading cached data for {symbol}")
                return pd.read_pickle(cache_file)
            except Exception as e:
                logger.warning(f"Failed to load cache for {symbol}: {e}")
        
        # Fetch fresh data from Yahoo Finance
        try:
            logger.info(f"Fetching fresh data for {symbol}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data found for {symbol}")
            
            # Add symbol column
            data['Symbol'] = symbol
            
            # Save to cache
            data.to_pickle(cache_file)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise
    
    def get_multiple_stocks(self, symbols: List[str], start_date: datetime,
                          end_date: datetime, force_refresh: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks.
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date for data
            end_date: End date for data
            force_refresh: Whether to force refresh cached data
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data_dict = {}
        
        for symbol in symbols:
            try:
                data_dict[symbol] = self.get_stock_data(
                    symbol, start_date, end_date, force_refresh
                )
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                continue
                
        return data_dict
    
    def get_combined_data(self, symbols: List[str], start_date: datetime,
                         end_date: datetime, price_column: str = 'Close') -> pd.DataFrame:
        """
        Get combined price data for multiple symbols in a single DataFrame.
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date for data
            end_date: End date for data
            price_column: Which price column to use ('Close', 'Adj Close', etc.)
            
        Returns:
            DataFrame with symbols as columns and dates as index
        """
        data_dict = self.get_multiple_stocks(symbols, start_date, end_date)
        
        price_data = {}
        for symbol, df in data_dict.items():
            if not df.empty and price_column in df.columns:
                price_data[symbol] = df[price_column]
        
        combined_df = pd.DataFrame(price_data)
        combined_df.index.name = 'Date'
        
        return combined_df
    
    def calculate_returns(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily returns from price data."""
        return price_data.pct_change().dropna()
    
    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cached data files.
        
        Args:
            symbol: If provided, clear cache for specific symbol only
        """
        if symbol:
            pattern = f"{symbol}_"
            files_to_remove = [f for f in os.listdir(self.data_dir) if f.startswith(pattern)]
        else:
            files_to_remove = [f for f in os.listdir(self.data_dir) if f.endswith('.pkl')]
        
        for file in files_to_remove:
            file_path = os.path.join(self.data_dir, file)
            try:
                os.remove(file_path)
                logger.info(f"Removed cache file: {file}")
            except Exception as e:
                logger.error(f"Failed to remove {file}: {e}")