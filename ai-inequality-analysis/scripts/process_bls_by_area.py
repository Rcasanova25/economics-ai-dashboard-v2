"""
Process BLS by_area zip files for tech employment analysis
Handles the directory structure within the zip files
"""

import pandas as pd
import os
from pathlib import Path
import zipfile
import re

class BLSByAreaProcessor:
    """Process BLS annual by area zip files"""
    
    def __init__(self, data_dir="data/bls"):
        self.data_dir = Path(data_dir)
        
        # MSA codes and names to search for
        # Note: BLS uses C prefix for MSA codes in file names
        self.target_msas = {
            'C4186': 'San Francisco-Oakland-Fremont, CA',
            'C4266': 'Seattle-Tacoma-Bellevue, WA', 
            'C1446': 'Boston-Cambridge-Newton, MA-NH',
            'C1242': 'Austin-Round Rock, TX'
        }
        
        # NAICS codes for tech industries - using ONLY 4-digit codes to avoid double counting
        # 4-digit codes capture ALL employment in their subcategories
        self.tech_naics_4digit = {
            '5415': 'Computer Systems Design and Related Services',
            '5182': 'Data Processing and Related Services'
        }
        
        # 6-digit codes for detailed breakdown if needed (not used in aggregation)
        self.tech_naics_6digit = {
            '541511': 'Custom Computer Programming Services',
            '541512': 'Computer Systems Design Services',
            '541513': 'Computer Facilities Management Services',
            '541519': 'Other Computer Related Services',
            '518210': 'Data Processing, Hosting, and Related Services'
        }
        
    def process_year_zip(self, zip_path, year):
        """Process a single year's by_area zip file"""
        
        all_data = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            
            # Find our MSA files
            for msa_code, msa_name in self.target_msas.items():
                # Look for files containing the MSA code
                msa_files = [f for f in file_list if msa_code in f and f.endswith('.csv')]
                
                for msa_file in msa_files:
                    print(f"  Processing {msa_file}...")
                    
                    # Read directly from zip
                    with zip_ref.open(msa_file) as csv_file:
                        # Read the CSV
                        df = pd.read_csv(csv_file, dtype={'area_fips': str, 'industry_code': str})
                        
                        # Filter for private sector and tech industries
                        # Use ONLY 4-digit codes to avoid double counting
                        tech_df = df[
                            (df['own_code'] == 5) &  # Private sector
                            (df['industry_code'].isin(self.tech_naics_4digit.keys()))  # Only 4-digit codes
                        ]
                        
                        if not tech_df.empty:
                            tech_df['year'] = year
                            tech_df['msa_name'] = msa_name
                            all_data.append(tech_df)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def process_all_years(self, start_year=2004, end_year=2024):
        """Process all year zip files"""
        
        print("Processing BLS by_area data for tech employment...")
        print("="*60)
        
        all_data = []
        
        for year in range(start_year, end_year + 1):
            zip_path = self.data_dir / f"{year}_annual_by_area.zip"
            
            if zip_path.exists():
                print(f"\nProcessing {year}...")
                year_data = self.process_year_zip(zip_path, year)
                if not year_data.empty:
                    all_data.append(year_data)
                    print(f"  Found {len(year_data)} tech employment records")
            else:
                print(f"Skipping {year} - file not found")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"\n\nTotal records: {len(combined_df)}")
            return combined_df
        else:
            return pd.DataFrame()
    
    def create_summary(self, df):
        """Create employment summary by MSA and year"""
        
        if df.empty:
            return pd.DataFrame()
        
        summary = []
        
        for year in sorted(df['year'].unique()):
            year_df = df[df['year'] == year]
            
            for msa in self.target_msas.values():
                msa_df = year_df[year_df['msa_name'] == msa]
                
                if not msa_df.empty:
                    # Sum employment across tech industries
                    total_employment = msa_df['annual_avg_emplvl'].sum()
                    avg_wage = msa_df['annual_avg_wkly_wage'].mean()
                    
                    summary.append({
                        'year': year,
                        'msa': msa,
                        'tech_employment': int(total_employment),
                        'avg_weekly_wage': int(avg_wage) if pd.notna(avg_wage) else None
                    })
        
        return pd.DataFrame(summary)
    
    def analyze_trends(self, summary_df):
        """Analyze growth trends and inequality"""
        
        print("\n" + "="*60)
        print("TECH EMPLOYMENT INEQUALITY ANALYSIS")
        print("="*60)
        
        # Latest year data
        latest_year = summary_df['year'].max()
        latest = summary_df[summary_df['year'] == latest_year]
        
        print(f"\nTech Employment in {latest_year}:")
        print("-"*40)
        total = latest['tech_employment'].sum()
        for _, row in latest.iterrows():
            pct = (row['tech_employment'] / total) * 100
            print(f"{row['msa']}: {row['tech_employment']:,} jobs ({pct:.1f}% of total)")
        
        # Long-term growth
        earliest_year = summary_df['year'].min()
        earliest = summary_df[summary_df['year'] == earliest_year]
        
        print(f"\nGrowth from {earliest_year} to {latest_year}:")
        print("-"*40)
        for msa in summary_df['msa'].unique():
            early = earliest[earliest['msa'] == msa]['tech_employment'].sum()
            late = latest[latest['msa'] == msa]['tech_employment'].sum()
            if early > 0:
                growth = ((late - early) / early) * 100
                print(f"{msa}: {growth:+.1f}% ({early:,} → {late:,})")
        
        # Concentration trends
        print("\nConcentration of Tech Employment:")
        print("-"*40)
        
        for year in [earliest_year, 2015, latest_year]:
            year_df = summary_df[summary_df['year'] == year]
            if not year_df.empty:
                total = year_df['tech_employment'].sum()
                top2 = year_df.nlargest(2, 'tech_employment')['tech_employment'].sum()
                print(f"{year}: Top 2 cities have {(top2/total)*100:.1f}% of tech jobs")

if __name__ == "__main__":
    processor = BLSByAreaProcessor(data_dir="../data/bls")
    
    # Process all years
    df = processor.process_all_years(2004, 2024)
    
    if not df.empty:
        # Create summary
        summary = processor.create_summary(df)
        
        # Save results
        df.to_csv("../outputs/tech_employment_raw.csv", index=False)
        summary.to_csv("../outputs/tech_employment_summary.csv", index=False)
        
        # Analyze trends
        processor.analyze_trends(summary)
        
        print("\n\nData saved to outputs folder.")
    else:
        print("No data found!")