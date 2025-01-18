from dash import html
from dash.development.base_component import Component

def create_footer() -> Component:
    """
    Crée un footer pour la page d'accueil dash

    Returns:
    Component: Un composant Dash (html) représentant le footer (pied de page).
    """
    return html.Div(
        className="footer",
        children=[
            html.P(
                "© 2025 Visualisation Parcoursup - Laura LEROY & Lauriane COTOR",
                style={"font-size": "14px", "margin": "0"}
            )
        ],
        style={
            "background-color": "#f8f9fa",
            "padding": "20px",
            "text-align": "center",
            "border-top": "2px solid #d3d3d3",
            "font-size": "14px"
        }
    )
