"""
Convert Raw Statistics to Structured Metrics

This script processes the extracted statistics and converts them into 
structured metrics that can be imported into the database.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def classify_statistic(stat: Dict, stat_type: str) -> Dict[str, Any]:
    """Convert a raw statistic into a structured metric."""
    
    # Extract value from the statistic
    value_str = stat.get('value', '')
    context = stat.get('context', '')
    
    # Parse numeric value
    value_match = re.search(r'([-]?\d+\.?\d*)', value_str)
    if not value_match:
        return None
    
    value = float(value_match.group(1))
    
    # Classify based on context
    context_lower = context.lower()
    
    # Determine metric type from context
    if any(word in context_lower for word in ['adoption', 'using ai', 'implemented']):
        metric_type = 'adoption_rate'
    elif any(word in context_lower for word in ['investment', 'funding', 'capital']):
        metric_type = 'investment'
    elif any(word in context_lower for word in ['cost', 'expense', 'spending']):
        metric_type = 'cost'
    elif any(word in context_lower for word in ['revenue', 'sales', 'income']):
        metric_type = 'revenue'
    elif any(word in context_lower for word in ['productivity', 'efficiency']):
        metric_type = 'productivity'
    elif any(word in context_lower for word in ['job', 'employment', 'worker']):
        metric_type = 'employment'
    elif any(word in context_lower for word in ['growth', 'increase', 'grew']):
        metric_type = 'growth_rate'
    elif any(word in context_lower for word in ['energy', 'power', 'mw', 'carbon']):
        metric_type = 'energy'
    else:
        metric_type = stat_type
    
    # Determine unit
    if stat_type == 'percentages' or '%' in value_str:
        unit = 'percentage'
    elif stat_type == 'dollar_amounts':
        if 'billion' in value_str.lower() or 'b' in value_str:
            unit = 'billions_usd'
        elif 'million' in value_str.lower() or 'm' in value_str:
            unit = 'millions_usd'
        else:
            unit = 'usd'
    elif stat_type == 'energy_metrics':
        if 'mw' in context_lower:
            unit = 'megawatts'
        elif 'gw' in context_lower:
            unit = 'gigawatts'
        elif 'kwh' in context_lower:
            unit = 'kilowatt_hours'
        elif 'ton' in context_lower or 'co2' in context_lower:
            unit = 'co2_tons'
        else:
            unit = 'energy_unit'
    else:
        unit = 'number'
    
    # Extract year from context
    year_match = re.search(r'(20\d{2})', context)
    year = int(year_match.group(1)) if year_match else 2025
    
    return {
        'metric_type': metric_type,
        'value': value,
        'unit': unit,
        'context': context[:200],
        'year': year,
        'confidence': 0.8,  # Medium confidence for converted statistics
        'source': 'converted_from_statistics'
    }


def process_extraction_file(file_path: Path) -> Dict[str, Any]:
    """Process a single extraction file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Skip if no statistics
    if 'statistics' not in data:
        return None
    
    pdf_name = data.get('pdf_name', 'unknown')
    existing_metrics = data.get('metrics', [])
    new_metrics = []
    
    # Process each type of statistic
    for stat_type, stat_list in data['statistics'].items():
        if stat_type == 'years':  # Skip year statistics
            continue
            
        # Limit to top 100 statistics per type to avoid overwhelming
        for stat in stat_list[:100]:
            metric = classify_statistic(stat, stat_type)
            if metric:
                metric['pdf_source'] = pdf_name
                new_metrics.append(metric)
    
    return {
        'pdf_name': pdf_name,
        'original_metrics': len(existing_metrics),
        'converted_metrics': len(new_metrics),
        'total_metrics': len(existing_metrics) + len(new_metrics),
        'metrics': existing_metrics + new_metrics
    }


def main():
    """Process all extraction files."""
    
    extractions_dir = Path("data/processed/extractions")
    output_dir = Path("data/processed/converted_metrics")
    output_dir.mkdir(exist_ok=True)
    
    print("Converting raw statistics to structured metrics...\n")
    
    total_original = 0
    total_converted = 0
    all_metrics = []
    
    for json_file in sorted(extractions_dir.glob("*.json")):
        result = process_extraction_file(json_file)
        
        if result:
            print(f"{result['pdf_name'][:50]:<50} | "
                  f"Original: {result['original_metrics']:>4} | "
                  f"Converted: {result['converted_metrics']:>4} | "
                  f"Total: {result['total_metrics']:>5}")
            
            total_original += result['original_metrics']
            total_converted += result['converted_metrics']
            
            # Save individual converted file
            output_file = output_dir / f"{json_file.stem}_converted.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            # Add to all metrics
            all_metrics.extend(result['metrics'])
    
    print("-" * 90)
    print(f"{'TOTALS':<50} | "
          f"Original: {total_original:>4} | "
          f"Converted: {total_converted:>4} | "
          f"Total: {total_original + total_converted:>5}")
    
    # Save all metrics combined
    all_metrics_file = output_dir / f"all_metrics_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(all_metrics_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_metrics': len(all_metrics),
            'extraction_date': datetime.now().isoformat(),
            'metrics': all_metrics
        }, f, indent=2)
    
    print(f"\n✅ Conversion complete!")
    print(f"📊 Combined metrics saved to: {all_metrics_file}")
    print(f"   Total metrics ready for database: {len(all_metrics):,}")
    
    # Show sample metrics
    print("\nSample converted metrics:")
    for i, metric in enumerate(all_metrics[:5]):
        print(f"{i+1}. {metric['metric_type']}: {metric['value']} {metric['unit']} "
              f"(from {metric.get('pdf_source', 'unknown')[:30]})")


if __name__ == "__main__":
    main()