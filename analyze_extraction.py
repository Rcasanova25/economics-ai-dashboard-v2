"""Analyze extraction results"""
import json
import os
from pathlib import Path

extractions_dir = Path("data/processed/extractions")
total_metrics = 0
total_stats = 0

print(f"{'PDF File':<50} | {'Metrics':>8} | {'Statistics':>10}")
print("-" * 75)

for json_file in sorted(extractions_dir.glob("*.json")):
    with open(json_file) as f:
        data = json.load(f)
    
    metrics_count = len(data.get('metrics', []))
    stats_count = sum(len(v) for v in data.get('statistics', {}).values())
    
    total_metrics += metrics_count
    total_stats += stats_count
    
    pdf_name = json_file.stem.replace('_extracted', '')[:45]
    print(f"{pdf_name:<50} | {metrics_count:>8} | {stats_count:>10}")

print("-" * 75)
print(f"{'TOTALS':<50} | {total_metrics:>8} | {total_stats:>10}")
print(f"\nTotal data points: {total_metrics + total_stats:,}")