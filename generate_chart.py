import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def generate_nupl_chart():
    # Read the real extracted data
    df = pd.read_csv('unrealised_profitloss_ratio.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.dropna(subset=['Price']) # Remove rows where price is NaN
    
    # Calculate combined ratio
    df['Combined Ratio'] = np.where(
        df['Unrealised Profit/Loss Ratio (+ve)'] != 1.0, 
        df['Unrealised Profit/Loss Ratio (+ve)'], 
        df['Unrealised Profit/Loss Ratio (-ve)']
    )

    # Filter to view from 2011 onwards to avoid early noisy data
    df = df[df['Date'].dt.year >= 2011].copy()

    # Create figure and two subplots (Price on top, Ratio on bottom)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    from matplotlib.ticker import FuncFormatter
    formatter = FuncFormatter(lambda y, _: '{:g}'.format(y))

    # ------------------ TOP PLOT: Bitcoin Price ------------------
    ax1.set_title('Bitcoin Price & Unrealised Profit/Loss Ratio (NUPL)', fontsize=16, pad=15)
    ax1.set_ylabel('BTC Price (USD)', color='black', fontsize=12)
    ax1.set_yscale('log')
    ax1.yaxis.set_major_formatter(formatter)
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # Plot base price line
    ax1.plot(df['Date'], df['Price'], color='tab:gray', linewidth=1.5, label='BTC Price (Normal)')

    # Highlight price when Ratio < 1.0
    bottom_zones = df['Combined Ratio'] < 1.0
    
    # To color the line specifically in bottom zones, we overlay a scatter or masked plot
    df_bottoms = df[bottom_zones]
    ax1.scatter(df_bottoms['Date'], df_bottoms['Price'], color='red', s=10, label='Price in Capitulation (NUPL < 1)', zorder=5)

    ax1.legend(loc='upper left')

    # ------------------ BOTTOM PLOT: NUPL Ratio ------------------
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('NUPL Ratio', color='tab:blue', fontsize=12)
    ax2.set_yscale('log')
    ax2.yaxis.set_major_formatter(formatter)
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    # Plot the Ratio
    ax2.plot(df['Date'], df['Combined Ratio'], color='tab:blue', linewidth=1.2, label='NUPL Ratio')
    
    # Add a horizontal line at Ratio = 1.0
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Capitulation Threshold (<1.0)')

    # Fill areas where Ratio < 1.0
    ax2.fill_between(df['Date'], df['Combined Ratio'], 1.0, where=bottom_zones, color='red', alpha=0.3, label='Market Bottom Zone')

    ax2.legend(loc='upper left')

    # Tweak layout
    fig.tight_layout()

    # Save the chart
    plt.savefig('nupl_chart.png', dpi=300, bbox_inches='tight')
    print("Chart saved successfully to nupl_chart.png")

if __name__ == "__main__":
    generate_nupl_chart()
