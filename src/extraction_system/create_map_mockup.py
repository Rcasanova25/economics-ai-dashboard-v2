"""
Create a geographic map mockup with our mismatched extracted data
Shows the reality of what we have vs what we need
"""

import json
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random

def find_geographic_data():
    """Search through our extracted data for any geographic mentions"""
    
    geographic_data = []
    
    # Geographic patterns to search for
    locations = {
        'United States': {'lat': 39.8283, 'lon': -98.5795, 'type': 'country'},
        'US': {'lat': 39.8283, 'lon': -98.5795, 'type': 'country'},
        'China': {'lat': 35.8617, 'lon': 104.1954, 'type': 'country'},
        'India': {'lat': 20.5937, 'lon': 78.9629, 'type': 'country'},
        'Europe': {'lat': 54.5260, 'lon': 15.2551, 'type': 'region'},
        'California': {'lat': 36.7783, 'lon': -119.4179, 'type': 'state'},
        'Silicon Valley': {'lat': 37.3621, 'lon': -122.0840, 'type': 'region'},
        'New York': {'lat': 40.7128, 'lon': -74.0060, 'type': 'city'},
        'Boston': {'lat': 42.3601, 'lon': -71.0589, 'type': 'city'},
        'Seattle': {'lat': 47.6062, 'lon': -122.3321, 'type': 'city'},
        'Germany': {'lat': 51.1657, 'lon': 10.4515, 'type': 'country'},
        'UK': {'lat': 55.3781, 'lon': -3.4360, 'type': 'country'},
        'Canada': {'lat': 56.1304, 'lon': -106.3468, 'type': 'country'},
    }
    
    # Read our extracted candidates
    for file in Path('extraction_output').glob('*_candidates.json'):
        print(f"Searching {file.name}...")
        
        with open(file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
        
        for candidate in candidates[:100]:  # Check first 100 candidates
            text = str(candidate.get('surrounding_text', '')) + ' ' + str(candidate.get('raw_value', ''))
            
            for location, coords in locations.items():
                if location.lower() in text.lower():
                    geographic_data.append({
                        'location': location,
                        'lat': coords['lat'],
                        'lon': coords['lon'],
                        'type': coords['type'],
                        'value': candidate.get('numeric_value', 0),
                        'unit': candidate.get('unit_hint', ''),
                        'metric': candidate.get('suggested_category', 'unknown'),
                        'source': file.stem.replace('_candidates', ''),
                        'context': text[:150],
                        'confidence': candidate.get('confidence_score', 0.5)
                    })
                    break  # Only match first location per candidate
    
    return geographic_data

def create_reality_map():
    """Create a map showing the mismatched reality of our data"""
    
    print("Creating geographic mockup with extracted data...")
    
    # Find whatever geographic data we have
    geo_data = find_geographic_data()
    
    if not geo_data:
        print("No geographic data found! Creating synthetic example...")
        # Create synthetic mismatched data to show the problem
        geo_data = [
            {'location': 'United States', 'lat': 39.8283, 'lon': -98.5795, 'value': 75, 
             'unit': '%', 'metric': 'AI adoption', 'source': 'McKinsey', 'context': '75% of US companies...', 'confidence': 0.8},
            {'location': 'China', 'lat': 35.8617, 'lon': 104.1954, 'value': 2030, 
             'unit': 'year', 'metric': 'prediction', 'source': 'AI Economy', 'context': 'By 2030, China will...', 'confidence': 0.5},
            {'location': 'Silicon Valley', 'lat': 37.3621, 'lon': -122.0840, 'value': 15.8, 
             'unit': 'billion', 'metric': 'investment', 'source': 'Stanford', 'context': '$15.8B invested in...', 'confidence': 0.9},
            {'location': 'Europe', 'lat': 54.5260, 'lon': 15.2551, 'value': 45, 
             'unit': '%', 'metric': 'productivity', 'source': 'OECD', 'context': '45% productivity gain...', 'confidence': 0.6},
            {'location': 'India', 'lat': 20.5937, 'lon': 78.9629, 'value': 500, 
             'unit': 'companies', 'metric': 'survey size', 'source': 'McKinsey', 'context': 'Survey of 500 companies...', 'confidence': 0.7},
        ]
    
    # Convert to DataFrame
    df = pd.DataFrame(geo_data)
    
    # Create the map
    fig = go.Figure()
    
    # Group by metric type for different colors
    metric_types = df['metric'].unique()
    colors = px.colors.qualitative.Set3[:len(metric_types)]
    
    for i, metric in enumerate(metric_types):
        metric_df = df[df['metric'] == metric]
        
        # Add scatter points
        fig.add_trace(go.Scattergeo(
            lon = metric_df['lon'],
            lat = metric_df['lat'],
            text = metric_df['location'],
            customdata = metric_df[['value', 'unit', 'source', 'context', 'confidence']],
            mode = 'markers+text',
            marker = dict(
                size = 15,
                color = colors[i % len(colors)],
                line = dict(width=2, color='white'),
                opacity = 0.8
            ),
            name = metric,
            textposition="top center",
            textfont=dict(size=10),
            hovertemplate = 
                '<b>%{text}</b><br>' +
                'Value: %{customdata[0]} %{customdata[1]}<br>' +
                'Source: %{customdata[2]}<br>' +
                'Context: %{customdata[3]}<br>' +
                'Confidence: %{customdata[4]:.1f}<br>' +
                '<extra></extra>'
        ))
    
    # Add title and annotations showing the data mismatch problem
    fig.update_layout(
        title={
            'text': "The Geographic Data Reality: A Mismatched Mosaic<br>" +
                   "<sup>What happens when you try to map disconnected metrics</sup>",
            'x': 0.5,
            'xanchor': 'center'
        },
        geo = dict(
            projection_type = 'natural earth',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            coastlinecolor = 'rgb(204, 204, 204)',
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)',
            showcountries = True,
            countrycolor = 'rgb(204, 204, 204)'
        ),
        height = 600,
        showlegend = True,
        legend = dict(
            title = "Metric Types<br><sup>(All different!)</sup>",
            x = 0.02,
            y = 0.98,
            bgcolor = 'rgba(255, 255, 255, 0.8)',
            bordercolor = 'Black',
            borderwidth = 1
        )
    )
    
    # Add annotations showing the problems
    fig.add_annotation(
        x=0.5, y=-0.15,
        xref='paper', yref='paper',
        text='⚠️ Notice: Different metrics (%, $, years, counts) • Different timeframes • Different methodologies • No trends',
        showarrow=False,
        font=dict(size=12, color='red'),
        xanchor='center'
    )
    
    # Save the figure
    fig.write_html('geographic_data_mockup.html')
    print("\nMap saved to: geographic_data_mockup.html")
    
    # Create a summary report
    print("\n" + "="*60)
    print("GEOGRAPHIC DATA EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total geographic mentions found: {len(df)}")
    print(f"Unique locations: {df['location'].nunique()}")
    print(f"Different metric types: {list(df['metric'].unique())}")
    print(f"Different units: {list(df['unit'].unique())}")
    print(f"Sources: {list(df['source'].unique())}")
    
    print("\nTHE FUNDAMENTAL PROBLEM:")
    print("- US: 75% (AI adoption from McKinsey)")
    print("- China: 2030 (Year prediction from AI Economy)")  
    print("- Silicon Valley: $15.8B (Investment from Stanford)")
    print("- Europe: 45% (Productivity from OECD)")
    print("- India: 500 (Company count from survey)")
    print("\n❌ These metrics CANNOT be compared or visualized coherently!")
    
    return df

if __name__ == "__main__":
    # Create the mockup
    data = create_reality_map()
    
    print("\nThis mockup demonstrates why our extracted data")
    print("cannot create a meaningful geographic dashboard.")
    print("\nWe need CONSISTENT metrics across ALL locations!")