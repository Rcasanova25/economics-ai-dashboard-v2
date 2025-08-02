"""
Create a simple visualization showing why geographic data doesn't work
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))

# Hide axes
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Title
plt.title("The Geographic Data Problem: Why Our Map Doesn't Work", 
          fontsize=20, fontweight='bold', pad=20)

# Draw mock map regions
locations = [
    {"name": "United States", "x": 2, "y": 7, "data": "75%", "desc": "AI adoption\n(McKinsey 2024)"},
    {"name": "China", "x": 7, "y": 6, "data": "2030", "desc": "Year prediction\n(AI Economy report)"},
    {"name": "Silicon Valley", "x": 1, "y": 6.5, "data": "$15.8B", "desc": "VC investment\n(Stanford AI Index)"},
    {"name": "Europe", "x": 5, "y": 8, "data": "45%", "desc": "Productivity gain\n(OECD study)"},
    {"name": "India", "x": 6.5, "y": 5, "data": "500", "desc": "Companies surveyed\n(McKinsey)"},
    {"name": "Boston", "x": 3, "y": 7.5, "data": "3", "desc": "NSF Institutes\n(Government data)"},
]

# Draw locations with mismatched data
for loc in locations:
    # Draw circle for location
    circle = plt.Circle((loc["x"], loc["y"]), 0.5, 
                       fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(circle)
    
    # Add location name
    ax.text(loc["x"], loc["y"]+0.7, loc["name"], 
           ha='center', fontsize=12, fontweight='bold')
    
    # Add data value (big and bold to show mismatch)
    ax.text(loc["x"], loc["y"], loc["data"], 
           ha='center', va='center', fontsize=16, 
           fontweight='bold', color='red')
    
    # Add description
    ax.text(loc["x"], loc["y"]-0.8, loc["desc"], 
           ha='center', va='top', fontsize=9, 
           style='italic', color='gray')

# Add problem annotations
problems = [
    "PROBLEM 1: Different Units\n% vs $ vs Years vs Counts",
    "PROBLEM 2: Different Metrics\nAdoption vs Investment vs Productivity",
    "PROBLEM 3: Different Timeframes\n2024 data vs 2030 predictions",
    "PROBLEM 4: Different Contexts\nSurveys vs Reports vs Predictions"
]

y_pos = 3
for i, problem in enumerate(problems):
    ax.text(1 + i*2.2, y_pos, problem, 
           bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.7),
           fontsize=10, ha='left', va='top')

# Add bottom message
ax.text(5, 0.5, 
       "This is what happens when you try to map disconnected metrics from different PDFs.\n" +
       "You get numbers on a map, but no coherent story or comparable insights.",
       ha='center', fontsize=12, color='darkred', 
       bbox=dict(boxstyle="round,pad=0.8", facecolor="lightyellow", edgecolor="red"))

plt.tight_layout()
plt.savefig('geographic_data_problem.png', dpi=150, bbox_inches='tight')
plt.close()

# Create comparison chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# What we have (left)
ax1.set_title("What We Have", fontsize=16, fontweight='bold')
ax1.axis('off')
have_text = """
Location Data Points:
• US: 75% (adoption rate)
• China: 2030 (year)
• Silicon Valley: $15.8B (investment)
• Europe: 45% (productivity)
• India: 500 (survey size)
• Boston: 3 (institutes)

Different:
✗ Units (%, $, years, counts)
✗ Metrics (adoption, investment, etc)
✗ Timeframes (current vs predictions)
✗ Sources (McKinsey, Stanford, OECD)
✗ Methodologies
"""
ax1.text(0.1, 0.9, have_text, transform=ax1.transAxes, 
         fontsize=12, va='top', family='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffcccc"))

# What we need (right)
ax2.set_title("What We Need for a Map", fontsize=16, fontweight='bold')
ax2.axis('off')
need_text = """
Consistent Geographic Metrics:
• US: 75% AI adoption
• China: 62% AI adoption
• Europe: 45% AI adoption
• India: 38% AI adoption
• Canada: 55% AI adoption
• Japan: 41% AI adoption

All with:
✓ Same metric (AI adoption %)
✓ Same timeframe (2024)
✓ Same methodology
✓ Same source
✓ Comparable values
"""
ax2.text(0.1, 0.9, need_text, transform=ax2.transAxes, 
         fontsize=12, va='top', family='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#ccffcc"))

plt.suptitle("The Geographic Dashboard Reality Check", fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig('map_comparison.png', dpi=150, bbox_inches='tight')

print("Created two visualizations:")
print("1. geographic_data_problem.png - Shows the mismatch on a mock map")
print("2. map_comparison.png - Shows what we have vs what we need")
print("\nThe fundamental issue: We're trying to compare apples, oranges, and timestamps!")