import dash_bootstrap_components as dbc
from dash import html

def create_institution_card(data):
    # Main info card
    institution_card = dbc.Card(
        [
            dbc.CardHeader(
                html.H3(f"Détails de l'établissement", className="text-center mb-0"),
                className="bg-primary text-white"
            ),
            dbc.CardBody(
                [
                    # Institution name in a separate styled div
                    html.Div(
                        data['nom_etab'],
                        className="h4 text-center mb-4 text-primary"
                    ),
                    
                    # Create two columns for better organization
                    dbc.Row(
                        [
                            # Left column
                            dbc.Col(
                                [
                                    create_info_item("Session", data['session'], "calendar"),
                                    create_info_item("Académie", data['academie'], "book"),
                                ],
                                width=6,
                            ),
                            # Right column
                            dbc.Col(
                                [
                                    create_info_item("Ville", data['ville'], "geo-alt"),
                                    create_info_item("Département", f"{data['dep_lib']} - {data['dep']}", "building"),
                                ],
                                width=6,
                            ),
                        ]
                    ),
                    
                    # Region in a separate row for emphasis
                    dbc.Row(
                        dbc.Col(
                            create_info_item("Région", data['region'], "map", True),
                            className="mt-3"
                        )
                    ),
                ]
            ),
        ],
        className="shadow-sm mb-4",
    )
    
    return institution_card

def create_info_item(label, value, icon, full_width=False):
    """Helper function to create consistently styled info items with icons"""
    return html.Div(
        [
            html.P(
                [
                    html.I(className=f"bi bi-{icon} me-2"),  # Bootstrap icon
                    html.Span(label, className="fw-bold me-2"),
                    html.Span(value),
                ],
                className="mb-2"
            ),
        ],
        className="w-100" if full_width else ""
    )
