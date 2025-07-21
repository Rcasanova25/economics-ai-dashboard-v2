"""
Investment Trends Page

Analyzes AI investment patterns across time, regions, and sectors.
Key economic insights for understanding capital flows into AI.
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime


def create_investment_layout(db):
    """Create the investment analysis page with REAL data."""
    
    # Get REAL investment metrics from database
    investment_metrics = db.get_metrics_by_type('investment')
    ai_investment_metrics = db.get_metrics_by_type('ai_investment')
    dollar_metrics = db.get_metrics_by_type('dollar_amounts')
    
    # Combine all investment-related metrics
    all_investment_metrics = investment_metrics + ai_investment_metrics + dollar_metrics
    
    # Calculate real statistics
    if all_investment_metrics:
        # Total investment (convert to billions)
        total_investment = sum(
            m['value'] / 1000 if m['unit'] == 'millions_usd' else m['value']
            for m in all_investment_metrics 
            if m['unit'] in ['millions_usd', 'billions_usd']
        )
        
        # Get latest year data
        latest_year = max(m['year'] for m in all_investment_metrics if m['year'] <= 2025)
        latest_metrics = [m for m in all_investment_metrics if m['year'] == latest_year]
        
        # Count unique sources
        unique_sources = len(set(m.get('source', 'Unknown') for m in all_investment_metrics))
    else:
        total_investment = 0
        latest_year = 2024
        latest_metrics = []
        unique_sources = 0
    
    # Calculate YoY growth if we have data
    yoy_growth = "N/A"
    if latest_year > 2020:
        current_year_total = sum(
            m['value'] for m in all_investment_metrics 
            if m['year'] == latest_year and m['unit'] in ['millions_usd', 'billions_usd']
        )
        previous_year_total = sum(
            m['value'] for m in all_investment_metrics 
            if m['year'] == latest_year - 1 and m['unit'] in ['millions_usd', 'billions_usd']
        )
        if previous_year_total > 0:
            yoy_growth = f"{((current_year_total - previous_year_total) / previous_year_total * 100):.1f}%"
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2("AI Investment Analysis", className="mb-4"),
                html.P(
                    f"Analyzing {len(all_investment_metrics)} investment data points from {unique_sources} sources",
                    className="lead text-muted"
                )
            ])
        ]),
        
        # Key Investment Metrics - REAL DATA
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Investment Found", className="card-title"),
                        html.H2(
                            f"${total_investment:.1f}B" if total_investment > 0 else "No Data",
                            className="text-primary"
                        ),
                        html.P(f"From {len(all_investment_metrics)} metrics", className="text-muted")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("YoY Growth", className="card-title"),
                        html.H2(yoy_growth, className="text-success"),
                        html.P(f"{latest_year-1}-{latest_year}", className="text-muted")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Data Points", className="card-title"),
                        html.H2(str(len(all_investment_metrics)), className="text-info"),
                        html.P("Investment metrics", className="text-muted")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Latest Year", className="card-title"),
                        html.H2(str(latest_year), className="text-warning"),
                        html.P(f"{len(latest_metrics)} metrics", className="text-muted")
                    ])
                ])
            ], md=3),
        ], className="mb-4"),
        
        # Controls
        dbc.Row([
            dbc.Col([
                html.Label("Select Metric Type:"),
                dcc.Dropdown(
                    id='investment-type-dropdown',
                    options=[
                        {'label': 'All Investment Metrics', 'value': 'all'},
                        {'label': 'AI Investment', 'value': 'ai_investment'},
                        {'label': 'General Investment', 'value': 'investment'},
                        {'label': 'Dollar Amounts', 'value': 'dollar_amounts'}
                    ],
                    value='all'
                )
            ], md=4),
            
            dbc.Col([
                html.Label("Time Period:"),
                dcc.RangeSlider(
                    id='investment-year-slider',
                    min=2010,
                    max=2025,
                    value=[2020, 2025],
                    marks={i: str(i) for i in range(2010, 2026, 2)},
                    step=1
                )
            ], md=8)
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Investment Trends Over Time (Real Data)"),
                    dbc.CardBody([
                        dcc.Graph(id="investment-time-series")
                    ])
                ])
            ], md=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Data Sources Distribution"),
                    dbc.CardBody([
                        dcc.Graph(id="investment-by-source")
                    ])
                ])
            ], md=4)
        ], className="mb-4"),
        
        # Data Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Raw Investment Data"),
                    dbc.CardBody([
                        html.Div(id="investment-data-table")
                    ])
                ])
            ])
        ])
    ], fluid=True)


# Store the database reference
_db_instance = None

def set_db_instance(db):
    """Set the database instance for callbacks."""
    global _db_instance
    _db_instance = db


# Callbacks for investment page
@callback(
    Output("investment-time-series", "figure"),
    [Input("investment-type-dropdown", "value"),
     Input("investment-year-slider", "value")]
)
def update_investment_time_series(metric_type, year_range):
    """Update investment time series chart with REAL DATA."""
    
    if not _db_instance:
        return go.Figure().add_annotation(text="No database connection")
    
    # Get REAL metrics based on selection
    if metric_type == 'all':
        metrics = []
        metrics.extend(_db_instance.get_metrics_by_type('investment'))
        metrics.extend(_db_instance.get_metrics_by_type('ai_investment'))
        metrics.extend(_db_instance.get_metrics_by_type('dollar_amounts'))
    else:
        metrics = _db_instance.get_metrics_by_type(metric_type)
    
    # Filter for investment-related metrics and year range
    investment_metrics = [
        m for m in metrics 
        if m['unit'] in ['millions_usd', 'billions_usd', 'percentage'] and
        year_range[0] <= m['year'] <= year_range[1]
    ]
    
    if not investment_metrics:
        fig = go.Figure()
        fig.add_annotation(
            text="No investment data found for selected criteria",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(investment_metrics)
    
    # Normalize values to billions USD
    df['value_billions'] = df.apply(
        lambda row: row['value'] / 1000 if row['unit'] == 'millions_usd' else row['value'],
        axis=1
    )
    
    # Group by year and sum
    yearly_data = df.groupby('year')['value_billions'].agg(['sum', 'count']).reset_index()
    
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=yearly_data['year'],
        y=yearly_data['sum'],
        mode='lines+markers',
        name='Total Investment',
        line=dict(width=3, color='#1f77b4'),
        marker=dict(size=8),
        text=[f"{count} data points" for count in yearly_data['count']],
        hovertemplate='Year: %{x}<br>Investment: $%{y:.1f}B<br>%{text}<extra></extra>'
    ))
    
    # Add trend line if we have enough data
    if len(yearly_data) > 2:
        z = np.polyfit(yearly_data['year'], yearly_data['sum'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=yearly_data['year'],
            y=p(yearly_data['year']),
            mode='lines',
            name='Trend',
            line=dict(width=2, dash='dash', color='red')
        ))
    
    fig.update_layout(
        title=f"AI Investment Over Time ({len(investment_metrics)} data points)",
        xaxis_title="Year",
        yaxis_title="Investment (Billions USD)",
        hovermode='x unified',
        template="plotly_white",
        showlegend=True
    )
    
    return fig


@callback(
    Output("investment-by-source", "figure"),
    Input("investment-year-slider", "value")
)
def update_investment_by_source(year_range):
    """Show distribution of data sources."""
    
    if not _db_instance:
        return go.Figure()
    
    # Get all investment metrics
    all_metrics = []
    all_metrics.extend(_db_instance.get_metrics_by_type('investment'))
    all_metrics.extend(_db_instance.get_metrics_by_type('ai_investment'))
    all_metrics.extend(_db_instance.get_metrics_by_type('dollar_amounts'))
    
    # Filter by year
    filtered_metrics = [
        m for m in all_metrics
        if year_range[0] <= m['year'] <= year_range[1]
    ]
    
    # Count by source
    source_counts = {}
    for metric in filtered_metrics:
        source = metric.get('source', 'Unknown')
        # Clean up source names
        if 'stanford' in source.lower():
            source = 'Stanford HAI'
        elif 'mckinsey' in source.lower():
            source = 'McKinsey'
        elif 'oecd' in source.lower():
            source = 'OECD'
        elif 'goldman' in source.lower():
            source = 'Goldman Sachs'
        
        source_counts[source] = source_counts.get(source, 0) + 1
    
    if not source_counts:
        fig = go.Figure()
        fig.add_annotation(text="No data for selected period")
        return fig
    
    # Create pie chart
    df = pd.DataFrame(list(source_counts.items()), columns=['Source', 'Count'])
    df = df.sort_values('Count', ascending=False)
    
    fig = px.pie(
        df,
        values='Count',
        names='Source',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value} metrics<br>%{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title=f"Data Sources ({sum(source_counts.values())} total metrics)",
        showlegend=True,
        template="plotly_white"
    )
    
    return fig


@callback(
    Output("investment-data-table", "children"),
    [Input("investment-type-dropdown", "value"),
     Input("investment-year-slider", "value")]
)
def update_investment_table(metric_type, year_range):
    """Show raw investment data in a table."""
    
    if not _db_instance:
        return html.P("No database connection")
    
    # Get metrics
    if metric_type == 'all':
        metrics = []
        metrics.extend(_db_instance.get_metrics_by_type('investment'))
        metrics.extend(_db_instance.get_metrics_by_type('ai_investment'))
        metrics.extend(_db_instance.get_metrics_by_type('dollar_amounts'))
    else:
        metrics = _db_instance.get_metrics_by_type(metric_type)
    
    # Filter
    filtered = [
        m for m in metrics
        if year_range[0] <= m['year'] <= year_range[1] and
        m['unit'] in ['millions_usd', 'billions_usd']
    ]
    
    # Sort by year descending
    filtered.sort(key=lambda x: (x['year'], x['value']), reverse=True)
    
    # Take top 20 for display
    display_metrics = filtered[:20]
    
    if not display_metrics:
        return html.P("No investment data found for selected criteria", className="text-muted")
    
    rows = []
    for metric in display_metrics:
        # Format value
        if metric['unit'] == 'millions_usd':
            value_str = f"${metric['value']:,.0f}M"
        else:
            value_str = f"${metric['value']:,.1f}B"
        
        rows.append(
            html.Tr([
                html.Td(str(metric['year'])),
                html.Td(metric.get('source', 'Unknown')[:30]),
                html.Td(metric.get('country', 'Global')),
                html.Td(value_str),
                html.Td(metric.get('context', '')[:100] + '...' if metric.get('context') else '')
            ])
        )
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Year"),
                html.Th("Source"),
                html.Th("Region"),
                html.Th("Value"),
                html.Th("Context")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
    
    return [
        html.P(f"Showing top 20 of {len(filtered)} investment metrics", className="text-muted mb-2"),
        table
    ]


# Import numpy for trend line
import numpy as np