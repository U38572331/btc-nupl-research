import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_backtest():
    # Load data
    df_pricing = pd.read_csv('pricing_onchainoriginals.csv')
    df_nupl = pd.read_csv('unrealised_profitloss_ratio.csv')
    
    # Merge on Date to get Price alongside Realised Price
    df = pd.merge(df_pricing, df_nupl, on='Date')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.dropna(subset=['Price', 'Realised Price'])
    df = df.sort_values('Date').reset_index(drop=True)

    # Filter data starting from 2011 to avoid early noisy data
    df = df[df['Date'].dt.year >= 2011].copy()

    # Calculate MVRV Ratio and NUPL Combined Ratio
    df['MVRV'] = df['Price'] / df['Realised Price']
    df['Combined_NUPL_Ratio'] = np.where(
        df['Unrealised Profit/Loss Ratio (+ve)'] != 1.0, 
        df['Unrealised Profit/Loss Ratio (+ve)'], 
        df['Unrealised Profit/Loss Ratio (-ve)']
    )

    # Initialize variables
    position = 0  # 0 for USD, 1 for BTC
    usd_balance = 1.0  # Start with 1.0 unit of capital
    btc_balance = 0.0
    
    strategy_value = []
    buy_signals = []
    sell_signals = []
    
    buy_hold_balance_btc = usd_balance / df['Price'].iloc[0]

    for index, row in df.iterrows():
        # Check signals: Entry = NUPL Ratio < 1, Exit = Price > MVRV +2.0sd
        if row['Combined_NUPL_Ratio'] < 1.0 and position == 0:
            # Buy signal
            position = 1
            btc_balance = usd_balance / row['Price']
            usd_balance = 0.0
            buy_signals.append((row['Date'], row['Price'], row['Combined_NUPL_Ratio']))
        elif row['Price'] > row['MVRV +2.0sd (95%)'] and position == 1:
            # Sell signal
            position = 0
            usd_balance = btc_balance * row['Price']
            btc_balance = 0.0
            sell_signals.append((row['Date'], row['Price'], row['MVRV']))
            
        # Calculate current strategy value
        current_value = usd_balance if position == 0 else btc_balance * row['Price']
        strategy_value.append(current_value)

    df['Strategy_Return'] = strategy_value
    df['Buy_Hold_Return'] = buy_hold_balance_btc * df['Price']

    # Print summary statistics
    print(f"Initial Capital: $1.00")
    print(f"Final Strategy Value: ${df['Strategy_Return'].iloc[-1]:.2f} ({df['Strategy_Return'].iloc[-1]}x)")
    print(f"Final Buy & Hold Value: ${df['Buy_Hold_Return'].iloc[-1]:.2f} ({df['Buy_Hold_Return'].iloc[-1]}x)")
    print(f"Total Trades Executed: {len(buy_signals) + len(sell_signals)}")

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [2, 1]})

    # Top Plot: Cumulative Returns
    ax1.plot(df['Date'], df['Strategy_Return'], label='Strategy (Buy MVRV<1, Sell +2.0sd)', color='blue', linewidth=2)
    ax1.plot(df['Date'], df['Buy_Hold_Return'], label='Buy & Hold', color='orange', alpha=0.7, linestyle='--')
    ax1.set_yscale('log')
    ax1.set_title('Cumulative Return Comparison: On-Chain Strategy vs Buy & Hold', fontsize=16)
    ax1.set_ylabel('Portfolio Value (Log Scale)')
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend(loc='upper left')

    # Bottom Plot: MVRV Ratio and Signals
    ax2.plot(df['Date'], df['Combined_NUPL_Ratio'], label='NUPL Ratio', color='purple', linewidth=1)
    ax2.plot(df['Date'], df['MVRV +2.0sd (95%)'] / df['Realised Price'], label='+2.0sd Exit Band', color='red', linestyle=':', alpha=0.5)
    ax2.axhline(y=1.0, color='green', linestyle='--', label='Entry Threshold (NUPL < 1.0)')
    
    # Mark buy/sell signals on ax2
    buy_dates = [s[0] for s in buy_signals]
    buy_mvrv = [s[2] for s in buy_signals]
    sell_dates = [s[0] for s in sell_signals]
    sell_mvrv = [s[2] for s in sell_signals]

    ax2.scatter(buy_dates, buy_mvrv, color='green', marker='^', s=100, label='Buy Signal', zorder=5)
    ax2.scatter(sell_dates, sell_mvrv, color='red', marker='v', s=100, label='Sell Signal', zorder=5)

    ax2.set_title('NUPL Ratio with Trade Signals', fontsize=14)
    ax2.set_ylabel('Ratio')
    ax2.set_xlabel('Date')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.savefig('mvrv_strategy_comparison.png', dpi=300)
    print("Chart saved to mvrv_strategy_comparison.png")

if __name__ == "__main__":
    run_backtest()
