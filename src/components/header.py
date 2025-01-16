from dash import html

def create_header():
    return html.Div(
        className="header",
        children=[
            html.Div(
                className="logo",
                children=[
                    html.Img(
                        src="/assets/logo.png",
                        alt="Logo",
                        style={"height": "50px", "margin-right": "15px"}
                    ),
                    html.H1(
                        "Visualisation des données Parcoursup",
                        style={"display": "inline", "vertical-align": "middle"}
                    ),
                ],
                style={"display": "flex", "align-items": "center"}
            ),
            html.P(
                "Explorez les formations, les établissements et les données d'admission",
                style={"font-size": "16px", "color": "gray", "margin-top": "10px"}
            ),
        ],
        style={
            "background-color": "#f8f9fa",
            "padding": "20px",
            "border-bottom": "2px solid #d3d3d3",
            "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)"
        }
    )
