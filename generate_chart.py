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
    # When ratio is > 1 (+ve), the +ve column has the value and -ve is 1.0
    # When ratio is < 1 (-ve), the -ve column has the value and +ve is 1.0
    df['Combined Ratio'] = np.where(
        df['Unrealised Profit/Loss Ratio (+ve)'] != 1.0, 
        df['Unrealised Profit/Loss Ratio (+ve)'], 
        df['Unrealised Profit/Loss Ratio (-ve)']
    )

    # Filter to view from 2011 onwards to avoid early noisy data
    df = df[df['Date'].dt.year >= 2011]

    # Create figure and axis objects with subplots
    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot Bitcoin Price on logarithmic scale (ax1)
    color1 = 'tab:gray'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('BTC Price (USD)', color=color1)
    ax1.plot(df['Date'], df['Price'], color=color1, linewidth=1.5, label='BTC Price')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_yscale('log')

    # Create a second y-axis for the Unrealised Profit/Loss Ratio
    ax2 = ax1.twinx()  
    color2 = 'tab:blue'
    ax2.set_ylabel('Unrealised Profit/Loss Ratio', color=color2)
    ax2.plot(df['Date'], df['Combined Ratio'], color=color2, linewidth=1.2, label='UP/UL Ratio')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_yscale('log')
    
    # Add a horizontal line at Ratio = 1.0
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='Capitulation Threshold (<1.0)')

    # Fill areas where Ratio < 1.0 (Predictable Market Bottoms)
    bottom_zones = df['Combined Ratio'] < 1.0
    ax2.fill_between(df['Date'], df['Combined Ratio'], 1.0, where=bottom_zones, color='red', alpha=0.3, label='Market Bottom Zone')

    # Title and grid
    plt.title('Bitcoin: Unrealised Profit/Loss Ratio vs Price (Real On-Chain Data)', fontsize=16, pad=20)
    fig.tight_layout()
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # Combine legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

    # Save the chart
    plt.savefig('nupl_chart.png', dpi=300, bbox_inches='tight')
    print("Chart saved successfully to nupl_chart.png")

if __name__ == "__main__":
    generate_nupl_chart()
