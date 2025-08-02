"""
Universal Source Cleanup Analysis Template
This template incorporates all lessons learned from Sources 1, 2, and 7
Key features:
- Proper duplicate handling (keeps first occurrence)
- Comprehensive metric reclassification
- Context-aware data validation
- Traceability with confidence scores
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class SourceCleanupAnalyzer:
    def __init__(self, source_id, previous_cleaned_file='ai_metrics.csv'):
        """
        Initialize analyzer for a specific source
        
        Args:
            source_id: The ID of the source to analyze
            previous_cleaned_file: The CSV file with previously cleaned data
        """
        # Load the dataset
        self.df = pd.read_csv(previous_cleaned_file)
        self.source_id = source_id
        self.source_df = self.df[self.df['source_id'] == source_id].copy()
        
        # Get source name
        sources_df = pd.read_csv('data/exports/data_sources_20250719.csv')
        self.source_name = sources_df[sources_df['id'] == source_id]['name'].values[0]
        
        self.records_to_keep = []
        self.records_to_remove = []
        self.records_to_modify = []
        
        # Track duplicate groups for proper handling
        self.duplicate_groups = {}
        
    def analyze(self):
        """Run complete analysis and categorize all records"""
        print("=" * 80)
        print(f"SOURCE {self.source_id} CLEANUP ANALYSIS")
        print(f"File: {self.source_name}")
        print("=" * 80)
        print(f"Total records to analyze: {len(self.source_df)}")
        
        if len(self.source_df) == 0:
            print("No records found for this source.")
            return
        
        # First, understand the data
        self.print_initial_analysis()
        
        # Pre-process to identify duplicate groups
        self.identify_duplicate_groups()
        
        # Analyze each record
        for idx, row in self.source_df.iterrows():
            self.categorize_record(idx, row)
            
        # Generate reports
        self.generate_csv_reports()
        self.generate_summary()
        
    def print_initial_analysis(self):
        """Print initial data analysis"""
        print("\nINITIAL DATA ANALYSIS:")
        print("-" * 40)
        
        # Metric type distribution
        print("\nMetric Type Distribution:")
        metric_dist = self.source_df['metric_type'].value_counts()
        for metric, count in metric_dist.head(10).items():
            print(f"  {metric}: {count} ({count/len(self.source_df)*100:.1f}%)")
            
        # Unit distribution
        print("\nUnit Distribution:")
        unit_dist = self.source_df['unit'].value_counts()
        for unit, count in unit_dist.head(10).items():
            print(f"  {unit}: {count}")
            
        # Check for problematic units
        problem_units = ['energy_unit', 'unknown', 'multiple', 'co2_emissions']
        found_problems = [u for u in problem_units if u in unit_dist.index]
        if found_problems:
            print(f"\n  WARNING: Problem units found: {found_problems}")
            
        # Year distribution
        print("\nYear Distribution:")
        year_dist = self.source_df['year'].value_counts().sort_index()
        if len(year_dist) > 0:
            print(f"  Range: {year_dist.index.min()} - {year_dist.index.max()}")
        
        # Value analysis for common patterns
        print("\nCommon Values (top 10):")
        value_counts = self.source_df['value'].value_counts().head(10)
        for value, count in value_counts.items():
            if count > 3:  # Only show values that appear frequently
                print(f"  {value}: appears {count} times")
                
    def identify_duplicate_groups(self):
        """Pre-identify duplicate groups to handle first occurrence properly"""
        self.duplicate_groups = {}
        
        # Group by value/unit/year - the key duplicate indicators
        grouped = self.source_df.groupby(['value', 'unit', 'year'])
        
        for (value, unit, year), group in grouped:
            if len(group) > 1:
                # Sort by index to ensure we keep the first occurrence
                sorted_group = group.sort_index()
                # Store first occurrence and duplicates separately
                self.duplicate_groups[(value, unit, year)] = {
                    'first': sorted_group.index[0],
                    'duplicates': sorted_group.index[1:].tolist(),
                    'count': len(group)
                }
                
        print(f"\nIdentified {len(self.duplicate_groups)} duplicate groups")
        if self.duplicate_groups:
            # Show some examples
            print("Examples of duplicate groups:")
            for i, (key, info) in enumerate(list(self.duplicate_groups.items())[:3]):
                print(f"  - {key}: {info['count']} occurrences")
        
    def categorize_record(self, idx, row):
        """Categorize each record into keep/remove/modify"""
        context = str(row['context']).lower()
        value = row['value']
        unit = row['unit']
        metric_type = row['metric_type']
        year = row['year']
        
        # SPECIAL HANDLING FOR ZERO VALUES - Check context first
        if value == 0.0 and unit == 'percentage':
            # Check if it's meaningful (e.g., "0% increase", "no change")
            meaningful_zero_keywords = ['no change', 'zero', 'unchanged', 'baseline', 'none', 'not', 'without', 'decrease']
            if not any(keyword in context for keyword in meaningful_zero_keywords):
                # Check context length - very short contexts are often artifacts
                if len(context) < 50:
                    self.records_to_remove.append({
                        'original_id': idx,
                        'value': value,
                        'unit': unit,
                        'year': year,
                        'metric_type': metric_type,
                        'context_preview': context[:100] + '...' if len(context) > 100 else context,
                        'reason': 'Zero percentage likely extraction artifact',
                        'confidence': 0.75
                    })
                    return
        
        # CHECK FOR DUPLICATES - but with context awareness
        dup_key = (value, unit, year)
        if dup_key in self.duplicate_groups:
            dup_info = self.duplicate_groups[dup_key]
            
            if idx == dup_info['first']:
                # This is the first occurrence - continue processing
                pass
            elif idx in dup_info['duplicates']:
                # For meaningful values, check if contexts are actually similar
                if value != 0.0 or not self._is_meaningful_context(context):
                    # This is a duplicate - mark for removal
                    self.records_to_remove.append({
                        'original_id': idx,
                        'value': value,
                        'unit': unit,
                        'year': year,
                        'metric_type': metric_type,
                        'context_preview': context[:100] + '...' if len(context) > 100 else context,
                        'reason': 'Duplicate record (keeping first occurrence)',
                        'confidence': 0.90
                    })
                    return
        
        # 2. Check for problematic units
        if unit in ['energy_unit', 'unknown', 'multiple', 'co2_emissions']:
            # Energy unit is often a misclassified year
            if unit == 'energy_unit' and 1950 <= value <= 2030:
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': 'reference_year',
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': self.extract_sector(context),
                    'country': '',
                    'company_size': '',
                    'reason': 'Energy unit is a misclassified year/reference',
                    'confidence': 0.95
                })
            else:
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': f'Problematic unit: {unit}',
                    'confidence': 0.85
                })
            return
            
        # 3. Check for vague metric classifications
        if metric_type in ['general_rate', 'general_metric', 'unknown_metric']:
            new_type = self.classify_metric_type(context, value, unit, metric_type)
            if new_type != metric_type:
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': new_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': self.extract_sector(context),
                    'country': '',
                    'company_size': '',
                    'reason': f'Reclassify based on context: {new_type}',
                    'confidence': 0.80
                })
            else:
                self.records_to_keep.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': f'{metric_type} - needs manual review',
                    'confidence': 0.50
                })
            return
            
        # 4. Check for financial metric unit inconsistencies
        if unit == 'billions_usd':
            # Check if context suggests smaller amounts
            small_amount_indicators = ['thousand', 'hundred', '100k', '500k', 'k usd', 'k$']
            if any(indicator in context for indicator in small_amount_indicators):
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': self.extract_sector(context),
                    'country': '',
                    'company_size': '',
                    'reason': 'Fix unit: billions_usd should be thousands based on context',
                    'confidence': 0.90
                })
                return
                
            # Check if from figure/table labels
            if any(word in context for word in ['figure', 'table', 'exhibit', 'appendix']):
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'Likely from figure/table numbering',
                    'confidence': 0.85
                })
                return
                
        # Default - keep the record
        self.records_to_keep.append({
            'original_id': idx,
            'value': value,
            'unit': unit,
            'year': year,
            'metric_type': metric_type,
            'context_preview': context[:100] + '...' if len(context) > 100 else context,
            'reason': 'No issues detected',
            'confidence': 0.80
        })
        
    def classify_metric_type(self, context, value, unit, current_type):
        """Classify vague metric types based on context with enhanced pattern matching"""
        # Convert context to lowercase for consistent matching
        context = context.lower()
        
        # FINANCIAL METRICS - Check first as these are high priority
        financial_patterns = [
            'revenue', 'profit', 'earnings', 'income', 'sales', 'turnover',
            'financial return', 'monetary', 'dollar', 'cost savings', 'savings'
        ]
        if any(pattern in context for pattern in financial_patterns):
            # Special case: if it's about revenue/profit increase, it's financial
            if any(word in context for word in ['revenue increase', 'profit increase', 'earnings growth']):
                return 'financial_metric'
            # ROI is always financial
            if 'roi' in context or 'return on investment' in context:
                return 'financial_metric'
            return 'financial_metric'
            
        # TRAINING/SKILLS METRICS - Important for workforce development
        training_patterns = [
            'training', 'skill', 'literacy', 'education', 'learning', 'upskilling',
            'reskilling', 'certification', 'competency', 'capability'
        ]
        if any(pattern in context for pattern in training_patterns):
            # Special case: "AI literacy skills increased by X%" is training
            if 'literacy' in context and ('skill' in context or 'training' in context):
                return 'training_metric'
            return 'training_metric'
            
        # WORKPLACE/WELLBEING METRICS - Employee satisfaction and burnout
        workplace_patterns = [
            'burned out', 'burnout', 'satisfaction', 'wellbeing', 'well-being',
            'stress', 'workload', 'work-life', 'employee experience', 'morale'
        ]
        if any(pattern in context for pattern in workplace_patterns):
            return 'workplace_metric'
            
        # MARKET METRICS - Market size, business statistics
        if ('businesses' in context and 'workers' in context) or \
           ('market size' in context) or \
           ('market share' in context) or \
           ('% of businesses' in context):
            return 'market_metric'
            
        # COST METRICS - Expenses and investments (but not revenue)
        cost_patterns = [
            'cost', 'expense', 'budget', 'spending', 'expenditure',
            'investment', 'capital', 'funding'
        ]
        if any(pattern in context for pattern in cost_patterns):
            # Don't classify as cost if it's about returns/revenue
            if not any(rev in context for rev in ['revenue', 'return', 'profit', 'earnings']):
                return 'cost_metric'
                
        # AI READINESS/MATURITY
        if any(word in context for word in ['readiness', 'maturity', 'stage', 'level', 'preparedness']):
            # But not if it's about revenue readiness
            if 'revenue' not in context:
                return 'readiness_metric'
            
        # STRATEGY/PLANNING
        if any(word in context for word in ['strategy', 'strategic', 'plan', 'initiative', 'roadmap']):
            return 'strategy_metric'
            
        # ADOPTION/IMPLEMENTATION
        adoption_patterns = [
            'adopt', 'implement', 'deploy', 'rollout', 'integration',
            'using for', 'use cases', 'utilization'
        ]
        if any(pattern in context for pattern in adoption_patterns):
            # Special case: "using gai for innovation" is adoption
            if 'using' in context and 'for' in context:
                return 'adoption_metric'
            return 'adoption_metric'
            
        # PERFORMANCE/PRODUCTIVITY
        if any(word in context for word in ['performance', 'productivity', 'efficiency', 'output', 'effectiveness']):
            # But not if it's about productive capacity (that's capacity metric)
            if 'productive capacity' not in context:
                return 'performance_metric'
                
        # CAPACITY METRICS - Production capacity, potential
        if 'productive capacity' in context or 'capacity' in context:
            return 'capacity_metric'
            
        # EMPLOYMENT/LABOR
        employment_patterns = [
            'employment', 'labor', 'worker', 'job', 'occupation', 'workforce',
            'talent', 'hiring', 'recruit'
        ]
        if any(pattern in context for pattern in employment_patterns):
            # But not if it's about market size (X% of workers)
            if '% of workers' in context and 'businesses' in context:
                return 'market_metric'
            return 'employment_metric'
            
        # GROWTH METRICS - But be specific about what's growing
        growth_patterns = [
            'growth', 'increase', 'expansion', 'scaling', 'grew', 'risen'
        ]
        if any(pattern in context for pattern in growth_patterns):
            # Check what's growing
            if any(fin in context for fin in ['revenue', 'profit', 'earnings']):
                return 'financial_metric'
            elif any(skill in context for skill in ['skill', 'literacy', 'training']):
                return 'training_metric'
            else:
                return 'growth_metric'
            
        # AI SPECIFIC
        if any(word in context for word in ['ai', 'artificial intelligence', 'genai', 'generative', 'machine learning']):
            # But only if it's not better classified above
            if current_type == 'general_rate':
                return 'ai_metric'
            
        # Return original if no match
        return current_type
        
    def _is_meaningful_context(self, context):
        """Check if a context contains meaningful information"""
        meaningful_keywords = ['no change', 'zero', 'unchanged', 'baseline', 'none', 'not', 
                              'without', 'decrease', 'growth', 'increase', 'reduction']
        return any(keyword in context.lower() for keyword in meaningful_keywords)
        
    def extract_sector(self, context):
        """Extract sector information from context"""
        sectors = {
            'financial services': ['financial', 'banking', 'finance', 'fintech', 'insurance'],
            'healthcare': ['health', 'medical', 'pharma', 'clinical', 'hospital'],
            'retail': ['retail', 'commerce', 'shopping', 'consumer', 'store'],
            'manufacturing': ['manufacturing', 'industrial', 'production', 'factory'],
            'technology': ['technology', 'tech', 'software', 'IT', 'digital'],
            'education': ['education', 'academic', 'university', 'school', 'learning'],
            'government': ['government', 'public sector', 'federal', 'municipal']
        }
        
        for sector, keywords in sectors.items():
            if any(keyword in context for keyword in keywords):
                return sector
                
        return ''
        
    def generate_csv_reports(self):
        """Generate the three CSV files"""
        import os
        output_dir = f"Source Data Cleanup Analysis/Source_{self.source_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Records to keep
        if self.records_to_keep:
            keep_df = pd.DataFrame(self.records_to_keep)
            keep_df.to_csv(f"{output_dir}/records_to_keep.csv", index=False)
            print(f"\nRecords to keep: {len(self.records_to_keep)}")
            
        # Records to remove
        if self.records_to_remove:
            remove_df = pd.DataFrame(self.records_to_remove)
            remove_df.to_csv(f"{output_dir}/records_to_remove.csv", index=False)
            print(f"Records to remove: {len(self.records_to_remove)}")
            
        # Records to modify
        if self.records_to_modify:
            modify_df = pd.DataFrame(self.records_to_modify)
            modify_df.to_csv(f"{output_dir}/records_to_modify.csv", index=False)
            print(f"Records to modify: {len(self.records_to_modify)}")
            
        # Initial analysis (all records with proposed actions)
        all_records = []
        
        for record in self.records_to_keep:
            record['proposed_action'] = 'KEEP'
            all_records.append(record)
            
        for record in self.records_to_remove:
            record['proposed_action'] = 'REMOVE'
            all_records.append(record)
            
        for record in self.records_to_modify:
            record['proposed_action'] = 'MODIFY'
            flat_record = {
                'original_id': record['original_id'],
                'value': record['value'],
                'unit': record['unit'],
                'year': record['year'],
                'metric_type': record['current_metric_type'],
                'context_preview': record['context_preview'],
                'reason': record['reason'],
                'confidence': record['confidence'],
                'proposed_action': 'MODIFY'
            }
            all_records.append(flat_record)
            
        # Sort by original ID
        if all_records:
            all_records_df = pd.DataFrame(all_records).sort_values('original_id')
            all_records_df.to_csv(f"{output_dir}/initial_analysis.csv", index=False)
        
    def generate_summary(self):
        """Generate summary text file"""
        output_dir = f"Source Data Cleanup Analysis/Source_{self.source_id}"
        
        summary = f"""SOURCE {self.source_id} CLEANUP ANALYSIS SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILE: {self.source_name}
Original Records: {len(self.source_df)}

PROPOSED ACTIONS:
- Records to KEEP: {len(self.records_to_keep)}
- Records to REMOVE: {len(self.records_to_remove)}
- Records to MODIFY: {len(self.records_to_modify)}

DUPLICATE HANDLING:
- Duplicate groups identified: {len(self.duplicate_groups)}
- First occurrences kept: {len(self.duplicate_groups)}
- Subsequent duplicates removed: {sum(len(info['duplicates']) for info in self.duplicate_groups.values())}

REMOVAL REASONS:
"""
        # Count removal reasons
        removal_reasons = {}
        for record in self.records_to_remove:
            reason = record['reason']
            removal_reasons[reason] = removal_reasons.get(reason, 0) + 1
            
        for reason, count in sorted(removal_reasons.items(), key=lambda x: x[1], reverse=True):
            summary += f"  - {reason}: {count} records\n"
            
        summary += "\nMODIFICATION SUMMARY:\n"
        
        # Count modification types
        mod_types = {}
        for record in self.records_to_modify:
            if 'current_metric_type' in record and 'new_metric_type' in record:
                change = f"{record['current_metric_type']} -> {record['new_metric_type']}"
                mod_types[change] = mod_types.get(change, 0) + 1
            
        for change, count in sorted(mod_types.items(), key=lambda x: x[1], reverse=True):
            summary += f"  - {change}: {count} records\n"
            
        # Count sector enrichments
        sector_count = sum(1 for r in self.records_to_modify if r.get('sector'))
        if sector_count > 0:
            summary += f"\nMETADATA ENRICHMENT:\n- Records with sector identified: {sector_count}\n"
            
        summary += f"""
CONFIDENCE DISTRIBUTION:
- High confidence (>0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] > 0.85)} records
- Medium confidence (0.70-0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if 0.70 <= r['confidence'] <= 0.85)} records  
- Low confidence (<0.70): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] < 0.70)} records

DATA QUALITY IMPROVEMENT:
- Proper duplicate handling ensures first occurrences are preserved
- Context-based metric reclassification improves data categorization
- Unit validation catches common extraction errors
- Confidence scores provide transparency for review

NEXT STEPS:
1. Review the CSV files to validate proposed actions
2. Verify that important metrics are preserved
3. Check metric reclassifications and unit corrections
4. Approve or modify the cleanup plan before execution
"""
        
        with open(f"{output_dir}/cleanup_summary.txt", 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"\nSummary saved to: {output_dir}/cleanup_summary.txt")
        

if __name__ == "__main__":
    # Example usage - replace with actual source ID
    import sys
    
    if len(sys.argv) > 1:
        source_id = int(sys.argv[1])
        if len(sys.argv) > 2:
            previous_file = sys.argv[2]
        else:
            previous_file = 'ai_metrics.csv'
            
        analyzer = SourceCleanupAnalyzer(source_id, previous_file)
        analyzer.analyze()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nFiles created in 'Source Data Cleanup Analysis/Source_{source_id}/':")
        print("  - initial_analysis.csv (all records with proposed actions)")
        print("  - records_to_keep.csv")
        print("  - records_to_remove.csv") 
        print("  - records_to_modify.csv")
        print("  - cleanup_summary.txt")
        print("\nPlease review these files before proceeding with cleanup.")
    else:
        print("Usage: python source_cleanup_template.py <source_id> [previous_cleaned_file]")
        print("Example: python source_cleanup_template.py 3 ai_metrics_cleaned_source1_2_7.csv")