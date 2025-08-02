"""
Human-in-the-Loop Validation Interface
Simple Dash app for reviewing and validating extracted metric candidates
"""

import json
from pathlib import Path
from typing import List, Dict
import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

from economic_metrics_schema import (
    MetricCategory, MetricType, Unit,
    GeographicScope, Sector
)


class ValidationUI:
    """Web interface for validating metric candidates"""
    
    def __init__(self, candidates_dir: Path = Path("extraction_output")):
        self.candidates_dir = candidates_dir
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.current_candidates = []
        self.current_index = 0
        self.current_file = None
        
        # Category and type options
        self.categories = [cat.value for cat in MetricCategory]
        self.types = [t.value for t in MetricType]
        self.units = [u.value for u in Unit]
        
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Create the UI layout"""
        
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Metric Validation Interface", className="mb-4"),
                    html.P("Review and validate extracted economic metrics", className="lead")
                ])
            ]),
            
            # File selector
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select candidates file:"),
                    dcc.Dropdown(
                        id="file-selector",
                        options=[],
                        placeholder="Select a file..."
                    )
                ], width=8),
                dbc.Col([
                    html.Div(id="file-stats", className="text-muted mt-4")
                ], width=4)
            ], className="mb-4"),
            
            # Progress bar
            dbc.Progress(id="progress-bar", className="mb-4"),
            
            # Main validation area
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Candidate Review", className="d-inline"),
                    html.Span(id="candidate-number", className="float-end text-muted")
                ]),
                dbc.CardBody([
                    # Extracted data display
                    dbc.Row([
                        dbc.Col([
                            html.H5("Extracted Value"),
                            html.H2(id="extracted-value", className="text-primary"),
                            html.P(id="extraction-method", className="text-muted")
                        ], width=4),
                        dbc.Col([
                            html.H5("Context"),
                            html.Div(id="context-text", 
                                    style={"maxHeight": "150px", "overflowY": "auto"},
                                    className="border p-2")
                        ], width=8)
                    ], className="mb-4"),
                    
                    # Validation controls
                    html.Hr(),
                    html.H5("Validation Decision"),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.RadioItems(
                                id="validation-decision",
                                options=[
                                    {"label": "Accept", "value": "accept"},
                                    {"label": "Reject", "value": "reject"},
                                    {"label": "Modify", "value": "modify"},
                                    {"label": "Skip", "value": "skip"}
                                ],
                                value="skip",
                                inline=True
                            )
                        ])
                    ], className="mb-3"),
                    
                    # Classification dropdowns (shown when Accept or Modify)
                    html.Div(id="classification-section", children=[
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Category"),
                                dcc.Dropdown(
                                    id="category-dropdown",
                                    options=[{"label": cat, "value": cat} for cat in self.categories],
                                    placeholder="Select category..."
                                )
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Type"),
                                dcc.Dropdown(
                                    id="type-dropdown",
                                    options=[{"label": t, "value": t} for t in self.types],
                                    placeholder="Select type..."
                                )
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Unit"),
                                dcc.Dropdown(
                                    id="unit-dropdown",
                                    options=[{"label": u, "value": u} for u in self.units],
                                    placeholder="Select unit..."
                                )
                            ], width=4)
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Notes"),
                                dbc.Textarea(
                                    id="notes-input",
                                    placeholder="Add any notes or corrections...",
                                    rows=2
                                )
                            ])
                        ])
                    ], style={"display": "none"}),
                    
                    # Suggested values display
                    html.Div(id="suggestions", className="mt-3 p-3 bg-light", children=[
                        html.H6("AI Suggestions:"),
                        html.P(id="suggested-values", className="mb-0")
                    ])
                ])
            ], className="mb-4"),
            
            # Navigation buttons
            dbc.Row([
                dbc.Col([
                    dbc.Button("Previous", id="prev-button", color="secondary", className="me-2"),
                    dbc.Button("Next", id="next-button", color="primary", className="me-2"),
                    dbc.Button("Save Progress", id="save-button", color="success", className="float-end")
                ])
            ]),
            
            # Hidden storage
            dcc.Store(id="validation-data", data={}),
            
            # Save confirmation
            dbc.Toast(
                "Progress saved!",
                id="save-toast",
                header="Success",
                is_open=False,
                dismissable=True,
                duration=4000,
                icon="success",
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            ),
        ], fluid=True)
    
    def _setup_callbacks(self):
        """Setup all callbacks"""
        
        @self.app.callback(
            Output("file-selector", "options"),
            Output("file-stats", "children"),
            Input("file-selector", "id")  # Triggered on load
        )
        def update_file_list(_):
            """Update available files list"""
            files = list(self.candidates_dir.glob("*_candidates.json"))
            options = [{"label": f.name, "value": str(f)} for f in files]
            
            stats = f"Found {len(files)} candidate files"
            return options, stats
        
        @self.app.callback(
            Output("validation-data", "data"),
            Output("candidate-number", "children"),
            Output("extracted-value", "children"),
            Output("extraction-method", "children"),
            Output("context-text", "children"),
            Output("suggested-values", "children"),
            Output("category-dropdown", "value"),
            Output("type-dropdown", "value"),
            Output("progress-bar", "value"),
            Output("progress-bar", "label"),
            Input("file-selector", "value"),
            Input("next-button", "n_clicks"),
            Input("prev-button", "n_clicks"),
            State("validation-data", "data"),
            State("validation-decision", "value"),
            State("category-dropdown", "value"),
            State("type-dropdown", "value"),
            State("unit-dropdown", "value"),
            State("notes-input", "value"),
            prevent_initial_call=True
        )
        def update_candidate(file_path, next_clicks, prev_clicks, 
                           validation_data, decision, category, type_val, unit, notes):
            """Handle candidate navigation and display"""
            
            triggered = ctx.triggered_id
            
            # Load file if changed
            if triggered == "file-selector" and file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.current_candidates = json.load(f)
                self.current_index = 0
                self.current_file = file_path
                validation_data = {}
            
            # Save current validation before moving
            elif triggered in ["next-button", "prev-button"] and self.current_candidates:
                if decision != "skip":
                    candidate_id = self.current_candidates[self.current_index]["candidate_id"]
                    validation_data[candidate_id] = {
                        "decision": decision,
                        "category": category,
                        "type": type_val,
                        "unit": unit,
                        "notes": notes,
                        "validated_at": datetime.now().isoformat()
                    }
                
                # Navigate
                if triggered == "next-button":
                    self.current_index = min(self.current_index + 1, 
                                           len(self.current_candidates) - 1)
                else:
                    self.current_index = max(self.current_index - 1, 0)
            
            # Display current candidate
            if self.current_candidates and 0 <= self.current_index < len(self.current_candidates):
                candidate = self.current_candidates[self.current_index]
                
                # Check if already validated
                existing_validation = validation_data.get(candidate["candidate_id"], {})
                
                # Progress calculation
                validated_count = len(validation_data)
                total_count = len(self.current_candidates)
                progress = (validated_count / total_count * 100) if total_count > 0 else 0
                
                return (
                    validation_data,
                    f"Candidate {self.current_index + 1} of {total_count}",
                    f"{candidate['numeric_value']} {candidate['unit_hint']}",
                    f"Method: {candidate['extraction_method']} | Confidence: {candidate['confidence_score']:.2f}",
                    candidate['surrounding_text'],
                    f"Category: {candidate['suggested_category']} | Type: {candidate['suggested_type']} | Geography: {candidate['suggested_geography']}",
                    existing_validation.get("category", candidate['suggested_category']),
                    existing_validation.get("type", candidate['suggested_type']),
                    progress,
                    f"{validated_count}/{total_count} validated"
                )
            
            return validation_data, "", "", "", "", "", None, None, 0, ""
        
        @self.app.callback(
            Output("classification-section", "style"),
            Input("validation-decision", "value")
        )
        def toggle_classification(decision):
            """Show/hide classification section based on decision"""
            if decision in ["accept", "modify"]:
                return {"display": "block"}
            return {"display": "none"}
        
        @self.app.callback(
            Output("save-toast", "is_open"),
            Input("save-button", "n_clicks"),
            State("validation-data", "data"),
            prevent_initial_call=True
        )
        def save_validation(n_clicks, validation_data):
            """Save validation results"""
            if n_clicks and self.current_file and validation_data:
                # Save to output file
                output_file = Path(self.current_file).parent / Path(self.current_file).name.replace(
                    "_candidates.json", "_validated.json"
                )
                
                # Merge validation data with candidates
                validated_candidates = []
                for candidate in self.current_candidates:
                    candidate_id = candidate["candidate_id"]
                    if candidate_id in validation_data:
                        candidate.update(validation_data[candidate_id])
                        candidate["is_validated"] = True
                        validated_candidates.append(candidate)
                
                # Save validated data
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(validated_candidates, f, indent=2, ensure_ascii=False)
                
                return True
            
            return False
    
    def run(self, debug=True, port=8050):
        """Run the validation UI"""
        self.app.run_server(debug=debug, port=port)


def create_final_dataset(validated_file: Path, output_file: Path):
    """Convert validated candidates to final Stanford-schema dataset"""
    
    with open(validated_file, 'r', encoding='utf-8') as f:
        validated_data = json.load(f)
    
    # Filter accepted candidates
    accepted = [c for c in validated_data if c.get("decision") == "accept"]
    
    # Convert to DataFrame for easy manipulation
    df = pd.DataFrame(accepted)
    
    # Create Stanford-style output
    stanford_format = []
    
    for _, row in df.iterrows():
        stanford_format.append({
            "source": row["source_document"],
            "page": row["page_number"],
            "category": row["category"],
            "type": row["type"],
            "value": row["numeric_value"],
            "unit": row["unit"],
            "geographic_area": row.get("suggested_geography", "Not specified"),
            "year": extract_year_from_context(row["surrounding_text"]),
            "confidence": row["confidence_score"],
            "context": row["surrounding_text"][:200],
            "notes": row.get("notes", "")
        })
    
    # Save as CSV
    output_df = pd.DataFrame(stanford_format)
    output_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Created final dataset with {len(output_df)} validated metrics")
    print(f"Saved to: {output_file}")
    
    # Summary statistics
    print("\nSummary by category:")
    print(output_df["category"].value_counts())
    
    print("\nSummary by geographic area:")
    print(output_df["geographic_area"].value_counts())


def extract_year_from_context(context: str) -> int:
    """Extract year from context string"""
    import re
    years = re.findall(r'\b(20\d{2})\b', context)
    if years:
        # Return the most recent year found
        return max(int(y) for y in years)
    return None


# Run the UI
if __name__ == "__main__":
    ui = ValidationUI()
    print("Starting validation UI at http://localhost:8050")
    print("Press Ctrl+C to stop")
    ui.run()