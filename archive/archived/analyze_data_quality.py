"""
Data Quality Analysis Script for Economics AI Dashboard
Week 3: Deep analysis and cleanup of extracted metrics

This script performs comprehensive data quality checks including:
1. Duplicate detection across all metric types
2. Invalid data identification (years, units, values)
3. Outlier detection
4. Data consistency checks
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import defaultdict
import os

class DataQualityAnalyzer:
    def __init__(self, csv_path):
        """Initialize the analyzer with the metrics CSV file"""
        self.df = pd.read_csv(csv_path)
        self.issues = {
            'duplicates': [],
            'invalid_years': [],
            'invalid_units': [],
            'outliers': [],
            'misclassified': [],
            'missing_data': []
        }
        self.stats = {}
        
    def analyze_all(self):
        """Run all quality checks"""
        print("Starting comprehensive data quality analysis...")
        print(f"Total records: {len(self.df)}")
        print(f"Unique metric types: {self.df['metric_type'].nunique()}")
        print("-" * 80)
        
        # Run all analyses
        self.analyze_duplicates()
        self.analyze_temporal_issues()
        self.analyze_unit_consistency()
        self.analyze_outliers()
        self.analyze_missing_data()
        self.analyze_metric_classification()
        
        # Generate summary report
        self.generate_report()
        
    def analyze_duplicates(self):
        """Identify duplicate entries across all metric types"""
        print("\n1. DUPLICATE ANALYSIS")
        print("-" * 40)
        
        # Group by metric type and analyze duplicates
        duplicate_stats = {}
        
        for metric_type in self.df['metric_type'].unique():
            metric_df = self.df[self.df['metric_type'] == metric_type]
            
            # Check for exact duplicates (same value, unit, year, context)
            duplicate_cols = ['value', 'unit', 'year', 'context']
            duplicates = metric_df[metric_df.duplicated(subset=duplicate_cols, keep=False)]
            
            if len(duplicates) > 0:
                duplicate_groups = duplicates.groupby(duplicate_cols).size().reset_index(name='count')
                duplicate_groups = duplicate_groups[duplicate_groups['count'] > 1]
                
                duplicate_stats[metric_type] = {
                    'total_duplicates': len(duplicates),
                    'unique_duplicate_sets': len(duplicate_groups),
                    'examples': []
                }
                
                # Store examples of duplicates
                for _, group in duplicate_groups.head(3).iterrows():
                    example_records = duplicates[
                        (duplicates['value'] == group['value']) &
                        (duplicates['unit'] == group['unit']) &
                        (duplicates['year'] == group['year']) &
                        (duplicates['context'] == group['context'])
                    ]
                    
                    duplicate_stats[metric_type]['examples'].append({
                        'value': group['value'],
                        'unit': group['unit'],
                        'year': group['year'],
                        'context': group['context'][:100] + '...' if len(str(group['context'])) > 100 else group['context'],
                        'occurrences': group['count'],
                        'source_ids': example_records['source_id'].unique().tolist()
                    })
                    
                self.issues['duplicates'].append({
                    'metric_type': metric_type,
                    'stats': duplicate_stats[metric_type]
                })
        
        # Print summary
        total_duplicates = sum(stats['total_duplicates'] for stats in duplicate_stats.values())
        print(f"Total duplicate records found: {total_duplicates}")
        print(f"Metric types with duplicates: {len(duplicate_stats)}")
        
        for metric_type, stats in duplicate_stats.items():
            print(f"\n  {metric_type}:")
            print(f"    - Duplicate records: {stats['total_duplicates']}")
            print(f"    - Unique duplicate sets: {stats['unique_duplicate_sets']}")
            
    def analyze_temporal_issues(self):
        """Check for invalid years and temporal inconsistencies"""
        print("\n2. TEMPORAL DATA ANALYSIS")
        print("-" * 40)
        
        current_year = datetime.now().year
        
        # Check for invalid years
        year_issues = []
        
        # Future years (beyond current year + 5 for forecasts)
        future_mask = self.df['year'] > current_year + 5
        if future_mask.any():
            future_years = self.df[future_mask][['year', 'metric_type', 'context']].drop_duplicates()
            year_issues.extend([{
                'issue': 'future_year',
                'year': row['year'],
                'metric_type': row['metric_type'],
                'context': row['context'][:100] + '...' if len(str(row['context'])) > 100 else row['context']
            } for _, row in future_years.iterrows()])
            
        # Very old years (before 2000 for AI metrics seems suspicious)
        past_mask = self.df['year'] < 2000
        if past_mask.any():
            past_years = self.df[past_mask][['year', 'metric_type', 'context']].drop_duplicates()
            year_issues.extend([{
                'issue': 'too_old',
                'year': row['year'],
                'metric_type': row['metric_type'],
                'context': row['context'][:100] + '...' if len(str(row['context'])) > 100 else row['context']
            } for _, row in past_years.iterrows()])
            
        self.issues['invalid_years'] = year_issues
        
        print(f"Records with future years (>{current_year + 5}): {future_mask.sum()}")
        print(f"Records with very old years (<2000): {past_mask.sum()}")
        
        # Year distribution
        year_dist = self.df['year'].value_counts().sort_index()
        print(f"\nYear distribution:")
        print(f"  - Min year: {year_dist.index.min()}")
        print(f"  - Max year: {year_dist.index.max()}")
        print(f"  - Most common years: {year_dist.head(5).to_dict()}")
        
    def analyze_unit_consistency(self):
        """Check for invalid or inconsistent units"""
        print("\n3. UNIT CONSISTENCY ANALYSIS")
        print("-" * 40)
        
        # Expected units for different metric types
        expected_units = {
            'investment_metric': ['billions_usd', 'millions_usd', 'usd', 'percentage'],
            'adoption_metric': ['percentage', 'number', 'rate'],
            'productivity_metric': ['percentage', 'hours', 'rate'],
            'employment_metric': ['number', 'percentage', 'thousands', 'millions'],
            'gdp_metric': ['billions_usd', 'percentage', 'trillions_usd'],
            'revenue_metric': ['billions_usd', 'millions_usd', 'usd', 'percentage'],
            'cost_metric': ['billions_usd', 'millions_usd', 'usd', 'percentage']
        }
        
        unit_issues = []
        
        # Check each metric type
        for metric_type in self.df['metric_type'].unique():
            metric_df = self.df[self.df['metric_type'] == metric_type]
            units_used = metric_df['unit'].value_counts()
            
            # Check for unusual units
            if metric_type in expected_units:
                unusual_units = [unit for unit in units_used.index 
                               if unit not in expected_units[metric_type] and pd.notna(unit)]
                if unusual_units:
                    for unit in unusual_units:
                        examples = metric_df[metric_df['unit'] == unit].head(3)
                        unit_issues.append({
                            'metric_type': metric_type,
                            'unusual_unit': unit,
                            'count': units_used[unit],
                            'examples': examples[['value', 'year', 'context']].to_dict('records')
                        })
            
            # Check for 'energy_unit' or other clearly wrong units
            wrong_units = ['energy_unit', 'distance_unit', 'weight_unit']
            for wrong_unit in wrong_units:
                if wrong_unit in units_used.index:
                    examples = metric_df[metric_df['unit'] == wrong_unit].head(3)
                    unit_issues.append({
                        'metric_type': metric_type,
                        'wrong_unit': wrong_unit,
                        'count': units_used[wrong_unit],
                        'examples': examples[['value', 'year', 'context']].to_dict('records')
                    })
                    
        self.issues['invalid_units'] = unit_issues
        
        print(f"Metric types with unit issues: {len(set(issue['metric_type'] for issue in unit_issues))}")
        print(f"Total unit inconsistencies found: {sum(issue['count'] for issue in unit_issues)}")
        
        # Show unit distribution
        print("\nMost common units across all metrics:")
        unit_counts = self.df['unit'].value_counts().head(10)
        for unit, count in unit_counts.items():
            print(f"  - {unit}: {count}")
            
    def analyze_outliers(self):
        """Identify statistical outliers in values"""
        print("\n4. OUTLIER ANALYSIS")
        print("-" * 40)
        
        outlier_issues = []
        
        # Analyze by metric type and unit combination
        for metric_type in self.df['metric_type'].unique():
            metric_df = self.df[self.df['metric_type'] == metric_type]
            
            for unit in metric_df['unit'].unique():
                if pd.isna(unit):
                    continue
                    
                unit_df = metric_df[metric_df['unit'] == unit]
                if len(unit_df) < 10:  # Skip if too few samples
                    continue
                
                values = unit_df['value'].dropna()
                if len(values) == 0:
                    continue
                
                # Calculate outliers using IQR method
                Q1 = values.quantile(0.25)
                Q3 = values.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 3 * IQR  # Using 3*IQR for extreme outliers
                upper_bound = Q3 + 3 * IQR
                
                outliers = unit_df[(unit_df['value'] < lower_bound) | (unit_df['value'] > upper_bound)]
                
                if len(outliers) > 0:
                    outlier_issues.append({
                        'metric_type': metric_type,
                        'unit': unit,
                        'outlier_count': len(outliers),
                        'value_range': f"{values.min():.2f} to {values.max():.2f}",
                        'normal_range': f"{lower_bound:.2f} to {upper_bound:.2f}",
                        'examples': outliers.nlargest(3, 'value')[['value', 'year', 'context']].to_dict('records')
                    })
                    
        self.issues['outliers'] = outlier_issues
        
        print(f"Metric type/unit combinations with outliers: {len(outlier_issues)}")
        print(f"Total outlier records: {sum(issue['outlier_count'] for issue in outlier_issues)}")
        
        # Show most extreme cases
        if outlier_issues:
            print("\nMost extreme outlier cases:")
            sorted_outliers = sorted(outlier_issues, key=lambda x: x['outlier_count'], reverse=True)
            for issue in sorted_outliers[:5]:
                print(f"  - {issue['metric_type']} ({issue['unit']}): {issue['outlier_count']} outliers")
                print(f"    Value range: {issue['value_range']}, Normal range: {issue['normal_range']}")
                
    def analyze_missing_data(self):
        """Check for missing or null values"""
        print("\n5. MISSING DATA ANALYSIS")
        print("-" * 40)
        
        missing_stats = {}
        for col in self.df.columns:
            missing_count = self.df[col].isna().sum()
            if missing_count > 0:
                missing_stats[col] = {
                    'count': missing_count,
                    'percentage': (missing_count / len(self.df)) * 100
                }
                
        self.issues['missing_data'] = missing_stats
        
        print("Columns with missing data:")
        for col, stats in missing_stats.items():
            print(f"  - {col}: {stats['count']} ({stats['percentage']:.2f}%)")
            
    def analyze_metric_classification(self):
        """Check for potentially misclassified metrics"""
        print("\n6. METRIC CLASSIFICATION ANALYSIS")
        print("-" * 40)
        
        # Metrics like "general_rate" and "unknown_metric" need reclassification
        vague_types = ['general_rate', 'unknown_metric', 'percentage']
        
        classification_issues = []
        
        for vague_type in vague_types:
            vague_df = self.df[self.df['metric_type'] == vague_type]
            if len(vague_df) > 0:
                # Sample some records to understand what they might actually be
                samples = vague_df.sample(min(10, len(vague_df)))[['value', 'unit', 'year', 'context']]
                
                classification_issues.append({
                    'metric_type': vague_type,
                    'count': len(vague_df),
                    'percentage': (len(vague_df) / len(self.df)) * 100,
                    'samples': samples.to_dict('records')
                })
                
        self.issues['misclassified'] = classification_issues
        
        print(f"Vague metric types found: {len(classification_issues)}")
        for issue in classification_issues:
            print(f"  - {issue['metric_type']}: {issue['count']} records ({issue['percentage']:.2f}%)")
            
    def generate_report(self):
        """Generate comprehensive data quality report"""
        print("\n" + "=" * 80)
        print("DATA QUALITY SUMMARY REPORT")
        print("=" * 80)
        
        # Calculate overall statistics
        total_issues = (
            sum(len(issue['stats']['examples']) for issue in self.issues['duplicates']) +
            len(self.issues['invalid_years']) +
            sum(issue['count'] for issue in self.issues['invalid_units']) +
            sum(issue['outlier_count'] for issue in self.issues['outliers']) +
            sum(issue['count'] for issue in self.issues['misclassified'])
        )
        
        print(f"\nTotal records analyzed: {len(self.df)}")
        print(f"Total quality issues found: {total_issues}")
        print(f"Percentage of records with issues: {(total_issues / len(self.df)) * 100:.2f}%")
        
        # Save detailed report to JSON
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_records': len(self.df),
            'total_issues': total_issues,
            'issues': self.issues,
            'recommendations': self.generate_recommendations()
        }
        
        report_path = 'data_quality_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\nDetailed report saved to: {report_path}")
        
        # Save cleaned data recommendations
        self.save_cleaning_recommendations()
        
    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # Duplicate handling
        if self.issues['duplicates']:
            recommendations.append({
                'issue': 'Duplicates',
                'recommendation': 'Implement deduplication by keeping highest confidence score or first occurrence per source',
                'priority': 'HIGH'
            })
            
        # Year issues
        if self.issues['invalid_years']:
            recommendations.append({
                'issue': 'Invalid Years',
                'recommendation': 'Review and correct years > 2030 or < 2000, likely extraction errors',
                'priority': 'HIGH'
            })
            
        # Unit issues
        if self.issues['invalid_units']:
            recommendations.append({
                'issue': 'Invalid Units',
                'recommendation': 'Standardize units and fix misclassified units like "energy_unit"',
                'priority': 'MEDIUM'
            })
            
        # Outliers
        if self.issues['outliers']:
            recommendations.append({
                'issue': 'Outliers',
                'recommendation': 'Review extreme values for potential extraction errors or unit confusion',
                'priority': 'MEDIUM'
            })
            
        # Misclassified metrics
        if self.issues['misclassified']:
            recommendations.append({
                'issue': 'Vague Classifications',
                'recommendation': 'Reclassify "general_rate" and "unknown_metric" based on context analysis',
                'priority': 'HIGH'
            })
            
        return recommendations
    
    def save_cleaning_recommendations(self):
        """Save specific records that need cleaning"""
        cleaning_df = pd.DataFrame()
        
        # Add duplicates
        for issue in self.issues['duplicates']:
            metric_type = issue['metric_type']
            for example in issue['stats']['examples']:
                duplicate_records = self.df[
                    (self.df['metric_type'] == metric_type) &
                    (self.df['value'] == example['value']) &
                    (self.df['unit'] == example['unit']) &
                    (self.df['year'] == example['year'])
                ]
                duplicate_records['issue_type'] = 'duplicate'
                duplicate_records['issue_details'] = f"Appears {example['occurrences']} times"
                cleaning_df = pd.concat([cleaning_df, duplicate_records])
                
        # Add temporal issues
        for issue in self.issues['invalid_years']:
            invalid_year_records = self.df[
                (self.df['year'] == issue['year']) &
                (self.df['metric_type'] == issue['metric_type'])
            ]
            invalid_year_records['issue_type'] = 'invalid_year'
            invalid_year_records['issue_details'] = issue['issue']
            cleaning_df = pd.concat([cleaning_df, invalid_year_records])
            
        # Save to CSV
        if not cleaning_df.empty:
            cleaning_df.to_csv('records_needing_cleaning.csv', index=False)
            print(f"\nRecords needing cleaning saved to: records_needing_cleaning.csv")
            print(f"Total records flagged for cleaning: {len(cleaning_df)}")


if __name__ == "__main__":
    # Run the analysis
    analyzer = DataQualityAnalyzer('data/exports/ai_metrics_20250719.csv')
    analyzer.analyze_all()