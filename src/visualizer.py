"""
Visualization tools for strategy performance analysis.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class PerformanceVisualizer:
    """Class for creating performance visualization charts."""
    
    def __init__(self, figsize=(12, 8)):
        self.figsize = figsize
        
    def plot_portfolio_performance(self, results: Dict, show_benchmark: bool = True):
        """
        Plot portfolio value over time.
        
        Args:
            results: Strategy backtest results
            show_benchmark: Whether to show benchmark comparison
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        portfolio_df = results['portfolio_history']
        
        # Portfolio value over time
        ax1.plot(portfolio_df.index, portfolio_df['Portfolio_Value'], 
                linewidth=2, label=results['strategy_name'])
        
        # Add benchmark if available
        if show_benchmark and 'benchmark_symbol' in results:
            # Calculate benchmark performance
            initial_value = results['initial_capital']
            benchmark_symbol = results['benchmark_symbol']
            
            ax1.axhline(y=initial_value, color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        
        ax1.set_title(f"{results['strategy_name']} - Portfolio Performance", fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Portfolio composition (cash vs positions)
        ax2.fill_between(portfolio_df.index, 0, portfolio_df['Cash'], 
                        alpha=0.7, label='Cash')
        ax2.fill_between(portfolio_df.index, portfolio_df['Cash'], 
                        portfolio_df['Portfolio_Value'], 
                        alpha=0.7, label='Positions Value')
        
        ax2.set_title('Portfolio Composition Over Time', fontsize=12)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Value ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_returns_distribution(self, results: Dict):
        """Plot distribution of daily returns."""
        portfolio_df = results['portfolio_history']
        returns = portfolio_df['Portfolio_Value'].pct_change().dropna() * 100
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram
        ax1.hist(returns, bins=50, alpha=0.7, edgecolor='black')
        ax1.axvline(returns.mean(), color='red', linestyle='--', 
                   label=f'Mean: {returns.mean():.3f}%')
        ax1.axvline(returns.median(), color='orange', linestyle='--', 
                   label=f'Median: {returns.median():.3f}%')
        ax1.set_title(f'{results["strategy_name"]} - Daily Returns Distribution')
        ax1.set_xlabel('Daily Return (%)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot for normality check
        from scipy import stats
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot (Normal Distribution)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_drawdown_analysis(self, results: Dict):
        """Plot drawdown analysis."""
        portfolio_df = results['portfolio_history']
        portfolio_values = portfolio_df['Portfolio_Value']
        
        # Calculate drawdowns
        running_max = portfolio_values.expanding().max()
        drawdowns = (portfolio_values - running_max) / running_max * 100
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Portfolio value with running max
        ax1.plot(portfolio_df.index, portfolio_values, label='Portfolio Value', linewidth=2)
        ax1.plot(portfolio_df.index, running_max, label='Running Maximum', 
                linestyle='--', alpha=0.8)
        ax1.fill_between(portfolio_df.index, portfolio_values, running_max, 
                        alpha=0.3, color='red', label='Drawdown Area')
        ax1.set_title(f'{results["strategy_name"]} - Portfolio Value and Drawdowns')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown percentage
        ax2.fill_between(portfolio_df.index, drawdowns, 0, alpha=0.7, color='red')
        ax2.plot(portfolio_df.index, drawdowns, color='darkred', linewidth=1)
        ax2.set_title('Drawdown Percentage Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        
        # Add max drawdown annotation
        max_dd_idx = drawdowns.idxmin()
        max_dd_value = drawdowns.min()
        ax2.annotate(f'Max Drawdown: {max_dd_value:.2f}%', 
                    xy=(max_dd_idx, max_dd_value),
                    xytext=(max_dd_idx, max_dd_value + 5),
                    arrowprops=dict(arrowstyle='->', color='black'),
                    fontsize=10, ha='center')
        
        plt.tight_layout()
        plt.show()
    
    def plot_strategy_comparison(self, results_list: List[Dict]):
        """
        Compare multiple strategies performance.
        
        Args:
            results_list: List of strategy results
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Portfolio values comparison
        ax1 = axes[0, 0]
        for result in results_list:
            portfolio_df = result['portfolio_history']
            normalized_values = portfolio_df['Portfolio_Value'] / result['initial_capital'] * 100
            ax1.plot(portfolio_df.index, normalized_values, 
                    linewidth=2, label=result['strategy_name'])
        
        ax1.set_title('Normalized Portfolio Performance Comparison')
        ax1.set_ylabel('Normalized Value (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Returns comparison
        ax2 = axes[0, 1]
        strategy_names = []
        total_returns = []
        annualized_returns = []
        
        for result in results_list:
            strategy_names.append(result['strategy_name'])
            total_returns.append(result['total_return'])
            
            metrics = result['performance_metrics']
            ann_ret = metrics.get('Annualized_Return_Pct', 0)
            annualized_returns.append(ann_ret)
        
        x = np.arange(len(strategy_names))
        width = 0.35
        
        ax2.bar(x - width/2, total_returns, width, label='Total Return', alpha=0.8)
        ax2.bar(x + width/2, annualized_returns, width, label='Annualized Return', alpha=0.8)
        ax2.set_title('Returns Comparison')
        ax2.set_ylabel('Return (%)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(strategy_names, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Risk-Return scatter
        ax3 = axes[1, 0]
        risks = []
        returns = []
        names = []
        
        for result in results_list:
            metrics = result['performance_metrics']  
            risk = metrics.get('Annualized_Volatility_Pct', 0)
            ret = metrics.get('Annualized_Return_Pct', 0)
            risks.append(risk)
            returns.append(ret)
            names.append(result['strategy_name'])
        
        scatter = ax3.scatter(risks, returns, s=100, alpha=0.7)
        for i, name in enumerate(names):
            ax3.annotate(name, (risks[i], returns[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax3.set_title('Risk-Return Profile')
        ax3.set_xlabel('Annualized Volatility (%)')
        ax3.set_ylabel('Annualized Return (%)')
        ax3.grid(True, alpha=0.3)
        
        # Sharpe ratios comparison
        ax4 = axes[1, 1]
        sharpe_ratios = []
        max_drawdowns = []
        
        for result in results_list:
            metrics = result['performance_metrics']
            sharpe = metrics.get('Sharpe_Ratio', 0)
            max_dd = abs(metrics.get('Max_Drawdown_Pct', 0))
            sharpe_ratios.append(sharpe)
            max_drawdowns.append(max_dd)
        
        x = np.arange(len(strategy_names))
        ax4_twin = ax4.twinx()
        
        bars1 = ax4.bar(x - 0.2, sharpe_ratios, 0.4, label='Sharpe Ratio', alpha=0.8)
        bars2 = ax4_twin.bar(x + 0.2, max_drawdowns, 0.4, 
                           label='Max Drawdown (%)', alpha=0.8, color='red')
        
        ax4.set_title('Risk-Adjusted Performance')
        ax4.set_ylabel('Sharpe Ratio', color='blue')
        ax4_twin.set_ylabel('Max Drawdown (%)', color='red')
        ax4.set_xticks(x)
        ax4.set_xticklabels(strategy_names, rotation=45, ha='right')
        
        # Combine legends
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def create_interactive_dashboard(self, results: Dict):
        """Create interactive dashboard with Plotly."""
        portfolio_df = results['portfolio_history']
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Portfolio Performance', 'Portfolio Composition',
                          'Daily Returns', 'Drawdown Analysis',
                          'Rolling Volatility', 'Cumulative Returns'),
            specs=[[{"secondary_y": False}, {"type": "scatter"}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Portfolio performance
        fig.add_trace(
            go.Scatter(x=portfolio_df.index, y=portfolio_df['Portfolio_Value'],
                      name='Portfolio Value', line=dict(width=2)),
            row=1, col=1
        )
        
        # Portfolio composition
        fig.add_trace(
            go.Scatter(x=portfolio_df.index, y=portfolio_df['Cash'],
                      fill='tonexty', name='Cash', opacity=0.7),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=portfolio_df.index, y=portfolio_df['Positions_Value'],
                      fill='tonexty', name='Positions', opacity=0.7),
            row=1, col=2
        )
        
        # Calculate additional metrics for other plots
        returns = portfolio_df['Portfolio_Value'].pct_change().dropna() * 100
        portfolio_values = portfolio_df['Portfolio_Value']
        running_max = portfolio_values.expanding().max()
        drawdowns = (portfolio_values - running_max) / running_max * 100
        rolling_vol = returns.rolling(window=30).std() * np.sqrt(252)
        cumulative_returns = (portfolio_values / portfolio_values.iloc[0] - 1) * 100
        
        # Daily returns
        fig.add_trace(
            go.Scatter(x=returns.index, y=returns.values,
                      mode='markers', name='Daily Returns', opacity=0.6),
            row=2, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(x=drawdowns.index, y=drawdowns.values,
                      fill='tonexty', name='Drawdown', line=dict(color='red')),
            row=2, col=2
        )
        
        # Rolling volatility
        fig.add_trace(
            go.Scatter(x=rolling_vol.index, y=rolling_vol.values,
                      name='30-Day Rolling Volatility'),
            row=3, col=1
        )
        
        # Cumulative returns
        fig.add_trace(
            go.Scatter(x=cumulative_returns.index, y=cumulative_returns.values,
                      name='Cumulative Return (%)', line=dict(width=2)),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f"{results['strategy_name']} - Performance Dashboard",
            height=900,
            showlegend=True
        )
        
        fig.show()
    
    def plot_trades_analysis(self, results: Dict):
        """Analyze and visualize trades."""
        if results['trades'].empty:
            print("No trades to analyze")
            return
        
        trades_df = results['trades']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Trades over time
        ax1 = axes[0, 0]
        buy_trades = trades_df[trades_df['Signal'] == 'BUY']
        sell_trades = trades_df[trades_df['Signal'] == 'SELL']
        
        ax1.scatter(buy_trades['Date'], buy_trades['Price'], 
                   color='green', alpha=0.7, label='Buy', s=50)
        ax1.scatter(sell_trades['Date'], sell_trades['Price'], 
                   color='red', alpha=0.7, label='Sell', s=50)
        ax1.set_title('Trade Execution Points')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Trade value distribution
        ax2 = axes[0, 1]
        trade_values = trades_df['Value'].abs()
        ax2.hist(trade_values, bins=20, alpha=0.7, edgecolor='black')
        ax2.set_title('Trade Value Distribution')
        ax2.set_xlabel('Trade Value ($)')
        ax2.set_ylabel('Frequency')
        ax2.grid(True, alpha=0.3)
        
        # Monthly trade count
        ax3 = axes[1, 0]
        trades_df['Month'] = pd.to_datetime(trades_df['Date']).dt.to_period('M')
        monthly_trades = trades_df.groupby('Month').size()
        monthly_trades.plot(kind='bar', ax=ax3)
        ax3.set_title('Monthly Trade Count')
        ax3.set_ylabel('Number of Trades')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Symbol distribution
        ax4 = axes[1, 1]
        symbol_counts = trades_df['Symbol'].value_counts()
        symbol_counts.plot(kind='pie', ax=ax4, autopct='%1.1f%%')
        ax4.set_title('Trades by Symbol')
        ax4.set_ylabel('')
        
        plt.tight_layout()
        plt.show()