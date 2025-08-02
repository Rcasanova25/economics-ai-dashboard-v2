"""
ICT AI Adoption Dashboard
Version: 1.0
Date: January 24, 2025

An honest dashboard showing what we actually have:
AI adoption rates and implementation patterns in the ICT sector.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


class ICTAdoptionDashboard:
    """Create visualizations for ICT AI adoption data"""
    
    def __init__(self, cleaned_csv: str):
        self.csv_path = Path(cleaned_csv)
        self.output_dir = Path("dashboard_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
        # Load and filter data
        self.load_ict_data(cleaned_csv)
        
    def load_ict_data(self, csv_path: str):
        """Load and prepare ICT data"""
        print("Loading ICT sector data...")
        df = pd.read_csv(csv_path)
        
        # Filter to ICT
        self.ict_df = df[df['sector'] == 'information_communication_technology'].copy()
        print(f"Found {len(self.ict_df)} ICT metrics")
        
        # Separate by type
        self.adoption_rates = self.ict_df[
            (self.ict_df['metric_type'] == 'ai_adoption_rate') & 
            (self.ict_df['unit'] == 'percentage')
        ].copy()
        
        self.implementation_counts = self.ict_df[
            (self.ict_df['metric_type'] == 'ai_implementation_count')
        ].copy()
        
        self.investment_data = self.ict_df[
            (self.ict_df['metric_type'] == 'ai_investment_amount') & 
            (self.ict_df['unit'] == 'millions_usd')
        ].copy()
        
        print(f"- Adoption rates: {len(self.adoption_rates)}")
        print(f"- Implementation counts: {len(self.implementation_counts)}")
        print(f"- Investment data: {len(self.investment_data)}")
    
    def create_adoption_overview(self):
        """Create main adoption rate visualization"""
        if len(self.adoption_rates) == 0:
            print("No adoption rate data to visualize")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('ICT Sector AI Adoption Analysis', fontsize=16, y=0.98)
        
        # 1. Distribution of adoption rates
        ax1 = axes[0, 0]
        adoption_values = self.adoption_rates['value'].values
        ax1.hist(adoption_values, bins=20, edgecolor='black', alpha=0.7)
        ax1.axvline(adoption_values.mean(), color='red', linestyle='--', 
                   label=f'Mean: {adoption_values.mean():.1f}%')
        ax1.axvline(np.median(adoption_values), color='green', linestyle='--',
                   label=f'Median: {np.median(adoption_values):.1f}%')
        ax1.set_xlabel('Adoption Rate (%)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distribution of AI Adoption Rates in ICT')
        ax1.legend()
        
        # 2. Adoption by confidence level
        ax2 = axes[0, 1]
        confidence_bins = pd.cut(self.adoption_rates['confidence'], 
                                bins=[0, 0.5, 0.7, 0.9, 1.0],
                                labels=['Low', 'Medium', 'High', 'Very High'])
        
        confidence_data = self.adoption_rates.groupby(confidence_bins)['value'].agg(['mean', 'count'])
        confidence_data.plot(kind='bar', y='mean', ax=ax2, legend=False)
        ax2.set_xlabel('Confidence Level')
        ax2.set_ylabel('Average Adoption Rate (%)')
        ax2.set_title('Adoption Rates by Data Confidence')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
        
        # Add count labels
        for i, (idx, row) in enumerate(confidence_data.iterrows()):
            ax2.text(i, row['mean'] + 1, f'n={int(row["count"])}', 
                    ha='center', va='bottom', fontsize=10)
        
        # 3. Top adoption contexts
        ax3 = axes[1, 0]
        # Extract key terms from high adoption contexts
        high_adoption = self.adoption_rates[self.adoption_rates['value'] > 50].copy()
        
        if len(high_adoption) > 0:
            # Categorize contexts
            categories = self.categorize_adoption_contexts(high_adoption)
            category_counts = pd.Series(categories).value_counts()
            
            category_counts.plot(kind='barh', ax=ax3)
            ax3.set_xlabel('Number of Mentions')
            ax3.set_title('High Adoption (>50%) Context Categories')
        else:
            ax3.text(0.5, 0.5, 'No high adoption rates found', 
                    ha='center', va='center', transform=ax3.transAxes)
        
        # 4. Summary statistics
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        # Calculate statistics
        stats_text = f"""
        ICT AI ADOPTION SUMMARY
        
        Total Metrics: {len(self.ict_df)}
        Adoption Rate Metrics: {len(self.adoption_rates)}
        
        ADOPTION STATISTICS:
        • Range: {adoption_values.min():.1f}% - {adoption_values.max():.1f}%
        • Mean: {adoption_values.mean():.1f}%
        • Median: {np.median(adoption_values):.1f}%
        • Std Dev: {adoption_values.std():.1f}%
        
        DATA QUALITY:
        • High Confidence: {(self.adoption_rates['confidence'] > 0.7).sum()}
        • Medium Confidence: {((self.adoption_rates['confidence'] >= 0.5) & (self.adoption_rates['confidence'] <= 0.7)).sum()}
        • Low Confidence: {(self.adoption_rates['confidence'] < 0.5).sum()}
        
        Note: This represents extracted metrics from
        {self.ict_df['source_pdf'].nunique()} different PDF sources
        """
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, 
                fontsize=11, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_dir / 'ict_adoption_overview.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved adoption overview to: {output_path}")
        
        return fig
    
    def categorize_adoption_contexts(self, df):
        """Categorize adoption contexts into themes"""
        categories = []
        
        for _, row in df.iterrows():
            context = str(row['context']).lower()
            
            if any(term in context for term in ['enterprise', 'large company', 'corporation']):
                categories.append('Enterprise')
            elif any(term in context for term in ['sme', 'small business', 'small and medium']):
                categories.append('SME')
            elif any(term in context for term in ['cloud', 'saas', 'infrastructure']):
                categories.append('Cloud/Infrastructure')
            elif any(term in context for term in ['telecom', 'mobile', '5g', 'network']):
                categories.append('Telecom/Network')
            elif any(term in context for term in ['software', 'application', 'develop']):
                categories.append('Software Development')
            elif any(term in context for term in ['security', 'cyber', 'threat']):
                categories.append('Cybersecurity')
            else:
                categories.append('Other')
        
        return categories
    
    def create_implementation_analysis(self):
        """Analyze implementation patterns"""
        if len(self.implementation_counts) == 0:
            print("No implementation data to analyze")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('ICT AI Implementation Patterns', fontsize=14)
        
        # 1. Implementation scale distribution
        ax1 = axes[0]
        impl_values = self.implementation_counts['value'].values
        
        # Log scale for better visualization
        log_values = np.log10(impl_values + 1)  # +1 to handle zeros
        ax1.hist(log_values, bins=30, edgecolor='black', alpha=0.7)
        ax1.set_xlabel('Log10(Implementation Count + 1)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distribution of Implementation Scales')
        
        # 2. Implementation context themes
        ax2 = axes[1]
        impl_categories = self.categorize_implementation_contexts()
        category_counts = pd.Series(impl_categories).value_counts().head(10)
        
        category_counts.plot(kind='barh', ax=ax2)
        ax2.set_xlabel('Number of Mentions')
        ax2.set_title('Top 10 Implementation Themes')
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_dir / 'ict_implementation_analysis.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved implementation analysis to: {output_path}")
        
        return fig
    
    def categorize_implementation_contexts(self):
        """Categorize implementation contexts"""
        categories = []
        
        for _, row in self.implementation_counts.iterrows():
            context = str(row['context']).lower()
            
            if any(term in context for term in ['ml', 'machine learning', 'model']):
                categories.append('Machine Learning')
            elif any(term in context for term in ['automat', 'process', 'workflow']):
                categories.append('Process Automation')
            elif any(term in context for term in ['customer', 'service', 'support']):
                categories.append('Customer Service')
            elif any(term in context for term in ['analytic', 'insight', 'data']):
                categories.append('Analytics/BI')
            elif any(term in context for term in ['security', 'threat', 'fraud']):
                categories.append('Security/Fraud')
            elif any(term in context for term in ['cloud', 'platform', 'infrastructure']):
                categories.append('Cloud Platform')
            elif any(term in context for term in ['develop', 'code', 'software']):
                categories.append('Development Tools')
            elif any(term in context for term in ['network', 'optim', 'performance']):
                categories.append('Network/Performance')
            else:
                categories.append('General AI')
        
        return categories
    
    def create_data_quality_report(self):
        """Create a data quality visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('ICT AI Data Quality Assessment', fontsize=14)
        
        # 1. Metric type distribution
        ax1 = axes[0, 0]
        metric_counts = self.ict_df['metric_type'].value_counts()
        metric_counts.plot(kind='pie', ax=ax1, autopct='%1.1f%%')
        ax1.set_ylabel('')
        ax1.set_title('Distribution of Metric Types')
        
        # 2. Data sources
        ax2 = axes[0, 1]
        source_counts = self.ict_df['source_pdf'].value_counts().head(10)
        source_counts.plot(kind='barh', ax=ax2)
        ax2.set_xlabel('Number of Metrics')
        ax2.set_title('Top 10 Source Documents')
        
        # 3. Confidence distribution
        ax3 = axes[1, 0]
        self.ict_df['confidence'].hist(bins=20, ax=ax3, edgecolor='black', alpha=0.7)
        ax3.set_xlabel('Confidence Score')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Confidence Score Distribution')
        ax3.axvline(0.7, color='red', linestyle='--', label='High Confidence Threshold')
        ax3.legend()
        
        # 4. Unit types
        ax4 = axes[1, 1]
        unit_counts = self.ict_df['unit'].value_counts()
        unit_counts.plot(kind='bar', ax=ax4)
        ax4.set_xlabel('Unit Type')
        ax4.set_ylabel('Count')
        ax4.set_title('Measurement Units Used')
        ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_dir / 'ict_data_quality.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved data quality report to: {output_path}")
        
        return fig
    
    def create_dashboard_json(self):
        """Create JSON data for web dashboard"""
        dashboard_data = {
            "title": "ICT Sector AI Adoption Dashboard",
            "subtitle": "Analysis of AI adoption patterns in Information & Communication Technology",
            "generated": datetime.now().isoformat(),
            "data_source": "Extracted from 23 PDF documents on AI economics",
            "metrics_summary": {
                "total_ict_metrics": len(self.ict_df),
                "adoption_rates": len(self.adoption_rates),
                "implementation_counts": len(self.implementation_counts),
                "investment_metrics": len(self.investment_data)
            },
            "adoption_statistics": {},
            "key_insights": [],
            "data_quality": {},
            "limitations": [
                "Data extracted from academic and policy papers, not industry reports",
                "Adoption rates may represent different scopes (enterprise vs SME)",
                "Limited temporal data prevents trend analysis",
                "Investment data is sparse (only 19 data points)"
            ]
        }
        
        # Add adoption statistics
        if len(self.adoption_rates) > 0:
            values = self.adoption_rates['value'].values
            dashboard_data["adoption_statistics"] = {
                "min": float(values.min()),
                "max": float(values.max()),
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "std_dev": float(values.std()),
                "quartiles": {
                    "q1": float(np.percentile(values, 25)),
                    "q2": float(np.percentile(values, 50)),
                    "q3": float(np.percentile(values, 75))
                }
            }
        
        # Extract key insights
        high_adoption = self.adoption_rates[self.adoption_rates['value'] > 70]
        for _, row in high_adoption.head(5).iterrows():
            dashboard_data["key_insights"].append({
                "type": "high_adoption",
                "value": float(row['value']),
                "context": str(row['context'])[:200],
                "confidence": float(row['confidence'])
            })
        
        # Data quality metrics
        dashboard_data["data_quality"] = {
            "high_confidence_percentage": float((self.ict_df['confidence'] > 0.7).mean() * 100),
            "sources_count": int(self.ict_df['source_pdf'].nunique()),
            "avg_confidence": float(self.ict_df['confidence'].mean())
        }
        
        # Save
        output_path = self.output_dir / 'dashboard_data.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2)
        
        print(f"Saved dashboard data to: {output_path}")
        
        return dashboard_data
    
    def generate_all_outputs(self):
        """Generate all dashboard outputs"""
        print("\n=== Generating ICT AI Adoption Dashboard ===")
        
        # Create visualizations
        self.create_adoption_overview()
        self.create_implementation_analysis()
        self.create_data_quality_report()
        
        # Create data export
        dashboard_data = self.create_dashboard_json()
        
        # Create summary report
        self.create_markdown_report(dashboard_data)
        
        print(f"\n✓ Dashboard generation complete!")
        print(f"All outputs saved to: {self.output_dir}/")
    
    def create_markdown_report(self, dashboard_data):
        """Create a markdown summary report"""
        md_lines = [
            "# ICT AI Adoption Dashboard Report",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## Executive Summary",
            f"Analysis of {dashboard_data['metrics_summary']['total_ict_metrics']} metrics "
            f"extracted from {dashboard_data['data_quality']['sources_count']} PDF documents "
            "focusing on AI adoption within the ICT sector.",
            "",
            "## Key Findings",
            ""
        ]
        
        if dashboard_data["adoption_statistics"]:
            stats = dashboard_data["adoption_statistics"]
            md_lines.extend([
                f"- **Adoption Rate Range**: {stats['min']:.1f}% to {stats['max']:.1f}%",
                f"- **Average Adoption**: {stats['mean']:.1f}%",
                f"- **Median Adoption**: {stats['median']:.1f}%",
                f"- **Standard Deviation**: {stats['std_dev']:.1f}%",
                ""
            ])
        
        md_lines.extend([
            "## Data Composition",
            f"- Adoption Rate Metrics: {dashboard_data['metrics_summary']['adoption_rates']}",
            f"- Implementation Counts: {dashboard_data['metrics_summary']['implementation_counts']}",
            f"- Investment Metrics: {dashboard_data['metrics_summary']['investment_metrics']}",
            "",
            "## Visualizations Generated",
            "1. `ict_adoption_overview.png` - Main adoption statistics and distribution",
            "2. `ict_implementation_analysis.png` - Implementation patterns analysis",
            "3. `ict_data_quality.png` - Data quality assessment",
            "",
            "## Data Limitations",
            ""
        ])
        
        for limitation in dashboard_data["limitations"]:
            md_lines.append(f"- {limitation}")
        
        md_lines.extend([
            "",
            "## Next Steps",
            "1. Validate findings against industry benchmark reports",
            "2. Acquire more granular financial and productivity data",
            "3. Expand analysis to other sectors with sufficient data",
            "4. Develop interactive web dashboard for stakeholder access",
            "",
            "---",
            "*This dashboard represents what can be reliably extracted and visualized "
            "from the available data sources. It focuses on adoption patterns rather than "
            "economic impact due to data limitations.*"
        ])
        
        output_path = self.output_dir / 'dashboard_report.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        
        print(f"Saved markdown report to: {output_path}")


def main():
    """Main execution"""
    # Find cleaned data
    extraction_dirs = list(Path('.').glob('extraction_output_*'))
    if not extraction_dirs:
        print("No extraction output found!")
        return
    
    latest_dir = sorted(extraction_dirs)[-1]
    cleaned_csv = latest_dir / 'cleaned_data' / 'cleaned_metrics.csv'
    
    if not cleaned_csv.exists():
        print(f"Cleaned data not found: {cleaned_csv}")
        return
    
    # Create dashboard
    dashboard = ICTAdoptionDashboard(str(cleaned_csv))
    dashboard.generate_all_outputs()


if __name__ == "__main__":
    main()