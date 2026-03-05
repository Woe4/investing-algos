"""
Example script demonstrating the investing strategies framework.
"""
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append('src')

from src.data_fetcher import DataFetcher
from src.backtest_engine import BacktestEngine
from src.visualizer import PerformanceVisualizer
from src.strategies import (
    BuyAndHoldStrategy,
    MovingAverageCrossoverStrategy,
    MomentumStrategy,
    MeanReversionStrategy
)


def main():
    """Main function demonstrating the framework."""
    print("🚀 Investment Strategies Testing Framework")
    print("=" * 50)
    
    # Configuration
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    START_DATE = datetime.now() - timedelta(days=5*365)  # 5 years ago
    END_DATE = datetime.now()
    INITIAL_CAPITAL = 100000  # $100,000
    
    print(f"Testing period: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"Symbols: {SYMBOLS}")
    print(f"Initial capital: ${INITIAL_CAPITAL:,}")
    print()
    
    # Initialize framework components
    data_fetcher = DataFetcher(data_dir='data')
    backtest_engine = BacktestEngine(data_fetcher)
    visualizer = PerformanceVisualizer()
    
    # Initialize strategies
    strategies = [
        BuyAndHoldStrategy(initial_capital=INITIAL_CAPITAL),
        MovingAverageCrossoverStrategy(
            short_window=20, 
            long_window=50, 
            initial_capital=INITIAL_CAPITAL
        ),
        MomentumStrategy(
            rsi_period=14,
            initial_capital=INITIAL_CAPITAL
        ),
        MeanReversionStrategy(
            bb_period=20,
            initial_capital=INITIAL_CAPITAL
        )
    ]
    
    print(f"Testing {len(strategies)} strategies:")
    for strategy in strategies:
        print(f"  - {strategy.name}")
    print()
    
    # Run backtests
    results = []
    for i, strategy in enumerate(strategies, 1):
        print(f"[{i}/{len(strategies)}] Running backtest for {strategy.name}...")
        
        try:
            result = backtest_engine.run_backtest(
                strategy=strategy,
                symbols=SYMBOLS,
                start_date=START_DATE,
                end_date=END_DATE
            )
            results.append(result)
            print(f"✓ Completed: {result['total_return']:.2f}% total return")
            
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
        
        print()
    
    # Display results
    if results:
        print("📊 Results Summary")
        print("=" * 50)
        
        comparison_df = backtest_engine.compare_strategies(results)
        print(comparison_df.round(2))
        print()
        
        # Find best strategy
        best_strategy = max(results, key=lambda x: x['total_return'])
        print(f"🏆 Best Performing Strategy: {best_strategy['strategy_name']}")
        print(f"   Total Return: {best_strategy['total_return']:.2f}%")
        print(f"   Final Value: ${best_strategy['final_portfolio_value']:,.2f}")
        
        # Save results
        os.makedirs('results', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'results/strategy_comparison_{timestamp}.csv'
        comparison_df.to_csv(results_file)
        print(f"\n💾 Results saved to: {results_file}")
        
    else:
        print("❌ No successful backtests to display.")
    
    print("\n✅ Framework demonstration complete!")
    print("💡 Check the Jupyter notebook for detailed analysis and visualizations.")


if __name__ == "__main__":
    main()