"""
Simple example script to test a single strategy quickly.
"""
import sys
sys.path.append('src')

from src.data_fetcher import DataFetcher
from src.backtest_engine import BacktestEngine
from src.strategies import BuyAndHoldStrategy
from datetime import datetime, timedelta


def quick_test():
    """Run a quick test with a single strategy."""
    print("🚀 Quick Strategy Test")
    print("=" * 30)
    
    # Configuration  
    SYMBOL = 'AAPL'
    START_DATE = datetime.now() - timedelta(days=365)  # 1 year
    END_DATE = datetime.now()
    INITIAL_CAPITAL = 10000  # $10,000
    
    print(f"Testing: {SYMBOL}")
    print(f"Period: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"Capital: ${INITIAL_CAPITAL:,}")
    print()
    
    # Initialize components
    data_fetcher = DataFetcher(data_dir='data')
    engine = BacktestEngine(data_fetcher)
    
    # Test strategy
    strategy = BuyAndHoldStrategy(initial_capital=INITIAL_CAPITAL)
    
    print(f"🧪 Testing: {strategy.name}")
    
    try:
        # Run backtest
        result = engine.run_backtest(
            strategy=strategy,
            symbols=[SYMBOL],
            start_date=START_DATE,
            end_date=END_DATE
        )
        
        # Display results
        print(f"✅ Backtest completed!")
        print(f"📊 Results:")
        print(f"   Initial Value: ${result['initial_capital']:,.2f}")
        print(f"   Final Value:   ${result['final_portfolio_value']:,.2f}")
        print(f"   Total Return:  {result['total_return']:.2f}%")
        print(f"   Total Trades:  {len(result['trades'])}")
        
        # Performance metrics
        metrics = result['performance_metrics']
        if metrics:
            print(f"📈 Performance Metrics:")
            for key, value in metrics.items():
                if 'Pct' in key:
                    print(f"   {key.replace('_', ' ').replace('Pct', ''): <20}: {value:.2f}%")
                elif 'Ratio' in key:
                    print(f"   {key.replace('_', ' '): <20}: {value:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✨ Test complete!")


if __name__ == "__main__":
    quick_test()