"""
Economics AI Dashboard - Version 2 with Database Connection

This version connects to our SQLite database containing 12,000+ extracted metrics
from authoritative AI economics reports.
"""

import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.operations import MetricsDatabase
from src.dashboard.pages.investment import create_investment_layout, set_db_instance

# Initialize database connection
db = MetricsDatabase()

# Set database instance for investment page callbacks
set_db_instance(db)

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Economics of AI Dashboard - Real Data Edition",
    suppress_callback_exceptions=True
)

# Create navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/", active=True)),
        dbc.NavItem(dbc.NavLink("AI Adoption", href="/adoption")),
        dbc.NavItem(dbc.NavLink("Investment Trends", href="/investment")),
        dbc.NavItem(dbc.NavLink("Sector Analysis", href="/sectors")),
        dbc.NavItem(dbc.NavLink("Data Sources", href="/sources")),
    ],
    brand="Economics of AI Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)

# Get summary statistics for the overview
summary_stats = db.get_summary_stats()

# Main layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Overview page layout
def create_overview_layout():
    """Create the main overview page."""
    
    # Get latest metrics for key indicators
    latest_adoption = db.get_latest_value('adoption_rate', 'United States')
    latest_investment = db.get_latest_value('ai_investment', 'Global')
    latest_productivity = db.get_latest_value('productivity', 'Global')
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("AI Economics Dashboard", className="text-center mb-4"),
                html.P(
                    f"Analyzing {summary_stats['total_metrics']:,} economic metrics from {summary_stats['unique_indicators']} indicators",
                    className="text-center text-muted lead"
                )
            ])
        ]),
        
        # Key Metrics Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("AI Adoption Rate", className="card-title"),
                        html.H2(
                            f"{latest_adoption['value']:.1f}%" if latest_adoption else "N/A",
                            className="text-primary"
                        ),
                        html.P(
                            f"United States ({latest_adoption['year']})" if latest_adoption else "No data",
                            className="text-muted"
                        )
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Total Metrics", className="card-title"),
                        html.H2(f"{summary_stats['total_metrics']:,}", className="text-success"),
                        html.P(f"From {summary_stats['unique_countries']} countries", className="text-muted")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Year Range", className="card-title"),
                        html.H2(
                            f"{summary_stats['year_range'][0]}-{summary_stats['year_range'][1]}",
                            className="text-info"
                        ),
                        html.P("Data coverage", className="text-muted")
                    ])
                ])
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Confidence", className="card-title"),
                        html.H2(f"{summary_stats['avg_confidence']:.0%}", className="text-warning"),
                        html.P("Average data confidence", className="text-muted")
                    ])
                ])
            ], md=3),
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Metrics by Type"),
                    dbc.CardBody([
                        dcc.Graph(id="metrics-by-type-chart")
                    ])
                ])
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Top Economic Indicators"),
                    dbc.CardBody([
                        dcc.Graph(id="top-indicators-chart")
                    ])
                ])
            ], md=6),
        ], className="mb-4"),
        
        # Recent Data Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent High-Confidence Metrics"),
                    dbc.CardBody([
                        html.Div(id="recent-metrics-table")
                    ])
                ])
            ])
        ])
    ], fluid=True)

# AI Adoption page
def create_adoption_layout():
    """Create the AI adoption analysis page."""
    
    return dbc.Container([
        html.H2("AI Adoption Analysis", className="mb-4"),
        
        # Year selector
        dbc.Row([
            dbc.Col([
                html.Label("Select Year Range:"),
                dcc.RangeSlider(
                    id='adoption-year-slider',
                    min=2020,
                    max=2025,
                    value=[2022, 2024],
                    marks={i: str(i) for i in range(2020, 2026)},
                    step=1
                )
            ], md=6),
            
            dbc.Col([
                html.Label("Select Countries:"),
                dcc.Dropdown(
                    id='adoption-country-dropdown',
                    options=[
                        {'label': 'United States', 'value': 'United States'},
                        {'label': 'China', 'value': 'China'},
                        {'label': 'Germany', 'value': 'Germany'},
                        {'label': 'Global', 'value': 'Global'}
                    ],
                    value=['United States', 'Global'],
                    multi=True
                )
            ], md=6)
        ], className="mb-4"),
        
        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Adoption Rate Trends"),
                    dbc.CardBody([
                        dcc.Graph(id="adoption-trends-chart")
                    ])
                ])
            ], md=12)
        ])
    ], fluid=True)

# Callbacks for overview page
@callback(
    Output("metrics-by-type-chart", "figure"),
    Input("url", "pathname")
)
def update_metrics_by_type(_):
    """Create bar chart of metrics by type."""
    
    # Get metric type counts from summary
    metric_types = summary_stats.get('metrics_by_type', {})
    
    # Sort by count and take top 10
    sorted_types = sorted(metric_types.items(), key=lambda x: x[1], reverse=True)[:10]
    
    df = pd.DataFrame(sorted_types, columns=['Metric Type', 'Count'])
    
    fig = px.bar(
        df, 
        x='Count', 
        y='Metric Type',
        orientation='h',
        color='Count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        showlegend=False,
        template="plotly_white",
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

@callback(
    Output("top-indicators-chart", "figure"),
    Input("url", "pathname")
)
def update_top_indicators(_):
    """Create pie chart of top economic indicators."""
    
    # Get top 5 metric types
    metric_types = summary_stats.get('metrics_by_type', {})
    sorted_types = sorted(metric_types.items(), key=lambda x: x[1], reverse=True)[:5]
    
    labels = [t[0].replace('_', ' ').title() for t in sorted_types]
    values = [t[1] for t in sorted_types]
    
    fig = px.pie(
        values=values,
        names=labels,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(
        showlegend=True,
        template="plotly_white"
    )
    
    return fig

@callback(
    Output("recent-metrics-table", "children"),
    Input("url", "pathname")
)
def update_recent_metrics_table(_):
    """Create table of recent high-confidence metrics."""
    
    # Get recent high-confidence metrics
    recent_metrics = db.get_metrics_by_type('adoption_rate', year=2024)[:10]
    
    if not recent_metrics:
        return html.P("No recent metrics found", className="text-muted")
    
    rows = []
    for metric in recent_metrics:
        rows.append(
            html.Tr([
                html.Td(str(metric['year'])),
                html.Td(metric.get('country', 'Global')),
                html.Td(metric['source']),
                html.Td(f"{metric['value']:.1f} {metric['unit']}"),
                html.Td(f"{metric['confidence']:.0%}")
            ])
        )
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Year"),
                html.Th("Country/Region"),
                html.Th("Source"),
                html.Th("Value"),
                html.Th("Confidence")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
    
    return table

# Callback for adoption trends
@callback(
    Output("adoption-trends-chart", "figure"),
    [Input("adoption-year-slider", "value"),
     Input("adoption-country-dropdown", "value")]
)
def update_adoption_trends(year_range, countries):
    """Update adoption trends chart based on selections."""
    
    if not countries:
        countries = ['United States']
    
    fig = go.Figure()
    
    for country in countries:
        # Get time series data
        df = db.get_time_series('adoption_rate', country)
        
        if not df.empty:
            # Filter by year range
            df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
            
            fig.add_trace(go.Scatter(
                x=df['year'],
                y=df['value'],
                mode='lines+markers',
                name=country,
                line=dict(width=3)
            ))
    
    fig.update_layout(
        title="AI Adoption Rate Over Time",
        xaxis_title="Year",
        yaxis_title="Adoption Rate (%)",
        hovermode='x unified',
        template="plotly_white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

# Page routing callback
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to different pages based on URL."""
    
    if pathname == '/adoption':
        return create_adoption_layout()
    elif pathname == '/investment':
        return create_investment_layout(db)
    elif pathname == '/sectors':
        return html.Div([
            html.H2("Sector Analysis - Coming Soon"),
            html.P("This page will show sector-specific AI metrics.")
        ])
    elif pathname == '/sources':
        return html.Div([
            html.H2("Data Sources - Coming Soon"),
            html.P("This page will show information about our data sources.")
        ])
    else:
        return create_overview_layout()

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)