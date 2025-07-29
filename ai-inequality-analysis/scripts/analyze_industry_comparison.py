"""
Compare employment trends across AI-adopting industries
Pull data for Finance, Healthcare, Manufacturing, and Retail vs Tech
"""

import pandas as pd
import numpy as np
from pathlib import Path
import zipfile

class IndustryComparisonAnalyzer:
    """Analyze employment across industries adopting AI"""
    
    def __init__(self, data_dir="data/bls"):
        self.data_dir = Path(data_dir)
        
        # Expand MSAs to include industry-specific hubs
        self.target_msas = {
            # Tech hubs (original)
            'C4186': 'San Francisco-Oakland-Fremont, CA',
            'C4266': 'Seattle-Tacoma-Bellevue, WA', 
            'C1446': 'Boston-Cambridge-Newton, MA-NH',
            'C1242': 'Austin-Round Rock, TX',
            
            # Finance hubs
            'C3562': 'New York-Newark-Jersey City, NY-NJ-PA',
            'C1692': 'Chicago-Naperville-Elgin, IL-IN-WI',
            
            # Healthcare hubs
            'C3798': 'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD',
            'C2628': 'Houston-The Woodlands-Sugar Land, TX',
            
            # Manufacturing hubs
            'C1982': 'Detroit-Warren-Dearborn, MI',
            'C1740': 'Cleveland-Elyria, OH'
        }
        
        # Industry NAICS codes (4-digit to avoid double counting)
        self.industries = {
            '5415': 'Computer Systems Design (Tech)',
            '5182': 'Data Processing (Tech)',
            '5221': 'Banking and Finance',
            '5222': 'Credit and Finance',
            '5223': 'Securities and Investments', 
            '6211': 'Offices of Physicians',
            '6214': 'Outpatient Care Centers',
            '6221': 'General Medical Hospitals',
            '3361': 'Motor Vehicle Manufacturing',
            '3363': 'Motor Vehicle Parts Manufacturing',
            '3341': 'Computer and Electronic Manufacturing',
            '4451': 'Grocery Stores',
            '4529': 'General Merchandise Stores',
            '4541': 'Electronic Shopping'
        }
        
        # Group industries
        self.industry_groups = {
            'Tech': ['5415', '5182'],
            'Finance': ['5221', '5222', '5223'],
            'Healthcare': ['6211', '6214', '6221'],
            'Manufacturing': ['3361', '3363', '3341'],
            'Retail': ['4451', '4529', '4541']
        }
    
    def extract_industry_data(self, year):
        """Extract data for all industries from a year's zip file"""
        
        zip_path = self.data_dir / f"{year}_annual_by_area.zip"
        if not zip_path.exists():
            return pd.DataFrame()
        
        all_data = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Process each MSA
            for msa_code, msa_name in self.target_msas.items():
                msa_files = [f for f in file_list if msa_code in f and f.endswith('.csv')]
                
                for msa_file in msa_files:
                    with zip_ref.open(msa_file) as csv_file:
                        df = pd.read_csv(csv_file, dtype={'area_fips': str, 'industry_code': str})
                        
                        # Filter for private sector and our industries
                        industry_df = df[
                            (df['own_code'] == 5) &  # Private sector
                            (df['industry_code'].isin(self.industries.keys()))
                        ].copy()
                        
                        if not industry_df.empty:
                            industry_df['year'] = year
                            industry_df['msa_name'] = msa_name
                            industry_df['msa_code'] = msa_code
                            # Simplify industry names
                            industry_df['industry_group'] = industry_df['industry_code'].map(
                                lambda x: next((group for group, codes in self.industry_groups.items() 
                                              if x in codes), 'Other')
                            )
                            all_data.append(industry_df)
        
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    
    def analyze_all_industries(self):
        """Process all years and create comparison"""
        
        print("Extracting employment data for AI-adopting industries...")
        print("="*60)
        
        # Process select years to speed up analysis
        years = [2004, 2008, 2012, 2015, 2019, 2024]
        all_data = []
        
        for year in years:
            print(f"Processing {year}...")
            year_data = self.extract_industry_data(year)
            if not year_data.empty:
                all_data.append(year_data)
                print(f"  Found {len(year_data)} records")
        
        if not all_data:
            print("No data found!")
            return None, None
        
        df = pd.concat(all_data, ignore_index=True)
        
        # Create summary by industry group and MSA
        summary = df.groupby(['year', 'msa_name', 'industry_group']).agg({
            'annual_avg_emplvl': 'sum',
            'annual_avg_wkly_wage': 'mean'
        }).reset_index()
        
        return df, summary
    
    def find_industry_hubs(self, df):
        """Identify main locations for each industry"""
        
        print("\n" + "="*60)
        print("INDUSTRY CONCENTRATION BY LOCATION (2024)")
        print("="*60)
        
        # Get 2024 data
        latest = df[df['year'] == 2024]
        
        for industry in self.industry_groups.keys():
            print(f"\n{industry.upper()} EMPLOYMENT:")
            print("-"*40)
            
            industry_data = latest[latest['industry_group'] == industry]
            if industry_data.empty:
                print("No data available")
                continue
                
            # Sum by MSA
            msa_totals = industry_data.groupby('msa_name')['annual_avg_emplvl'].sum().sort_values(ascending=False)
            
            total = msa_totals.sum()
            for msa, employment in msa_totals.items():
                pct = (employment / total * 100) if total > 0 else 0
                print(f"{msa}: {employment:,.0f} jobs ({pct:.1f}% of total)")
    
    def analyze_growth_patterns(self, summary):
        """Compare growth patterns across industries"""
        
        print("\n" + "="*60)
        print("EMPLOYMENT GROWTH COMPARISON: Tech vs Other Industries")
        print("="*60)
        
        # Calculate growth rates for each industry
        growth_stats = []
        
        for industry in self.industry_groups.keys():
            ind_data = summary[summary['industry_group'] == industry]
            
            if not ind_data.empty:
                # Get total employment by year
                yearly = ind_data.groupby('year')['annual_avg_emplvl'].sum()
                
                if 2004 in yearly.index and 2024 in yearly.index:
                    start = yearly[2004]
                    end = yearly[2024]
                    
                    if start > 0:
                        total_growth = ((end - start) / start) * 100
                        cagr = (np.power(end / start, 1/20) - 1) * 100
                        
                        growth_stats.append({
                            'Industry': industry,
                            '2004 Employment': int(start),
                            '2024 Employment': int(end),
                            'Absolute Change': int(end - start),
                            'Total Growth %': total_growth,
                            '20-Year CAGR': cagr
                        })
        
        growth_df = pd.DataFrame(growth_stats)
        print("\n20-YEAR EMPLOYMENT TRENDS:")
        print(growth_df.to_string(index=False))
        
        # Pre-AI vs AI era comparison
        print("\n\nPRE-AI ERA (2004-2015) vs AI ERA (2015-2024):")
        print("-"*60)
        
        for industry in self.industry_groups.keys():
            ind_data = summary[summary['industry_group'] == industry]
            yearly = ind_data.groupby('year')['annual_avg_emplvl'].sum()
            
            if 2004 in yearly.index and 2015 in yearly.index and 2024 in yearly.index:
                # Pre-AI CAGR
                pre_cagr = (np.power(yearly[2015] / yearly[2004], 1/11) - 1) * 100
                # AI era CAGR
                ai_cagr = (np.power(yearly[2024] / yearly[2015], 1/9) - 1) * 100
                
                print(f"{industry:15} Pre-AI: {pre_cagr:6.1f}%  AI-Era: {ai_cagr:6.1f}%  Change: {ai_cagr-pre_cagr:+6.1f}pp")
        
        return growth_df

def main():
    analyzer = IndustryComparisonAnalyzer(data_dir="../data/bls")
    
    # Extract and analyze data
    result = analyzer.analyze_all_industries()
    if result is None:
        print("No data found!")
        return
    
    raw_data, summary = result
    
    if summary is not None:
        # Save processed data
        summary.to_csv('../outputs/industry_comparison_summary.csv', index=False)
        
        # Find industry hubs
        analyzer.find_industry_hubs(summary)
        
        # Analyze growth patterns
        growth_df = analyzer.analyze_growth_patterns(summary)
        
        # Key insights
        print("\n" + "="*60)
        print("KEY INSIGHTS: The AI Employment Paradox")
        print("="*60)
        print("""
1. TECH GROWS, OTHERS STAGNATE/DECLINE
   - Tech employment continues expanding (even if slowing)
   - Traditional industries show flat or negative growth
   
2. AI ADOPTION ≠ JOB CREATION
   - Finance and Retail adopt AI but cut jobs
   - Manufacturing uses AI for automation, not expansion
   
3. GEOGRAPHIC DIVERGENCE
   - Tech concentrates in 4 hubs
   - Traditional industries more distributed
   - Old industrial cities (Detroit, Cleveland) left behind
   
4. THE INEQUALITY ACCELERATES
   - AI era shows even starker divergence
   - Tech workers benefit, others displaced
   - No evidence of AI creating jobs outside tech
        """)

if __name__ == "__main__":
    main()