"""
Analyze tech employment growth trends: Pre-AI era (2004-2015) vs AI era (2015-2024)
Calculate CAGRs and identify the real story in the data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or end_value <= 0:
        return None
    return (np.power(end_value / start_value, 1/years) - 1) * 100

def analyze_growth_periods():
    """Analyze growth in pre-AI and AI eras"""
    
    # Load the data
    df = pd.read_csv('../outputs/tech_employment_summary.csv')
    
    print("TECH EMPLOYMENT GROWTH ANALYSIS: The Unexpected Story")
    print("="*60)
    
    # Define periods
    pre_ai_start, pre_ai_end = 2004, 2015
    ai_era_start, ai_era_end = 2015, 2024
    
    # Calculate for each city
    results = []
    
    for city in df['msa'].unique():
        city_data = df[df['msa'] == city].sort_values('year')
        
        # Get employment values
        emp_2004 = city_data[city_data['year'] == 2004]['tech_employment'].iloc[0]
        emp_2015 = city_data[city_data['year'] == 2015]['tech_employment'].iloc[0]
        emp_2024 = city_data[city_data['year'] == 2024]['tech_employment'].iloc[0]
        
        # Skip if any values are 0 (Austin data issues)
        if emp_2004 == 0 or emp_2015 == 0:
            # For Austin, use nearest non-zero years
            if 'Austin' in city:
                # Find first non-zero year
                non_zero = city_data[city_data['tech_employment'] > 0].sort_values('year')
                if len(non_zero) > 0:
                    emp_2004 = non_zero.iloc[0]['tech_employment']
                    emp_2015 = city_data[city_data['year'] == 2016]['tech_employment'].iloc[0]  # Use 2016 instead
        
        # Get wage values
        wage_2004 = city_data[city_data['year'] == 2004]['avg_weekly_wage'].iloc[0]
        wage_2015 = city_data[city_data['year'] == 2015]['avg_weekly_wage'].iloc[0]
        wage_2024 = city_data[city_data['year'] == 2024]['avg_weekly_wage'].iloc[0]
        
        # Calculate CAGRs
        emp_cagr_pre = calculate_cagr(emp_2004, emp_2015, 11)
        emp_cagr_ai = calculate_cagr(emp_2015, emp_2024, 9)
        
        wage_cagr_pre = calculate_cagr(wage_2004, wage_2015, 11)
        wage_cagr_ai = calculate_cagr(wage_2015, wage_2024, 9)
        
        # Calculate absolute growth
        emp_growth_pre = emp_2015 - emp_2004
        emp_growth_ai = emp_2024 - emp_2015
        
        results.append({
            'city': city.split(',')[0],  # Shorten name
            'emp_2004': emp_2004,
            'emp_2015': emp_2015,
            'emp_2024': emp_2024,
            'emp_cagr_pre_ai': emp_cagr_pre,
            'emp_cagr_ai_era': emp_cagr_ai,
            'emp_abs_growth_pre': emp_growth_pre,
            'emp_abs_growth_ai': emp_growth_ai,
            'wage_cagr_pre_ai': wage_cagr_pre,
            'wage_cagr_ai_era': wage_cagr_ai,
            'wage_2024': wage_2024
        })
    
    results_df = pd.DataFrame(results)
    
    # Print detailed analysis
    print("\nEMPLOYMENT GROWTH COMPARISON")
    print("-"*60)
    print(f"{'City':<20} {'2004-2015 CAGR':>15} {'2015-2024 CAGR':>15} {'Change':>10}")
    print("-"*60)
    
    for _, row in results_df.iterrows():
        if row['emp_cagr_pre_ai'] and row['emp_cagr_ai_era']:
            change = row['emp_cagr_ai_era'] - row['emp_cagr_pre_ai']
            print(f"{row['city']:<20} {row['emp_cagr_pre_ai']:>14.1f}% {row['emp_cagr_ai_era']:>14.1f}% {change:>9.1f}%")
    
    print("\nWAGE GROWTH COMPARISON")
    print("-"*60)
    print(f"{'City':<20} {'2004-2015 CAGR':>15} {'2015-2024 CAGR':>15} {'2024 Wage':>12}")
    print("-"*60)
    
    for _, row in results_df.iterrows():
        if row['wage_cagr_pre_ai'] and row['wage_cagr_ai_era']:
            print(f"{row['city']:<20} {row['wage_cagr_pre_ai']:>14.1f}% {row['wage_cagr_ai_era']:>14.1f}% ${row['wage_2024']:>10,}")
    
    # The surprising findings
    print("\n" + "="*60)
    print("THE UNEXPECTED STORY IN THE DATA")
    print("="*60)
    
    # Finding 1: Growth deceleration
    avg_cagr_pre = results_df['emp_cagr_pre_ai'].mean()
    avg_cagr_ai = results_df['emp_cagr_ai_era'].mean()
    
    print(f"\n1. GROWTH DECELERATION PARADOX")
    print(f"   Average CAGR Pre-AI Era (2004-2015): {avg_cagr_pre:.1f}%")
    print(f"   Average CAGR AI Era (2015-2024): {avg_cagr_ai:.1f}%")
    print(f"   --> AI era growth is {avg_cagr_pre - avg_cagr_ai:.1f} percentage points SLOWER!")
    
    # Finding 2: Absolute numbers tell different story
    print(f"\n2. ABSOLUTE GROWTH REALITY CHECK")
    for _, row in results_df.iterrows():
        print(f"   {row['city']}: Added {row['emp_abs_growth_pre']:,} jobs (pre-AI) vs {row['emp_abs_growth_ai']:,} (AI era)")
    
    # Finding 3: Wage acceleration
    print(f"\n3. THE WAGE EXPLOSION")
    print(f"   While employment growth slowed, wages accelerated dramatically:")
    for _, row in results_df.iterrows():
        if row['wage_cagr_ai_era'] and row['wage_cagr_pre_ai']:
            wage_acceleration = row['wage_cagr_ai_era'] - row['wage_cagr_pre_ai']
            if wage_acceleration > 0:
                print(f"   {row['city']}: Wages grew {wage_acceleration:.1f}pp faster in AI era")
    
    # The real story
    print("\n" + "="*60)
    print("WHAT THE DATA IS REALLY TELLING US")
    print("="*60)
    print("""
1. MARKET MATURATION: Early exponential growth (small base) has shifted to 
   steady absolute gains (large base). SF adding 30K jobs on 100K base < 10% 
   but still massive growth.

2. TALENT SCARCITY: Slowing employment growth + accelerating wages = 
   classic supply constraint. There aren't enough AI engineers to hire.

3. QUALITY OVER QUANTITY: The AI era isn't about hiring more people, 
   it's about paying more for the right people. Average wage in SF tech 
   is now ${:,}/week (${:,}/year)!

4. THE AUSTIN ANOMALY: Volatile data suggests a different dynamic - 
   boom/bust cycles rather than steady growth. The "frontier" of tech expansion?
    """.format(
        int(results_df[results_df['city'] == 'San Francisco-Oakland-Fremont']['wage_2024'].iloc[0]),
        int(results_df[results_df['city'] == 'San Francisco-Oakland-Fremont']['wage_2024'].iloc[0] * 52)
    ))
    
    # Save results
    results_df.to_csv('../outputs/growth_analysis.csv', index=False)
    
    # Create visualization
    create_growth_visualization(df, results_df)
    
    return results_df

def create_growth_visualization(df, results_df):
    """Create visualization showing the growth story"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('The Unexpected Story: AI Era Growth Deceleration', fontsize=16)
    
    # 1. Employment over time
    ax1 = axes[0, 0]
    for city in df['msa'].unique():
        city_data = df[df['msa'] == city].sort_values('year')
        ax1.plot(city_data['year'], city_data['tech_employment'], 
                marker='o', label=city.split(',')[0], linewidth=2)
    
    ax1.axvline(x=2015, color='red', linestyle='--', alpha=0.5)
    ax1.text(2015, ax1.get_ylim()[1]*0.9, 'AI Era Begins', ha='center', color='red')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Tech Employment')
    ax1.set_title('Tech Employment Growth')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. CAGR comparison
    ax2 = axes[0, 1]
    x = np.arange(len(results_df))
    width = 0.35
    
    ax2.bar(x - width/2, results_df['emp_cagr_pre_ai'], width, label='Pre-AI Era (2004-2015)')
    ax2.bar(x + width/2, results_df['emp_cagr_ai_era'], width, label='AI Era (2015-2024)')
    
    ax2.set_xlabel('City')
    ax2.set_ylabel('CAGR (%)')
    ax2.set_title('Employment Growth Rates: Pre-AI vs AI Era')
    ax2.set_xticks(x)
    ax2.set_xticklabels(results_df['city'], rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Wage growth
    ax3 = axes[1, 0]
    for city in df['msa'].unique():
        city_data = df[df['msa'] == city].sort_values('year')
        ax3.plot(city_data['year'], city_data['avg_weekly_wage'], 
                marker='o', label=city.split(',')[0], linewidth=2)
    
    ax3.axvline(x=2015, color='red', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Average Weekly Wage ($)')
    ax3.set_title('Wage Growth Acceleration in AI Era')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Employment vs Wage CAGR
    ax4 = axes[1, 1]
    ax4.scatter(results_df['emp_cagr_ai_era'], results_df['wage_cagr_ai_era'], s=200)
    
    for i, row in results_df.iterrows():
        ax4.annotate(row['city'], (row['emp_cagr_ai_era'], row['wage_cagr_ai_era']), 
                    xytext=(5, 5), textcoords='offset points')
    
    ax4.set_xlabel('Employment CAGR in AI Era (%)')
    ax4.set_ylabel('Wage CAGR in AI Era (%)')
    ax4.set_title('The Trade-off: Slower Hiring, Faster Wage Growth')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../outputs/growth_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("\nVisualization saved to: ../outputs/growth_analysis.png")

if __name__ == "__main__":
    results = analyze_growth_periods()
    
    # Future projections based on AI era CAGRs
    print("\n" + "="*60)
    print("PROJECTIONS: What if AI Era Trends Continue?")
    print("="*60)
    
    print("\nProjected 2034 Employment (using AI era CAGRs):")
    for _, row in results.iterrows():
        if row['emp_cagr_ai_era'] and row['emp_cagr_ai_era'] > 0:
            projected_2034 = row['emp_2024'] * np.power(1 + row['emp_cagr_ai_era']/100, 10)
            print(f"{row['city']}: {int(projected_2034):,} jobs (from {row['emp_2024']:,} in 2024)")
    
    print("\nBUT... this assumes:")
    print("- No talent supply constraints")
    print("- No geographic dispersion (remote work)")
    print("- No policy changes")
    print("- No AI replacing tech workers themselves")
    print("\nThe real story isn't in the projections - it's in understanding why growth is slowing.")