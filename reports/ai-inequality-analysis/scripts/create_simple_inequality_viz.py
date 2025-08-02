"""
Create focused visualizations showing AI employment inequality
Simpler version focusing on key story elements
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('default')
sns.set_palette("husl")

def create_wage_inequality_chart():
    """Show wage differences across industries"""
    
    # Data from our analysis
    industries = ['Manufacturing', 'Healthcare', 'Tech', 'Finance']
    wages = [697, 1552, 4375, 4474]  # Weekly wages from industry capitals analysis
    annual_wages = [w * 52 for w in wages]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create horizontal bar chart
    colors = ['#e74c3c', '#f39c12', '#27ae60', '#3498db']
    bars = ax.barh(industries, wages, color=colors)
    
    # Add value labels
    for i, (wage, annual) in enumerate(zip(wages, annual_wages)):
        ax.text(wage + 100, i, f'${wage:,}/wk\n(${annual:,}/yr)', 
                va='center', fontsize=10)
    
    # Add median household income line
    median_household = 75000 / 52
    ax.axvline(median_household, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax.text(median_household + 50, 3.5, 'US Median\nHousehold', 
            color='red', fontsize=9, fontweight='bold')
    
    # Styling
    ax.set_xlabel('Average Weekly Wage ($)', fontsize=12)
    ax.set_title('The Wage Chasm: Industry Capital Cities (2024)', 
                fontsize=16, fontweight='bold')
    ax.set_xlim(0, 5000)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add ratio annotations
    tech_wage = wages[2]
    for i, (industry, wage) in enumerate(zip(industries, wages)):
        if industry != 'Tech':
            ratio = wage / tech_wage
            ax.text(50, i, f'{ratio:.0%} of tech', 
                   fontsize=9, color='gray', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../outputs/wage_inequality_simple.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created wage inequality chart")

def create_employment_growth_chart():
    """Show employment growth comparison"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Data from industry capitals analysis
    industries = ['Tech', 'Healthcare', 'Finance', 'Manufacturing']
    growth_2004_2024 = [110.9, 27.3, 1.6, -67.7]  # Percentage growth
    pre_ai_cagr = [5.8, -0.6, -0.6, -3.2]
    ai_era_cagr = [1.4, 3.5, 0.9, -8.2]
    
    x = np.arange(len(industries))
    width = 0.35
    
    # Create grouped bars for CAGRs
    bars1 = ax.bar(x - width/2, pre_ai_cagr, width, label='Pre-AI Era (2004-2015)')
    bars2 = ax.bar(x + width/2, ai_era_cagr, width, label='AI Era (2015-2024)')
    
    # Color based on positive/negative
    for bars in [bars1, bars2]:
        for bar in bars:
            if bar.get_height() < 0:
                bar.set_color('#e74c3c')
            else:
                bar.set_color('#3498db')
    
    # Add value labels
    for i in range(len(industries)):
        # Pre-AI label
        val = pre_ai_cagr[i]
        y = val + 0.3 if val > 0 else val - 0.5
        ax.text(i - width/2, y, f'{val:.1f}%', ha='center', fontsize=9)
        
        # AI-era label
        val = ai_era_cagr[i]
        y = val + 0.3 if val > 0 else val - 0.5
        ax.text(i + width/2, y, f'{val:.1f}%', ha='center', fontsize=9)
    
    # Styling
    ax.set_ylabel('Annual Growth Rate (CAGR %)', fontsize=12)
    ax.set_title('Employment Growth in Industry Capitals: Pre-AI vs AI Era', 
                fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(industries)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(0, color='black', linewidth=1)
    ax.set_ylim(-10, 8)
    
    # Add annotations
    ax.text(0.02, 0.98, 'Tech growth SLOWED in AI era', 
           transform=ax.transAxes, fontsize=10, 
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
           verticalalignment='top')
    
    ax.text(0.98, 0.02, 'Manufacturing decline ACCELERATED', 
           transform=ax.transAxes, fontsize=10, 
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffcccc', alpha=0.7),
           verticalalignment='bottom', horizontalalignment='right')
    
    plt.tight_layout()
    plt.savefig('../outputs/employment_growth_simple.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created employment growth chart")

def create_tech_concentration_chart():
    """Show geographic concentration of tech employment"""
    
    # Load tech employment data
    tech_summary = pd.read_csv('../outputs/tech_employment_summary.csv')
    latest = tech_summary[tech_summary['year'] == 2024]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Employment by city
    cities = [row['msa'].split(',')[0] for _, row in latest.iterrows()]
    employment = latest['tech_employment'].values
    wages = latest['avg_weekly_wage'].values
    
    # Sort by employment
    sorted_idx = np.argsort(employment)[::-1]
    cities = [cities[i] for i in sorted_idx]
    employment = employment[sorted_idx]
    wages = wages[sorted_idx]
    
    bars = ax1.bar(cities, employment, color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'])
    
    # Add percentage labels
    total = employment.sum()
    for bar, emp in zip(bars, employment):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{emp:,}\n({emp/total*100:.1f}%)', 
                ha='center', va='bottom', fontsize=9)
    
    ax1.set_ylabel('Tech Employment', fontsize=12)
    ax1.set_title('Tech Employment Concentration (2024)', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Right: Wages by city
    bars2 = ax2.bar(cities, wages, color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c'])
    
    for bar, wage in zip(bars2, wages):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${wage:,}', ha='center', va='bottom', fontsize=9)
    
    ax2.set_ylabel('Average Weekly Wage ($)', fontsize=12)
    ax2.set_title('Tech Wages by City (2024)', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Overall title
    fig.suptitle('Geographic Concentration of Tech Wealth', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../outputs/tech_concentration_simple.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created tech concentration chart")

def create_inequality_summary():
    """Create a summary visualization of key inequality metrics"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Wage ratios (top left)
    industries = ['Manufacturing', 'Healthcare', 'Finance', 'Tech']
    ratios = [0.16, 0.35, 1.02, 1.0]  # Relative to tech
    colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    
    bars = ax1.bar(industries, ratios, color=colors)
    ax1.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Wage Ratio (Tech = 1.0)', fontsize=11)
    ax1.set_title('Wages Relative to Tech Industry', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 1.2)
    
    for bar, ratio in zip(bars, ratios):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{ratio:.0%}', ha='center', va='bottom', fontsize=10)
    
    # 2. Employment change (top right)
    employment_change = [110.9, 27.3, 1.6, -67.7]
    colors2 = ['#2ecc71' if x > 0 else '#e74c3c' for x in employment_change]
    
    bars2 = ax2.bar(industries, employment_change, color=colors2)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_ylabel('Employment Change (%)', fontsize=11)
    ax2.set_title('20-Year Employment Change (2004-2024)', fontsize=12, fontweight='bold')
    
    for bar, change in zip(bars2, employment_change):
        y = change + 5 if change > 0 else change - 5
        ax2.text(bar.get_x() + bar.get_width()/2., y,
                f'{change:+.1f}%', ha='center', va='center', fontsize=10)
    
    # 3. AI era impact (bottom left)
    pre_ai = [5.8, -0.6, -0.6, -3.2]
    ai_era = [1.4, 3.5, 0.9, -8.2]
    change = [ai - pre for ai, pre in zip(ai_era, pre_ai)]
    
    colors3 = ['#e74c3c' if x < 0 else '#2ecc71' for x in change]
    bars3 = ax3.bar(industries, change, color=colors3)
    ax3.axhline(0, color='black', linewidth=1)
    ax3.set_ylabel('Change in Growth Rate (pp)', fontsize=11)
    ax3.set_title('AI Era Impact on Growth (AI Era - Pre-AI)', fontsize=12, fontweight='bold')
    
    for bar, ch in zip(bars3, change):
        y = ch + 0.3 if ch > 0 else ch - 0.3
        ax3.text(bar.get_x() + bar.get_width()/2., y,
                f'{ch:+.1f}pp', ha='center', va='center', fontsize=10)
    
    # 4. Key insights (bottom right)
    ax4.axis('off')
    insights = """KEY FINDINGS:

• Tech wages are 6x manufacturing wages

• Manufacturing lost 68% of jobs while
  tech gained 111%

• AI era SLOWED tech hiring but
  ACCELERATED manufacturing decline

• Only healthcare shows resilience

• Finance matches tech wages but
  employment barely grew (1.6%)

THE PARADOX:
Industries adopt AI but shed workers.
Benefits flow to tech sector only."""
    
    ax4.text(0.05, 0.95, insights, transform=ax4.transAxes,
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=1', facecolor='lightgray', alpha=0.3))
    
    # Overall title
    fig.suptitle('AI Employment Inequality: The Complete Picture', 
                fontsize=18, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../outputs/inequality_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Created inequality summary")

def main():
    print("Creating AI Employment Inequality Visualizations...")
    print("="*60)
    
    # Create individual focused charts
    create_wage_inequality_chart()
    create_employment_growth_chart()
    create_tech_concentration_chart()
    create_inequality_summary()
    
    print("\nAll visualizations created successfully!")
    print("\nFiles saved:")
    print("- wage_inequality_simple.png")
    print("- employment_growth_simple.png")
    print("- tech_concentration_simple.png")
    print("- inequality_summary.png")

if __name__ == "__main__":
    main()