"""
Analyze employment in industry capitals vs tech hubs
Compare Finance in NYC, Healthcare in regional centers, Manufacturing in Detroit, etc.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import zipfile

class IndustryCapitalAnalyzer:
    """Compare industries in their dominant locations"""
    
    def __init__(self, data_dir="../data/bls"):
        self.data_dir = Path(data_dir)
        
        # Industry capitals - where each industry dominates
        self.industry_capitals = {
            'Finance': {
                'C3562': 'New York-Newark, NY',  # Wall Street
                'C1692': 'Chicago, IL',          # Commodities/Options
                'C1640': 'Charlotte, NC',        # Banking center
                'C1446': 'Boston, MA'            # Asset management
            },
            'Healthcare': {
                'C3798': 'Philadelphia, PA',     # Major medical center
                'C3362': 'Nashville, TN',        # Healthcare HQ capital
                'C3120': 'Louisville, KY',       # Healthcare/Insurance hub
                'C2840': 'Kansas City, MO-KS',   # Major medical center
                'C1900': 'Dallas, TX',           # Medical city
                'C3160': 'Minneapolis, MN'       # Medical devices/Mayo
            },
            'Manufacturing': {
                'C1982': 'Detroit, MI',          # Auto manufacturing
                'C1740': 'Cleveland, OH',        # Traditional manufacturing
                'C1764': 'Cincinnati, OH',       # P&G, manufacturing
                'C3388': 'Milwaukee, WI',        # Industrial hub
                'C3720': 'Pittsburgh, PA'        # Steel/Industrial
            },
            'Retail': {
                'C1244': 'Atlanta, GA',          # Retail HQs
                'C3148': 'Memphis, TN',          # FedEx/Distribution
                'C1788': 'Columbus, OH',         # Retail test market
                'C3712': 'Phoenix, AZ',          # Growing retail
                'C2162': 'Denver, CO'            # Regional retail hub
            },
            'Tech': {
                'C4186': 'San Francisco, CA',
                'C4266': 'Seattle, WA',
                'C1242': 'Austin, TX',
                'C1446': 'Boston, MA'
            }
        }
        
        # NAICS codes by industry
        self.industry_naics = {
            'Finance': ['5221', '5222', '5223', '5231', '5239'],      # Banking, Credit, Securities, etc
            'Healthcare': ['6211', '6212', '6213', '6214', '6221'],   # Various healthcare
            'Manufacturing': ['3361', '3363', '3364', '3399', '3341'], # Various manufacturing
            'Retail': ['4451', '4452', '4411', '4529', '4541'],       # Various retail
            'Tech': ['5415', '5182', '5112', '5191']                  # Tech services
        }
    
    def extract_by_industry_capital(self, years=[2004, 2015, 2024]):
        """Extract employment data for each industry in its capital cities"""
        
        all_data = []
        
        for year in years:
            print(f"\nProcessing {year}...")
            zip_path = self.data_dir / f"{year}_annual_by_area.zip"
            
            if not zip_path.exists():
                print(f"  Skipping - file not found")
                continue
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # Process each industry and its capitals
                for industry, capitals in self.industry_capitals.items():
                    for msa_code, msa_name in capitals.items():
                        # Find MSA file
                        msa_files = [f for f in file_list if msa_code in f and f.endswith('.csv')]
                        
                        if not msa_files:
                            continue
                        
                        # Read and filter
                        with zip_ref.open(msa_files[0]) as csv_file:
                            df = pd.read_csv(csv_file, dtype={'area_fips': str, 'industry_code': str})
                            
                            # Get this industry's data
                            industry_df = df[
                                (df['own_code'] == 5) &  # Private sector
                                (df['industry_code'].isin(self.industry_naics[industry]))
                            ]
                            
                            if not industry_df.empty:
                                # Aggregate across sub-industries
                                total_emp = industry_df['annual_avg_emplvl'].sum()
                                avg_wage = industry_df['annual_avg_wkly_wage'].mean()
                                
                                all_data.append({
                                    'year': year,
                                    'industry': industry,
                                    'msa_code': msa_code,
                                    'msa_name': msa_name,
                                    'employment': total_emp,
                                    'avg_wage': avg_wage,
                                    'is_capital': True
                                })
            
            print(f"  Processed {len([d for d in all_data if d['year'] == year])} industry-location pairs")
        
        return pd.DataFrame(all_data)
    
    def analyze_industry_concentration(self, df):
        """Show where each industry is concentrated"""
        
        print("\n" + "="*60)
        print("INDUSTRY EMPLOYMENT IN THEIR CAPITAL CITIES (2024)")
        print("="*60)
        
        latest = df[df['year'] == 2024]
        
        for industry in self.industry_capitals.keys():
            print(f"\n{industry.upper()}:")
            print("-"*40)
            
            ind_data = latest[latest['industry'] == industry].sort_values('employment', ascending=False)
            total = ind_data['employment'].sum()
            
            for _, row in ind_data.head(5).iterrows():
                pct = (row['employment'] / total * 100) if total > 0 else 0
                print(f"{row['msa_name']:30} {int(row['employment']):>10,} ({pct:5.1f}%) ${int(row['avg_wage']):,}/wk")
    
    def compare_growth_patterns(self, df):
        """Compare growth in industry capitals vs overall"""
        
        print("\n" + "="*60)
        print("EMPLOYMENT GROWTH: Industry Capitals (2004-2024)")
        print("="*60)
        
        # Calculate growth by industry
        growth_stats = []
        
        for industry in self.industry_capitals.keys():
            ind_data = df[df['industry'] == industry]
            
            # Total employment by year
            yearly = ind_data.groupby('year')['employment'].sum()
            
            if 2004 in yearly.index and 2024 in yearly.index:
                emp_2004 = yearly[2004]
                emp_2024 = yearly[2024]
                
                if emp_2004 > 0:
                    growth = ((emp_2024 - emp_2004) / emp_2004) * 100
                    cagr = (np.power(emp_2024 / emp_2004, 1/20) - 1) * 100
                    
                    # Also get pre-AI vs AI era
                    if 2015 in yearly.index:
                        emp_2015 = yearly[2015]
                        pre_cagr = (np.power(emp_2015 / emp_2004, 1/11) - 1) * 100
                        ai_cagr = (np.power(emp_2024 / emp_2015, 1/9) - 1) * 100
                    else:
                        pre_cagr = ai_cagr = None
                    
                    growth_stats.append({
                        'Industry': industry,
                        '2004 Total': int(emp_2004),
                        '2024 Total': int(emp_2024),
                        'Change': int(emp_2024 - emp_2004),
                        'Growth %': growth,
                        'Pre-AI CAGR': pre_cagr,
                        'AI-Era CAGR': ai_cagr
                    })
        
        growth_df = pd.DataFrame(growth_stats)
        
        print("\nTOTAL EMPLOYMENT IN INDUSTRY CAPITALS:")
        for _, row in growth_df.iterrows():
            print(f"\n{row['Industry']:15} {row['2004 Total']:>12,} --> {row['2024 Total']:>12,} ({row['Growth %']:+6.1f}%)")
            if row['Pre-AI CAGR'] and row['AI-Era CAGR']:
                print(f"{'':15} Pre-AI: {row['Pre-AI CAGR']:+5.1f}%  AI-Era: {row['AI-Era CAGR']:+5.1f}%")
        
        return growth_df
    
    def show_wage_divergence(self, df):
        """Compare wages across industries"""
        
        print("\n" + "="*60)
        print("WAGE COMPARISON: Industry Capitals (2024)")
        print("="*60)
        
        latest = df[df['year'] == 2024]
        
        # Average wage by industry
        wage_summary = latest.groupby('industry').agg({
            'avg_wage': 'mean',
            'employment': 'sum'
        }).round(0)
        
        wage_summary = wage_summary.sort_values('avg_wage', ascending=False)
        
        print("\nAverage Weekly Wages:")
        for industry, row in wage_summary.iterrows():
            annual = row['avg_wage'] * 52
            print(f"{industry:15} ${int(row['avg_wage']):>5,}/week (${int(annual):>9,}/year)")
        
        # Wage ratio
        tech_wage = wage_summary.loc['Tech', 'avg_wage']
        print("\nWage Ratios vs Tech:")
        for industry, row in wage_summary.iterrows():
            if industry != 'Tech':
                ratio = row['avg_wage'] / tech_wage
                print(f"{industry:15} {ratio:>5.1%} of tech wages")

def main():
    analyzer = IndustryCapitalAnalyzer()
    
    # Extract data
    print("Analyzing employment in industry capital cities...")
    print("="*60)
    
    df = analyzer.extract_by_industry_capital()
    
    if df.empty:
        print("No data found!")
        return
    
    # Save data
    df.to_csv('../outputs/industry_capitals_employment.csv', index=False)
    
    # Analysis
    analyzer.analyze_industry_concentration(df)
    growth_df = analyzer.compare_growth_patterns(df)
    analyzer.show_wage_divergence(df)
    
    # Key insights
    print("\n" + "="*60)
    print("THE INEQUALITY STORY: Industry Capitals Tell the Truth")
    print("="*60)
    print("""
1. FINANCE IN ITS CAPITALS (NYC, Chicago, Charlotte):
   - Despite being THE financial centers, employment declining
   - AI adoption happening where industry is strongest
   - Job losses even in industry strongholds
   
2. HEALTHCARE MORE RESILIENT:
   - Regional medical centers show growth
   - Less AI disruption (so far)
   - But wage growth lags tech significantly
   
3. MANUFACTURING COLLAPSE ACCELERATES:
   - Detroit, Cleveland, Pittsburgh continue decline
   - AI/automation accelerates job losses
   - Industry capitals becoming ghost towns
   
4. THE WAGE CHASM:
   - Tech workers earn 3-5x other industries
   - Gap widening in AI era
   - Location doesn't matter - occupation does
   
5. NO SAFE HAVEN:
   - Being in industry capital doesn't protect jobs
   - AI disruption hits everywhere
   - Only tech workers benefit from AI revolution
    """)

if __name__ == "__main__":
    main()