"""
Debug the CSV writing issue to find the root cause
"""
import csv
import pandas as pd
import os

print("=== DEBUGGING CSV ISSUE ===\n")

# Test 1: Basic CSV writing
print("Test 1: Basic CSV writing")
filename = "debug_test1.csv"

headers = ['col1', 'col2', 'col3']
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()

print(f"After writeheader(), file contents:")
with open(filename, 'rb') as f:  # Read as binary to see exact bytes
    content = f.read()
    print(f"Bytes: {content}")
    print(f"Decoded: {content.decode('utf-8')}")

# Now append data
data = {'col1': 'value1', 'col2': 'value2', 'col3': 'value3'}
with open(filename, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writerow(data)

print(f"\nAfter appending data:")
with open(filename, 'rb') as f:
    content = f.read()
    print(f"Bytes: {content}")
    print(f"Decoded: {content.decode('utf-8')}")

print("\nWhat pandas sees:")
try:
    df = pd.read_csv(filename)
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    print(f"Data:\n{df}")
except Exception as e:
    print(f"Error: {e}")

os.remove(filename)

print("\n" + "="*50 + "\n")

# Test 2: Check if the issue is with our QualityTracker approach
print("Test 2: Testing the QualityTracker approach")

from quality_tracker import QualityTracker

# Create a minimal test
filename2 = "debug_test2.csv"
tracker = QualityTracker(filename2)

print(f"\nAfter initialization, file exists: {os.path.exists(filename2)}")
print(f"File size: {os.path.getsize(filename2)} bytes")

with open(filename2, 'rb') as f:
    content = f.read()
    print(f"Initial content bytes: {content}")
    print(f"Initial content decoded: {content.decode('utf-8')}")

# Try to read with pandas immediately
print("\nReading empty file with pandas:")
try:
    df = pd.read_csv(filename2)
    print(f"Success! Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Now add a record
analysis_results = {
    'total_records': 100,
    'kept_records': 70,
    'removed_records': 20,
    'modified_records': 10,
    'duplicate_groups': 5,
    'duplicates_removed': 15,
    'top_removal_reason': 'Test',
    'top_removal_count': 15,
    'schema_version': '1.1'
}

record = tracker.record_source_analysis(1, 'Test Source', analysis_results)

print(f"\nAfter adding record:")
with open(filename2, 'rb') as f:
    content = f.read()
    lines = content.decode('utf-8').split('\n')
    for i, line in enumerate(lines[:5]):  # First 5 lines
        print(f"Line {i}: {repr(line)}")

print("\nReading with pandas after adding data:")
try:
    df = pd.read_csv(filename2)
    print(f"Columns: {df.columns.tolist()[:5]}...")  # First 5 columns
    print(f"Shape: {df.shape}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

os.remove(filename2)

print("\n=== DIAGNOSIS ===")
print("The issue appears to be that pandas cannot read a CSV file with only headers.")
print("When we try to read it immediately after creation, it fails.")
print("This is causing our tests to fail when checking the initial state.")