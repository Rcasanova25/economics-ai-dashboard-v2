"""
Economics AI Dashboard - Main Application

This is like the main control panel of your economic analysis tool.
Dash turns Python code into interactive web pages.
"""

import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Import our data models
from src.models.schema import create_sample_data, AIAdoptionMetric

# Initialize the Dash app with a nice theme
# Think of this as setting up your presentation template
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],  # Professional looking theme
    title="Economics of AI Dashboard"
)

# Create the layout - this is what users will see
# Think of it as designing the pages of your economic report
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Economics of AI Dashboard", className="text-center mb-4"),
            html.P(
                "Analyzing AI adoption trends and economic impacts across industries",
                className="text-center text-muted"
            )
        ])
    ]),
    
    # Key Metrics Cards - Like executive summary boxes
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Global AI Adoption", className="card-title"),
                    html.H2("45.5%", className="text-primary"),
                    html.P("of companies using AI (2023)", className="text-muted")
                ])
            ])
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("AI Investment", className="card-title"),
                    html.H2("$127.8B", className="text-success"),
                    html.P("Global investment (2024)", className="text-muted")
                ])
            ])
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Productivity Gain", className="card-title"),
                    html.H2("+15.2%", className="text-info"),
                    html.P("in manufacturing (2023)", className="text-muted")
                ])
            ])
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Data Sources", className="card-title"),
                    html.H2("6", className="text-warning"),
                    html.P("Analyzed reports", className="text-muted")
                ])
            ])
        ], md=3),
    ], className="mb-4"),
    
    # Charts Section
    dbc.Row([
        # Left chart - Adoption over time
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("AI Adoption Trends by Sector"),
                dbc.CardBody([
                    dcc.Graph(id="adoption-chart")
                ])
            ])
        ], md=6),
        
        # Right chart - Investment by region
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("AI Investment by Region"),
                dbc.CardBody([
                    dcc.Graph(id="investment-chart")
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Data Table Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Detailed Metrics"),
                dbc.CardBody([
                    html.Div(id="data-table")
                ])
            ])
        ])
    ])
    
], fluid=True, className="p-4")


# Callbacks - These make the dashboard interactive
# Think of callbacks as "when user does X, update Y"

@callback(
    Output("adoption-chart", "figure"),
    Input("adoption-chart", "id")  # Triggered on load
)
def update_adoption_chart(_):
    """Create adoption trends chart"""
    # For now, using sample data
    # Later, this will pull from our database
    
    # Create sample trend data
    years = [2020, 2021, 2022, 2023, 2024]
    tech_adoption = [25, 32, 38, 45, 52]
    finance_adoption = [20, 28, 35, 42, 48]
    manufacturing_adoption = [15, 20, 26, 32, 38]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years, y=tech_adoption,
        mode='lines+markers',
        name='Technology',
        line=dict(width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=finance_adoption,
        mode='lines+markers', 
        name='Finance',
        line=dict(width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=years, y=manufacturing_adoption,
        mode='lines+markers',
        name='Manufacturing',
        line=dict(width=3)
    ))
    
    fig.update_layout(
        yaxis_title="Adoption Rate (%)",
        xaxis_title="Year",
        hovermode='x unified',
        template="plotly_white"
    )
    
    return fig


@callback(
    Output("investment-chart", "figure"),
    Input("investment-chart", "id")
)
def update_investment_chart(_):
    """Create investment by region chart"""
    
    regions = ['North America', 'Europe', 'Asia Pacific', 'Rest of World']
    investment = [45.2, 32.1, 38.5, 12.0]
    
    fig = px.pie(
        values=investment,
        names=regions,
        hole=0.4,  # Makes it a donut chart
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>$%{value}B<br>%{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        template="plotly_white"
    )
    
    return fig


@callback(
    Output("data-table", "children"),
    Input("data-table", "id")
)
def update_data_table(_):
    """Create a simple data table from our sample data"""
    
    # Get sample data
    metrics = create_sample_data()
    
    # Convert to a simple HTML table
    # In a real app, we'd use dash_table.DataTable for more features
    
    rows = []
    for metric in metrics:
        rows.append(
            html.Tr([
                html.Td(str(metric.year)),
                html.Td(metric.sector or "Global"),
                html.Td(metric.metric_type.replace("_", " ").title()),
                html.Td(f"{metric.value:.1f} {metric.unit}"),
                html.Td(metric.source.value if metric.source else "Unknown")
            ])
        )
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Year"),
                html.Th("Sector"),
                html.Th("Metric"),
                html.Th("Value"),
                html.Th("Source")
            ])
        ]),
        html.Tbody(rows)
    ], striped=True, bordered=True, hover=True, responsive=True)
    
    return table


# This is what runs the app
if __name__ == "__main__":
    # Run in debug mode for development
    # In production, set debug=False
    app.run_server(debug=True, host="127.0.0.1", port=8050)