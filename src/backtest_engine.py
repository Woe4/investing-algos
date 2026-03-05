"""
Backtesting engine for testing trading strategies.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .base_strategy import BaseStrategy
from .data_fetcher import DataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Engine for backtesting trading strategies.
    """
    
    def __init__(self, data_fetcher: DataFetcher):
        self.data_fetcher = data_fetcher
        self.results: Dict[str, Dict] = {}
    
    def run_backtest(self, strategy: BaseStrategy, symbols: List[str], 
                    start_date: datetime, end_date: datetime,
                    benchmark_symbol: str = 'SPY') -> Dict:
        """
        Run backtest for a single strategy on multiple symbols.
        
        Args:
            strategy: Strategy instance to test
            symbols: List of symbols to trade
            start_date: Start date for backtest
            end_date: End date for backtest
            benchmark_symbol: Symbol to use as benchmark
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest for {strategy.name}")
        
        # Reset strategy
        strategy.reset()
        
        # Get data for all symbols
        logger.info("Fetching market data...")
        data_dict = self.data_fetcher.get_multiple_stocks(symbols, start_date, end_date)
        
        if not data_dict:
            raise ValueError("No data found for any symbols")
        
        # Get benchmark data
        benchmark_data = self.data_fetcher.get_stock_data(benchmark_symbol, start_date, end_date)
        
        # Create combined price matrix for portfolio value tracking
        price_data = {}
        for symbol, df in data_dict.items():
            if not df.empty:
                price_data[symbol] = df['Close']
        combined_prices = pd.DataFrame(price_data)
        
        # Track portfolio value over time
        portfolio_history = []
        
        # Get all trading dates
        all_dates = sorted(set().union(*[df.index for df in data_dict.values()]))
        
        for date in all_dates:
            daily_prices = {}
            
            # Process each symbol for this date
            for symbol in symbols:
                if (symbol in data_dict and 
                    not data_dict[symbol].empty and 
                    date in data_dict[symbol].index):
                    
                    # Get data up to current date for signal generation
                    historical_data = data_dict[symbol].loc[:date]
                    
                    if len(historical_data) < 2:
                        continue
                    
                    # Add technical indicators
                    historical_data = strategy.calculate_technical_indicators(historical_data)
                    
                    # Generate signals
                    signals = strategy.generate_signals(historical_data)
                    
                    if date in signals.index:
                        signal = signals.loc[date]
                        current_price = data_dict[symbol].loc[date, 'Close']
                        
                        # Execute trade if signal is not HOLD
                        strategy.execute_trade(symbol, signal, current_price, date)
                        
                        daily_prices[symbol] = current_price
            
            # Update portfolio value
            if daily_prices:
                strategy.update_portfolio_value(daily_prices)
                
                portfolio_history.append({
                    'Date': date,
                    'Portfolio_Value': strategy.portfolio_value,
                    'Cash': strategy.cash,
                    'Positions_Value': strategy.portfolio_value - strategy.cash
                })
        
        # Create results DataFrame
        portfolio_df = pd.DataFrame(portfolio_history).set_index('Date')
        
        # Calculate performance metrics
        performance_metrics = self.calculate_performance_metrics(
            portfolio_df, benchmark_data, strategy.initial_capital
        )
        
        # Prepare results
        results = {
            'strategy_name': strategy.name,
            'symbols': symbols,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': strategy.initial_capital,
            'final_portfolio_value': strategy.portfolio_value,
            'total_return': (strategy.portfolio_value / strategy.initial_capital - 1) * 100,
            'portfolio_history': portfolio_df,
            'trades': pd.DataFrame(strategy.trades),
            'final_positions': strategy.positions,
            'performance_metrics': performance_metrics,
            'benchmark_symbol': benchmark_symbol
        }
        
        self.results[strategy.name] = results
        
        logger.info(f"Backtest completed for {strategy.name}")
        logger.info(f"Total Return: {results['total_return']:.2f}%")
        
        return results
    
    def calculate_performance_metrics(self, portfolio_df: pd.DataFrame, 
                                    benchmark_data: pd.DataFrame,
                                    initial_capital: float) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            portfolio_df: DataFrame with portfolio values over time
            benchmark_data: Benchmark price data
            initial_capital: Initial capital amount
            
        Returns:
            Dictionary with performance metrics
        """
        if portfolio_df.empty:
            return {}
        
        # Portfolio returns
        portfolio_values = portfolio_df['Portfolio_Value']
        portfolio_returns = portfolio_values.pct_change().dropna()
        
        # Benchmark returns (aligned with portfolio dates)
        benchmark_aligned = benchmark_data.reindex(portfolio_df.index, method='ffill')
        benchmark_returns = benchmark_aligned['Close'].pct_change().dropna()
        
        # Basic metrics
        total_return = (portfolio_values.iloc[-1] / initial_capital - 1) * 100
        
        # Annualized metrics
        days = (portfolio_df.index[-1] - portfolio_df.index[0]).days
        years = days / 365.25
        
        annualized_return = ((portfolio_values.iloc[-1] / initial_capital) ** (1/years) - 1) * 100
        
        # Volatility
        annualized_volatility = portfolio_returns.std() * np.sqrt(252) * 100
        
        # Sharpe Ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        excess_returns = portfolio_returns - risk_free_rate/252
        sharpe_ratio = (excess_returns.mean() / portfolio_returns.std()) * np.sqrt(252)
        
        # Maximum Drawdown
        running_max = portfolio_values.expanding().max()
        drawdowns = (portfolio_values - running_max) / running_max * 100
        max_drawdown = drawdowns.min()
        
        # Calmar Ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Win/Loss metrics
        positive_returns = portfolio_returns[portfolio_returns > 0]
        negative_returns = portfolio_returns[portfolio_returns < 0]
        
        win_rate = len(positive_returns) / len(portfolio_returns) * 100
        avg_win = positive_returns.mean() * 100 if len(positive_returns) > 0 else 0
        avg_loss = negative_returns.mean() * 100 if len(negative_returns) > 0 else 0
        
        # Beta (if benchmark data is available)
        beta = np.nan
        alpha = np.nan
        correlation = np.nan
        
        if not benchmark_returns.empty:
            aligned_portfolio = portfolio_returns.reindex(benchmark_returns.index).dropna()
            aligned_benchmark = benchmark_returns.reindex(aligned_portfolio.index).dropna()
            
            if len(aligned_portfolio) > 10 and len(aligned_benchmark) > 10:
                correlation = aligned_portfolio.corr(aligned_benchmark)
                
                # Beta calculation
                covariance = np.cov(aligned_portfolio, aligned_benchmark)[0, 1]
                benchmark_variance = np.var(aligned_benchmark)
                beta = covariance / benchmark_variance if benchmark_variance != 0 else np.nan
                
                # Alpha calculation (Jensen's Alpha)
                benchmark_annualized = (aligned_benchmark.mean() + 1) ** 252 - 1
                portfolio_annualized = (aligned_portfolio.mean() + 1) ** 252 - 1
                alpha = (portfolio_annualized - risk_free_rate - 
                        beta * (benchmark_annualized - risk_free_rate)) * 100
        
        metrics = {
            'Total_Return_Pct': total_return,
            'Annualized_Return_Pct': annualized_return,
            'Annualized_Volatility_Pct': annualized_volatility,
            'Sharpe_Ratio': sharpe_ratio,
            'Max_Drawdown_Pct': max_drawdown,
            'Calmar_Ratio': calmar_ratio,
            'Win_Rate_Pct': win_rate,
            'Average_Win_Pct': avg_win,
            'Average_Loss_Pct': avg_loss,
            'Beta': beta,
            'Alpha_Pct': alpha,
            'Correlation_with_Benchmark': correlation,
            'Total_Days': days,
            'Total_Years': years
        }
        
        return {k: v for k, v in metrics.items() if pd.notna(v)}
    
    def compare_strategies(self, results_list: List[Dict]) -> pd.DataFrame:
        """
        Compare multiple strategy results.
        
        Args:
            results_list: List of strategy results dictionaries
            
        Returns:
            DataFrame comparing strategy performance
        """
        comparison_data = []
        
        for result in results_list:
            metrics = result['performance_metrics']
            comparison_data.append({
                'Strategy': result['strategy_name'],
                'Total_Return_%': result['total_return'],
                'Annualized_Return_%': metrics.get('Annualized_Return_Pct', 0),
                'Volatility_%': metrics.get('Annualized_Volatility_Pct', 0),
                'Sharpe_Ratio': metrics.get('Sharpe_Ratio', 0),
                'Max_Drawdown_%': metrics.get('Max_Drawdown_Pct', 0),
                'Win_Rate_%': metrics.get('Win_Rate_Pct', 0),
                'Final_Value': result['final_portfolio_value'],
                'Number_of_Trades': len(result['trades']) if not result['trades'].empty else 0
            })
        
        return pd.DataFrame(comparison_data).set_index('Strategy')