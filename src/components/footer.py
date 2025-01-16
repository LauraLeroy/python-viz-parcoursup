from dash import html

def create_footer():
    return html.Div(
        className="footer",
        children=[
            html.P(
                "© 2025 Visualisation Parcoursup - Laura LEROY & Lauriane COTOR",
                style={"font-size": "14px", "margin": "0"}
            ),
            html.Div(
                children=[
                    html.A(
                        "Mentions légales",
                        href="#",
                        style={"margin-right": "15px", "text-decoration": "none", "color": "#007bff"}
                    ),
                    html.A(
                        "Contactez-nous",
                        href="mailto:contact@example.com",
                        style={"text-decoration": "none", "color": "#007bff"}
                    ),
                ],
                style={"margin-top": "10px"}
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
