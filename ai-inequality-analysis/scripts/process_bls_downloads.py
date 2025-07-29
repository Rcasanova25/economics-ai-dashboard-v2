"""
Process BLS downloaded CSV files for tech employment analysis
Works with QCEW data downloaded from https://www.bls.gov/cew/downloadable-data-files.htm
"""

import pandas as pd
import os
from pathlib import Path
import zipfile

class BLSDataProcessor:
    """Process downloaded BLS QCEW CSV files"""
    
    def __init__(self, data_dir="data/bls"):
        self.data_dir = Path(data_dir)
        
        # MSA codes for target cities
        self.target_msas = {
            '41860': 'San Francisco-Oakland-Hayward, CA',
            '42660': 'Seattle-Tacoma-Bellevue, WA', 
            '14460': 'Boston-Cambridge-Newton, MA-NH',
            '12420': 'Austin-Round Rock-Georgetown, TX'
        }
        
        # NAICS codes for tech industries
        self.tech_naics = {
            '5415': 'Computer Systems Design and Related Services',
            '541511': 'Custom Computer Programming Services',
            '541512': 'Computer Systems Design Services',
            '518210': 'Data Processing, Hosting, and Related Services',
            '541519': 'Other Computer Related Services'
        }
        
    def load_qcew_data(self, csv_path):
        """Load and filter QCEW CSV for our target MSAs and industries"""
        
        print(f"Loading {csv_path}...")
        
        # Define columns we need to save memory
        usecols = ['area_fips', 'own_code', 'industry_code', 'agglvl_code',
                   'annual_avg_emplvl', 'total_annual_wages', 'annual_avg_wkly_wage']
        
        # QCEW CSVs have specific column names
        # Use chunks for large files
        chunk_list = []
        for chunk in pd.read_csv(csv_path, 
                                dtype={'area_fips': str, 'industry_code': str},
                                usecols=usecols,
                                chunksize=100000):
            
            # Filter for our MSAs
            msa_chunk = chunk[chunk['area_fips'].isin(self.target_msas.keys())]
            
            # Filter for private sector (own_code = 5) and appropriate aggregation level
            # agglvl_code 78 = MSA, by industry
            msa_chunk = msa_chunk[
                (msa_chunk['own_code'] == 5) & 
                (msa_chunk['agglvl_code'] == 78)
            ]
            
            # Filter for our tech industries
            tech_chunk = msa_chunk[
                msa_chunk['industry_code'].isin(self.tech_naics.keys()) |
                msa_chunk['industry_code'].str.startswith('5415')
            ]
            
            if not tech_chunk.empty:
                chunk_list.append(tech_chunk)
        
        if chunk_list:
            return pd.concat(chunk_list, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def process_annual_files(self, start_year=2019, end_year=2023):
        """Process multiple years of QCEW annual data"""
        
        all_data = []
        
        for year in range(start_year, end_year + 1):
            # Check for both .csv and .zip files
            csv_path = self.data_dir / f"{year}.annual.singlefile.csv"
            zip_path = self.data_dir / f"{year}_annual_singlefile.zip"
            by_area_zip_path = self.data_dir / f"{year}_annual_by_area.zip"
            
            if csv_path.exists():
                year_data = self.load_qcew_data(csv_path)
                if not year_data.empty:
                    year_data['year'] = year
                    all_data.append(year_data)
                    print(f"Loaded {len(year_data)} records for {year}")
            elif zip_path.exists():
                # Extract and process zip file
                print(f"Extracting {zip_path}...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract to temp location
                    csv_name = zip_ref.namelist()[0]  # Should be one CSV
                    zip_ref.extract(csv_name, self.data_dir)
                    
                    # Process the extracted CSV
                    extracted_path = self.data_dir / csv_name
                    # Add .csv extension if missing
                    if not extracted_path.suffix:
                        extracted_path = extracted_path.with_suffix('.csv')
                    year_data = self.load_qcew_data(extracted_path)
                    if not year_data.empty:
                        year_data['year'] = year
                        all_data.append(year_data)
                        print(f"Loaded {len(year_data)} records for {year}")
                    
                    # Clean up extracted file to save space
                    os.remove(extracted_path)
            elif by_area_zip_path.exists():
                # Extract and process by_area zip file
                print(f"Extracting {by_area_zip_path}...")
                with zipfile.ZipFile(by_area_zip_path, 'r') as zip_ref:
                    # Extract to temp location
                    csv_name = zip_ref.namelist()[0]  # Should be one CSV
                    zip_ref.extract(csv_name, self.data_dir)
                    
                    # Process the extracted CSV
                    extracted_path = self.data_dir / csv_name
                    # Add .csv extension if missing
                    if not extracted_path.suffix:
                        extracted_path = extracted_path.with_suffix('.csv')
                    year_data = self.load_qcew_data(extracted_path)
                    if not year_data.empty:
                        year_data['year'] = year
                        all_data.append(year_data)
                        print(f"Loaded {len(year_data)} records for {year}")
                    
                    # Clean up extracted file to save space
                    os.remove(extracted_path)
            else:
                print(f"Warning: No data file found for {year}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"\nTotal records loaded: {len(combined_df)}")
            return combined_df
        else:
            print("No data files found!")
            return None
    
    def create_employment_summary(self, df):
        """Create summary of tech employment by MSA"""
        
        # Focus on annual average employment
        summary_data = []
        
        for msa_code, msa_name in self.target_msas.items():
            msa_data = df[df['area_fips'] == msa_code]
            
            for year in df['year'].unique():
                year_data = msa_data[msa_data['year'] == year]
                
                # Sum employment across all tech industries
                total_employment = year_data['annual_avg_emplvl'].sum()
                
                # Get employment by specific NAICS
                for naics, industry_name in self.tech_naics.items():
                    industry_employment = year_data[
                        year_data['industry_code'] == naics
                    ]['annual_avg_emplvl'].sum()
                    
                    if industry_employment > 0:
                        summary_data.append({
                            'msa_code': msa_code,
                            'msa_name': msa_name,
                            'year': year,
                            'naics': naics,
                            'industry': industry_name,
                            'employment': int(industry_employment)
                        })
        
        return pd.DataFrame(summary_data)
    
    def calculate_growth_metrics(self, summary_df):
        """Calculate growth rates and concentration metrics"""
        
        # Calculate year-over-year growth
        for msa in summary_df['msa_code'].unique():
            for naics in summary_df['naics'].unique():
                mask = (summary_df['msa_code'] == msa) & (summary_df['naics'] == naics)
                msa_industry_data = summary_df[mask].sort_values('year')
                
                if len(msa_industry_data) > 1:
                    summary_df.loc[mask, 'yoy_growth'] = (
                        msa_industry_data['employment'].pct_change() * 100
                    )
        
        # Calculate share of total tech employment
        for year in summary_df['year'].unique():
            year_total = summary_df[summary_df['year'] == year]['employment'].sum()
            year_mask = summary_df['year'] == year
            summary_df.loc[year_mask, 'share_of_total'] = (
                summary_df.loc[year_mask, 'employment'] / year_total * 100
            )
        
        return summary_df

def create_download_instructions():
    """Create instructions for downloading BLS data"""
    
    instructions = """
BLS DATA DOWNLOAD INSTRUCTIONS
==============================

1. Go to: https://www.bls.gov/cew/downloadable-data-files.htm

2. Download QCEW Annual Averages (Single Files) for years 2019-2023:
   - Click on each year
   - Download "Annual Averages, All Counties, All Industries"
   - Files will be named like: 2023.annual.singlefile.csv

3. Save all files to: ai-inequality-analysis/data/bls/

4. File sizes are large (~500MB each) but contain all US employment data

Alternative: MSA-specific downloads
-----------------------------------
For smaller files, you can download MSA-specific data:
1. Go to: https://data.bls.gov/cew/apps/data_views/data_views.htm
2. Select "Metropolitan Statistical Area (MSA)"
3. Choose each MSA:
   - San Francisco-Oakland-Hayward, CA (41860)
   - Seattle-Tacoma-Bellevue, WA (42660)
   - Boston-Cambridge-Newton, MA-NH (14460)
   - Austin-Round Rock-Georgetown, TX (12420)
4. Select NAICS 5415 (Computer Systems Design)
5. Download CSV for each
    """
    
    with open('../documentation/bls_download_guide.txt', 'w') as f:
        f.write(instructions)
    
    print("Download instructions saved to: documentation/bls_download_guide.txt")
    print("\n" + instructions)

if __name__ == "__main__":
    # Check if we're creating instructions or processing data
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'process':
        # Process downloaded data
        print("Processing BLS data for tech employment analysis...")
        print("="*60)
        
        processor = BLSDataProcessor(data_dir="../data/bls")
        
        # Process files - now with 20 years of data!
        df = processor.process_annual_files(2004, 2024)
        
        if df is not None and not df.empty:
            # Create summary
            summary = processor.create_employment_summary(df)
            summary = processor.calculate_growth_metrics(summary)
            
            # Save results
            output_path = "../outputs/tech_employment_summary.csv"
            summary.to_csv(output_path, index=False)
            print(f"\nSummary saved to: {output_path}")
            
            # Print key insights
            print("\n" + "="*60)
            print("KEY FINDINGS")
            print("="*60)
            
            # Latest year employment
            latest_year = summary['year'].max()
            latest_data = summary[summary['year'] == latest_year]
            
            print(f"\nTech Employment in {latest_year}:")
            for msa in processor.target_msas.values():
                msa_total = latest_data[latest_data['msa_name'] == msa]['employment'].sum()
                print(f"  {msa}: {msa_total:,} jobs")
            
            # Growth rates - both recent and long-term
            print(f"\nGrowth from 2019 to {latest_year} (Recent):")
            for msa in processor.target_msas.values():
                msa_2019 = summary[(summary['msa_name'] == msa) & (summary['year'] == 2019)]['employment'].sum()
                msa_latest = summary[(summary['msa_name'] == msa) & (summary['year'] == latest_year)]['employment'].sum()
                if msa_2019 > 0:
                    growth = ((msa_latest - msa_2019) / msa_2019) * 100
                    print(f"  {msa}: {growth:+.1f}%")
            
            print(f"\nGrowth from 2004 to {latest_year} (20-Year):")
            for msa in processor.target_msas.values():
                msa_2004 = summary[(summary['msa_name'] == msa) & (summary['year'] == 2004)]['employment'].sum()
                msa_latest = summary[(summary['msa_name'] == msa) & (summary['year'] == latest_year)]['employment'].sum()
                if msa_2004 > 0:
                    growth = ((msa_latest - msa_2004) / msa_2004) * 100
                    print(f"  {msa}: {growth:+.1f}%")
        else:
            print("No data found! Make sure files are downloaded to data/bls/")
    else:
        # Show download instructions
        create_download_instructions()