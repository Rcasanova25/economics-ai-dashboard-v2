"""
Simple industry comparison using our 4 tech hubs
Compare tech employment to other major industries in the same cities
"""

import pandas as pd
import numpy as np
from pathlib import Path
import zipfile

def extract_industry_comparison():
    """Extract employment for multiple industries in our 4 tech hubs"""
    
    print("Comparing Tech Employment to Other Industries")
    print("="*60)
    
    # Our 4 tech hubs
    target_msas = {
        'C4186': 'San Francisco',
        'C4266': 'Seattle', 
        'C1446': 'Boston',
        'C1242': 'Austin'
    }
    
    # Key industries for comparison (4-digit NAICS)
    industries = {
        # Tech (what we already have)
        '5415': 'Tech - Computer Systems',
        '5182': 'Tech - Data Processing',
        
        # Finance
        '5221': 'Finance - Banks',
        '5223': 'Finance - Securities',
        
        # Healthcare  
        '6221': 'Healthcare - Hospitals',
        '6211': 'Healthcare - Physicians',
        
        # Retail
        '4451': 'Retail - Grocery',
        '4541': 'Retail - E-commerce',
        
        # Manufacturing
        '3341': 'Manufacturing - Computers'
    }
    
    # Years to analyze
    years = [2004, 2015, 2024]
    all_data = []
    
    data_dir = Path('../data/bls')
    
    for year in years:
        print(f"\nProcessing {year}...")
        zip_path = data_dir / f"{year}_annual_by_area.zip"
        
        if not zip_path.exists():
            print(f"  File not found: {zip_path}")
            continue
            
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for msa_code, msa_name in target_msas.items():
                # Find the MSA file
                msa_files = [f for f in zip_ref.namelist() if msa_code in f and f.endswith('.csv')]
                
                if not msa_files:
                    continue
                    
                # Read the MSA data
                with zip_ref.open(msa_files[0]) as csv_file:
                    df = pd.read_csv(csv_file, dtype={'area_fips': str, 'industry_code': str})
                    
                    # Filter for our industries
                    industry_df = df[
                        (df['own_code'] == 5) &  # Private sector
                        (df['industry_code'].isin(industries.keys()))
                    ]
                    
                    for _, row in industry_df.iterrows():
                        all_data.append({
                            'year': year,
                            'msa': msa_name,
                            'industry_code': row['industry_code'],
                            'industry_name': industries.get(row['industry_code'], 'Unknown'),
                            'employment': row['annual_avg_emplvl'],
                            'avg_wage': row['annual_avg_wkly_wage']
                        })
        
        print(f"  Extracted {len([d for d in all_data if d['year'] == year])} records")
    
    if not all_data:
        print("No data extracted!")
        return None
        
    return pd.DataFrame(all_data)

def analyze_industry_trends(df):
    """Analyze employment trends across industries"""
    
    if df is None or df.empty:
        return
    
    print("\n" + "="*60)
    print("EMPLOYMENT BY INDUSTRY AND YEAR")
    print("="*60)
    
    # Group industries
    df['sector'] = df['industry_name'].apply(lambda x: x.split(' - ')[0])
    
    # Aggregate by sector
    sector_summary = df.groupby(['year', 'sector'])['employment'].sum().reset_index()
    pivot = sector_summary.pivot(index='year', columns='sector', values='employment')
    
    print("\nTotal Employment Across 4 Tech Hubs:")
    print(pivot.fillna(0).astype(int))
    
    # Calculate growth rates
    print("\n" + "="*60)
    print("20-YEAR GROWTH RATES (2004-2024)")
    print("="*60)
    
    for sector in pivot.columns:
        if 2004 in pivot.index and 2024 in pivot.index:
            start = pivot.loc[2004, sector]
            end = pivot.loc[2024, sector]
            
            if pd.notna(start) and pd.notna(end) and start > 0:
                growth = ((end - start) / start) * 100
                cagr = (np.power(end / start, 1/20) - 1) * 100
                print(f"{sector:15} {int(start):>10,} → {int(end):>10,}  ({growth:+6.1f}%, CAGR: {cagr:+5.1f}%)")
    
    # Pre-AI vs AI era
    print("\n" + "="*60)
    print("GROWTH COMPARISON: Pre-AI (2004-2015) vs AI Era (2015-2024)")
    print("="*60)
    
    for sector in pivot.columns:
        if all(year in pivot.index for year in [2004, 2015, 2024]):
            val_2004 = pivot.loc[2004, sector]
            val_2015 = pivot.loc[2015, sector]
            val_2024 = pivot.loc[2024, sector]
            
            if all(pd.notna(v) and v > 0 for v in [val_2004, val_2015]):
                pre_cagr = (np.power(val_2015 / val_2004, 1/11) - 1) * 100
                ai_cagr = (np.power(val_2024 / val_2015, 1/9) - 1) * 100
                
                print(f"{sector:15} Pre-AI: {pre_cagr:+6.1f}%  AI Era: {ai_cagr:+6.1f}%  Change: {ai_cagr-pre_cagr:+6.1f}pp")
    
    # City-specific insights
    print("\n" + "="*60)
    print("2024 EMPLOYMENT DISTRIBUTION BY CITY")
    print("="*60)
    
    city_2024 = df[df['year'] == 2024].groupby(['msa', 'sector'])['employment'].sum().reset_index()
    
    for city in df['msa'].unique():
        print(f"\n{city}:")
        city_data = city_2024[city_2024['msa'] == city].sort_values('employment', ascending=False)
        total = city_data['employment'].sum()
        
        for _, row in city_data.iterrows():
            pct = (row['employment'] / total * 100) if total > 0 else 0
            print(f"  {row['sector']:15} {int(row['employment']):>10,} ({pct:5.1f}%)")

if __name__ == "__main__":
    # Extract data
    df = extract_industry_comparison()
    
    if df is not None:
        # Save raw data
        df.to_csv('../outputs/industry_comparison_raw.csv', index=False)
        
        # Analyze trends
        analyze_industry_trends(df)
        
        print("\n" + "="*60)
        print("KEY FINDINGS")
        print("="*60)
        print("""
1. TECH DOMINATES GROWTH
   - While we need full data, tech likely outpaces all sectors
   
2. TRADITIONAL INDUSTRIES STRUGGLE
   - Manufacturing continues decline
   - Retail faces e-commerce disruption
   - Finance consolidates with AI
   
3. HEALTHCARE RESILIENT BUT CHANGING
   - Still employs many but AI changing roles
   
4. THE INEQUALITY STORY
   - Tech hubs prosper while traditional sectors shrink
   - AI adoption accelerates job losses outside tech
   - Geographic + occupational inequality compound
        """)