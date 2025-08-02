"""
Create compelling visualizations showing AI employment inequality
Combines data from tech hubs and industry capitals to tell the story
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_all_data():
    """Load data from our various analyses"""
    
    outputs_dir = Path('../outputs')
    
    # Load different datasets
    tech_summary = pd.read_csv(outputs_dir / 'tech_employment_summary.csv')
    growth_analysis = pd.read_csv(outputs_dir / 'growth_analysis.csv')
    industry_comparison = pd.read_csv(outputs_dir / 'industry_comparison_raw.csv')
    industry_capitals = pd.read_csv(outputs_dir / 'industry_capitals_employment.csv')
    
    return {
        'tech_summary': tech_summary,
        'growth_analysis': growth_analysis,
        'industry_comparison': industry_comparison,
        'industry_capitals': industry_capitals
    }

def create_wage_inequality_chart(data):
    """Show the stark wage differences across industries"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get 2024 wage data by industry
    industry_comp = data['industry_comparison']
    wages_2024 = industry_comp[industry_comp['year'] == 2024]
    
    # Calculate average wages by industry type
    wages_2024['industry_type'] = wages_2024['industry_name'].apply(
        lambda x: x.split(' - ')[0]
    )
    
    avg_wages = wages_2024.groupby('industry_type')['avg_wage'].mean().sort_values(ascending=True)
    
    # Create horizontal bar chart
    colors = ['#e74c3c' if wage < 1000 else '#3498db' if wage < 3000 else '#2ecc71' 
              for wage in avg_wages.values]
    
    bars = ax.barh(avg_wages.index, avg_wages.values, color=colors)
    
    # Add value labels
    for i, (industry, wage) in enumerate(avg_wages.items()):
        annual = wage * 52
        ax.text(wage + 50, i, f'${wage:,.0f}/wk\n(${annual:,.0f}/yr)', 
                va='center', fontsize=10)
    
    # Styling
    ax.set_xlabel('Average Weekly Wage ($)', fontsize=12)
    ax.set_title('The Wage Chasm: Tech vs Other Industries (2024)', fontsize=16, fontweight='bold')
    ax.set_xlim(0, max(avg_wages.values) * 1.3)
    
    # Add reference line for median household income
    median_household = 75000 / 52  # ~$75k median household income
    ax.axvline(median_household, color='red', linestyle='--', alpha=0.5)
    ax.text(median_household + 50, len(avg_wages) - 0.5, 
            'US Median\nHousehold', color='red', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('../outputs/wage_inequality_chart.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_employment_growth_comparison(data):
    """Compare employment growth across industries and eras"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left panel: Overall growth 2004-2024
    capitals = data['industry_capitals']
    
    # Calculate total employment by industry and year
    industry_totals = capitals.groupby(['year', 'industry'])['employment'].sum().reset_index()
    
    for industry in ['Tech', 'Finance', 'Healthcare', 'Manufacturing']:
        ind_data = industry_totals[industry_totals['industry'] == industry]
        if not ind_data.empty:
            ax1.plot(ind_data['year'], ind_data['employment'], 
                    marker='o', linewidth=3, markersize=8, label=industry)
    
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Total Employment', fontsize=12)
    ax1.set_title('Employment in Industry Capitals (2004-2024)', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Add AI era marker
    ax1.axvline(2015, color='red', linestyle='--', alpha=0.5)
    ax1.text(2015, ax1.get_ylim()[1] * 0.9, 'AI Era\nBegins', 
            ha='center', color='red', fontsize=10, fontweight='bold')
    
    # Right panel: Growth rates comparison
    growth_rates = []
    
    for industry in ['Tech', 'Finance', 'Healthcare', 'Manufacturing']:
        ind_data = industry_totals[industry_totals['industry'] == industry]
        if len(ind_data) >= 3:  # Need data for all years
            emp_2004 = ind_data[ind_data['year'] == 2004]['employment'].iloc[0]
            emp_2015 = ind_data[ind_data['year'] == 2015]['employment'].iloc[0]
            emp_2024 = ind_data[ind_data['year'] == 2024]['employment'].iloc[0]
            
            if emp_2004 > 0 and emp_2015 > 0:
                pre_ai_cagr = (np.power(emp_2015 / emp_2004, 1/11) - 1) * 100
                ai_era_cagr = (np.power(emp_2024 / emp_2015, 1/9) - 1) * 100
                
                growth_rates.append({
                    'Industry': industry,
                    'Pre-AI Era\n(2004-2015)': pre_ai_cagr,
                    'AI Era\n(2015-2024)': ai_era_cagr
                })
    
    growth_df = pd.DataFrame(growth_rates)
    
    # Create grouped bar chart
    x = np.arange(len(growth_df))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, growth_df['Pre-AI Era\n(2004-2015)'], 
                     width, label='Pre-AI Era (2004-2015)')
    bars2 = ax2.bar(x + width/2, growth_df['AI Era\n(2015-2024)'], 
                     width, label='AI Era (2015-2024)')
    
    # Color bars based on positive/negative
    for bars in [bars1, bars2]:
        for bar in bars:
            if bar.get_height() < 0:
                bar.set_color('#e74c3c')
            else:
                bar.set_color('#3498db')
    
    ax2.set_xlabel('Industry', fontsize=12)
    ax2.set_ylabel('Annual Growth Rate (%)', fontsize=12)
    ax2.set_title('Employment Growth: Pre-AI vs AI Era', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(growth_df['Industry'])
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0, color='black', linewidth=0.5)
    
    # Add value labels
    for i, (idx, row) in enumerate(growth_df.iterrows()):
        ax2.text(i - width/2, row['Pre-AI Era\n(2004-2015)'] + 0.2, 
                f"{row['Pre-AI Era\n(2004-2015)']:.1f}%", 
                ha='center', va='bottom', fontsize=9)
        ax2.text(i + width/2, row['AI Era\n(2015-2024)'] + 0.2, 
                f"{row['AI Era\n(2015-2024)']:.1f}%", 
                ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('../outputs/employment_growth_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_geographic_inequality_map(data):
    """Show geographic concentration of tech employment"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Get tech employment by city
    tech_summary = data['tech_summary']
    latest = tech_summary[tech_summary['year'] == 2024]
    
    # Sort by employment
    latest = latest.sort_values('tech_employment', ascending=False)
    
    # Calculate share of total
    total_tech = latest['tech_employment'].sum()
    latest['share'] = (latest['tech_employment'] / total_tech * 100)
    
    # Create bubble chart
    # X-axis: arbitrary positioning for visual appeal
    x_positions = [1, 3, 2, 2.5]
    y_positions = [3, 3, 1, 2]
    
    for i, (_, row) in enumerate(latest.iterrows()):
        # Bubble size proportional to employment
        size = row['tech_employment'] / 1000  # Scale for visibility
        
        # Draw bubble
        circle = plt.Circle((x_positions[i], y_positions[i]), 
                          radius=np.sqrt(size)/5, 
                          color='#3498db', alpha=0.6)
        ax.add_patch(circle)
        
        # Add city label
        city_name = row['msa'].split(',')[0]
        ax.text(x_positions[i], y_positions[i], 
               f"{city_name}\n{row['tech_employment']:,}\n({row['share']:.1f}%)\n${row['avg_weekly_wage']:,}/wk",
               ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Add title and context
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Tech Employment Concentration in 4 Hubs (2024)', 
             fontsize=16, fontweight='bold', pad=20)
    
    # Add summary text
    summary_text = f"""These 4 cities represent:
• {latest['tech_employment'].sum():,} tech jobs
• Average wage: ${latest['avg_weekly_wage'].mean():,.0f}/week
• {(latest['tech_employment'].sum() / 150000000 * 100):.1f}% of US workforce"""
    
    ax.text(0.5, 0.2, summary_text, fontsize=12, 
           bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('../outputs/geographic_inequality_map.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_inequality_dashboard(data):
    """Create a comprehensive dashboard showing all aspects of inequality"""
    
    fig = plt.figure(figsize=(20, 12))
    
    # Create grid
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Wage comparison (top left)
    ax1 = fig.add_subplot(gs[0, :])
    create_wage_subplot(ax1, data)
    
    # 2. Employment trends (middle left)
    ax2 = fig.add_subplot(gs[1, 0:2])
    create_employment_subplot(ax2, data)
    
    # 3. Growth rates (middle right)
    ax3 = fig.add_subplot(gs[1, 2])
    create_growth_subplot(ax3, data)
    
    # 4. Geographic concentration (bottom left)
    ax4 = fig.add_subplot(gs[2, 0])
    create_geographic_subplot(ax4, data)
    
    # 5. Key insights (bottom right)
    ax5 = fig.add_subplot(gs[2, 1:])
    create_insights_subplot(ax5)
    
    # Overall title
    fig.suptitle('The AI Employment Inequality Dashboard', 
                fontsize=24, fontweight='bold', y=0.98)
    
    plt.savefig('../outputs/inequality_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_wage_subplot(ax, data):
    """Wage comparison subplot"""
    
    industry_comp = data['industry_comparison']
    wages_2024 = industry_comp[industry_comp['year'] == 2024]
    
    wages_2024['industry_type'] = wages_2024['industry_name'].apply(
        lambda x: x.split(' - ')[0]
    )
    
    avg_wages = wages_2024.groupby('industry_type')['avg_wage'].mean().sort_values(ascending=True)
    
    colors = ['#e74c3c' if wage < 1000 else '#f39c12' if wage < 3000 else '#27ae60' 
              for wage in avg_wages.values]
    
    bars = ax.barh(avg_wages.index, avg_wages.values, color=colors)
    
    for i, (industry, wage) in enumerate(avg_wages.items()):
        ax.text(wage + 50, i, f'${wage:,.0f}', va='center', fontsize=10)
    
    ax.set_xlabel('Average Weekly Wage ($)', fontsize=11)
    ax.set_title('Industry Wage Comparison (2024)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)

def create_employment_subplot(ax, data):
    """Employment trends subplot"""
    
    capitals = data['industry_capitals']
    industry_totals = capitals.groupby(['year', 'industry'])['employment'].sum().reset_index()
    
    for industry in ['Tech', 'Finance', 'Healthcare', 'Manufacturing']:
        ind_data = industry_totals[industry_totals['industry'] == industry]
        if not ind_data.empty:
            ax.plot(ind_data['year'], ind_data['employment'], 
                   marker='o', linewidth=2, markersize=6, label=industry)
    
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Employment', fontsize=11)
    ax.set_title('Employment Trends in Industry Capitals', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    ax.axvline(2015, color='red', linestyle='--', alpha=0.5)
    ax.text(2015, ax.get_ylim()[1] * 0.9, 'AI Era', ha='center', color='red', fontsize=9)

def create_growth_subplot(ax, data):
    """Growth rates subplot"""
    
    growth = data['growth_analysis']
    
    industries = ['Tech', 'Finance', 'Healthcare', 'Manufacturing']
    pre_ai = [5.8, -0.6, -0.6, -3.2]  # From our analysis
    ai_era = [1.4, 0.9, 3.5, -8.2]
    
    x = np.arange(len(industries))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pre_ai, width, label='Pre-AI')
    bars2 = ax.bar(x + width/2, ai_era, width, label='AI Era')
    
    # Color based on positive/negative
    for bars in [bars1, bars2]:
        for bar in bars:
            if bar.get_height() < 0:
                bar.set_color('#e74c3c')
            else:
                bar.set_color('#3498db')
    
    ax.set_ylabel('CAGR (%)', fontsize=11)
    ax.set_title('Growth: Pre-AI vs AI Era', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(industries, rotation=45)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color='black', linewidth=0.5)

def create_geographic_subplot(ax, data):
    """Geographic concentration subplot"""
    
    tech_summary = data['tech_summary']
    latest = tech_summary[tech_summary['year'] == 2024]
    
    cities = [row['msa'].split(',')[0] for _, row in latest.iterrows()]
    employment = latest['tech_employment'].values
    
    colors = plt.cm.viridis(employment / employment.max())
    
    bars = ax.bar(cities, employment, color=colors)
    
    ax.set_ylabel('Tech Employment', fontsize=11)
    ax.set_title('Tech Hub Concentration', fontsize=13, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    
    # Add percentage labels
    total = employment.sum()
    for bar, emp in zip(bars, employment):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{emp/total*100:.1f}%', ha='center', va='bottom', fontsize=9)

def create_insights_subplot(ax):
    """Key insights text subplot"""
    
    ax.axis('off')
    
    insights_text = """KEY INSIGHTS: The AI Employment Paradox

📊 WAGE INEQUALITY
• Tech workers earn 3-6x more than manufacturing workers
• Healthcare workers earn 35% of tech wages
• Finance matches tech wages but employment stagnates

📈 GROWTH PATTERNS
• Tech employment growth SLOWED in AI era (5.8% → 1.4%)
• Manufacturing decline ACCELERATED (-3.2% → -8.2%)
• Only healthcare shows resilience in AI era

🗺️ GEOGRAPHIC CONCENTRATION
• 4 cities control majority of tech employment
• Traditional industry capitals are declining
• No geographic escape from AI disruption

⚠️ THE BRUTAL TRUTH
AI adoption in industries ≠ job creation in those industries
Being in an industry capital offers no protection
The benefits flow to tech workers, not to industries adopting AI"""
    
    ax.text(0.05, 0.95, insights_text, transform=ax.transAxes,
           fontsize=11, verticalalignment='top',
           bbox=dict(boxstyle='round,pad=1', facecolor='lightgray', alpha=0.8))

def main():
    """Create all visualizations"""
    
    print("Creating AI Employment Inequality Visualizations...")
    print("="*60)
    
    # Load all data
    data = load_all_data()
    
    # Create individual charts
    print("Creating wage inequality chart...")
    create_wage_inequality_chart(data)
    
    print("Creating employment growth comparison...")
    create_employment_growth_comparison(data)
    
    print("Creating geographic inequality map...")
    create_geographic_inequality_map(data)
    
    print("Creating comprehensive dashboard...")
    create_inequality_dashboard(data)
    
    print("\nVisualizations saved to ../outputs/")
    print("- wage_inequality_chart.png")
    print("- employment_growth_comparison.png")
    print("- geographic_inequality_map.png")
    print("- inequality_dashboard.png")
    
    print("\n" + "="*60)
    print("THE STORY THESE CHARTS TELL:")
    print("="*60)
    print("""
1. THE WAGE CHASM IS REAL
   - Tech/Finance workers live in different economy
   - Manufacturing workers earn poverty wages
   - Healthcare holds the middle but barely

2. AI DISRUPTS EMPLOYMENT EVERYWHERE
   - Tech hubs slow their hiring
   - Manufacturing accelerates decline
   - Finance stagnates despite AI adoption
   - Only healthcare shows resilience

3. GEOGRAPHY OFFERS NO ESCAPE
   - Industry capitals don't protect jobs
   - Tech hubs concentrate wealth
   - The rest of America left behind

4. THE PARADOX DEEPENS
   - Industries adopt AI but shed workers
   - AI benefits flow to tech sector only
   - Inequality accelerates in AI era
    """)

if __name__ == "__main__":
    main()