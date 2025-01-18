from typing import Dict, Union, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_pie_chart(result: Dict[str, Union[int, str]]) -> go.Figure:
    """Genère un graphique en camembert pour la répartition des mentions au bac des admis pour une formation donnée
        Args:
        result (Dict[str, int]): Le dictionnaire de données  à utiliser déjà filtré par année et formation

        Returns:
        Optional[go.Figure]: Le graphique
    """

    labels = ['Sans Mention', 'Mention AB', 'Mention B', 'Mention TB', 'Mention TBF']
    values = [
        result['effectif_admis_mention_aucune'],
        result['effectif_admis_mention_AB'],
        result['effectif_admis_mention_B'],
        result['effectif_admis_mention_TB'],
        result['effectif_admis_mention_TBF'],
    ]
    fig = px.pie(
        names=labels,
        values=values,
        title=f"Répartition des mentions au bac des admis pour la formation"
    )
    fig.update_layout(
        title={
            'font': {'size': 12},
        },
        margin=dict(t=40, b=40, l=40, r=40),
    )
    return fig


def create_nested_pie_chart(data: Dict[str, int]) -> go.Figure:
    """Genère un graphique en camembert imbriqué pour la répartition des candidats, propositions et admis par type de bac 
        BG: Bagéalaureat général
        BT: Baccalauréat technologique
        BP: Baccalauréat professionnel
        Autre: Autres types de baccalauréat ou formation

        Args:
        data (Dict[str, int]): Le dictionnaire de données  à utiliser déjà filtré par année et formation

        Returns:
        Optional[go.Figure]: Le graphique
    """
    candidats = [
        data['effectif_total_candidat_bg_pp'],
        data['effectif_total_candidat_bt_pp'],
        data['effectif_total_candidat_bp_pp'],
        data['effectif_total_candidat_autre_pp'],
    ]
    propositions = [
        data['proposition_admission_total_BG'],
        data['proposition_admission_total_BT'],
        data['proposition_admission_total_BP'],
        data['proposition_admission_total_autre'],
    ]
    admis = [
        data['effectif_admis_BG'],
        data['effectif_admis_BT'],
        data['effectif_admis_BP'],
        data['effectif_admis_at'],
    ]

    refuses = [max(c - p, 0) for c, p in zip(candidats, propositions)]
    voeux_non_acceptes = [max(p - a, 0) for p, a in zip(propositions, admis)]

    labels = [
        "Candidats BG", "Propositions BG", "Admis BG", "Vœux non acceptés BG", "Refusé BG",
        "Candidats BT", "Propositions BT", "Admis BT", "Vœux non acceptés BT", "Refusé BT",
        "Candidats BP", "Propositions BP", "Admis BP", "Vœux non acceptés BP", "Refusé BP",
        "Candidats Autres", "Propositions Autres", "Admis Autres", "Vœux non acceptés Autres", "Refusé Autres",
    ]

    parents = [
        "", "Candidats BG", "Propositions BG", "Propositions BG", "Candidats BG",
        "", "Candidats BT", "Propositions BT", "Propositions BT", "Candidats BT",
        "", "Candidats BP", "Propositions BP", "Propositions BP", "Candidats BP",
        "", "Candidats Autres", "Propositions Autres", "Propositions Autres", "Candidats Autres",
    ]

    values = [
        candidats[0], propositions[0], admis[0], voeux_non_acceptes[0], refuses[0],
        candidats[1], propositions[1], admis[1], voeux_non_acceptes[1], refuses[1],
        candidats[2], propositions[2], admis[2], voeux_non_acceptes[2], refuses[2],
        candidats[3], propositions[3], admis[3], voeux_non_acceptes[3], refuses[3],
    ]

    colors = [
        "#1B4965", "#0081A7", "#00AFB9", "#62B6CB", "#BEE9E8",
        "#FF7B00", "#FF9500", "#FFA200", "#FFB700", "#FF8800",
        "#55753C", "#96BE8C", "#ACECA1", "#C9F2C7", "#629460",
        "#6E0D0D", "#F73E3E", "#A81111", "#FF7777", "#DE1021",
    ]

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colors=colors)
    ))

    fig.update_layout(
        title={
            'text': "Répartition des candidats, propositions et admis par type de bac",
            'font': {'size': 12}
        },
    )

    return fig


def generate_heatmap(df: pd.DataFrame, formation: str, annee: int) -> Optional[go.Figure]:
    """Génère un heatmap du nombre de propositions d'admission par doublette de spécialités pour une formation et une année données

    Args:
        df (pd.DataFrame): le dataframe contenant les données
        formation (str): la formation choisie dans le sélecteur
        annee (int): l'année choisie 

    Returns:
        Optional[go.Figure]: Le graphique ou none si aucune donnée n'est trouvée
    """
    df_filtered = df[(df["formation"] == formation) & (df["annee_du_bac"] == annee)].copy()
    if df_filtered.empty:
        return None

    df_filtered["spe1"] = df_filtered["doublette"].apply(lambda x: x[0])
    df_filtered["spe2"] = df_filtered["doublette"].apply(lambda x: x[1])

    pivot_table = df_filtered.pivot_table(
        index="spe2",
        columns="spe1",
        values="propositions_d_admissions",
        aggfunc="sum",
        fill_value=0
    )

    max_value = pivot_table.max().max()
    pivot_table_percentage = (pivot_table / max_value) * 100

    fig = px.imshow(
        pivot_table_percentage,
        labels={
            "x": "Spécialité 1 (Axe X)",
            "y": "Spécialité 2 (Axe Y)",
            "color": "Pourcentage (%)"
        },
        title=f"Répartition des propositions d'admission ({formation} - {annee})",
        color_continuous_scale="Portland",
        text_auto=".2f",
        zmin=0,
        zmax=100,
    )

    fig.update_layout(
        xaxis_title="Spécialité 1",
        yaxis_title="Spécialité 2",
        height=700,
        margin=dict(l=150, r=50, t=100, b=150),
        coloraxis_colorbar=dict(tickformat=".0%", title="Pourcentage"),
    )

    fig.update_xaxes(tickangle=45, tickfont=dict(size=10), automargin=True)
    fig.update_yaxes(tickangle=0, tickfont=dict(size=10), automargin=True)

    return fig


def generate_gender_metrics(formation_data: Dict[str, Union[int, str]]) -> tuple:
    """Genère deux graphiques pour analyser la répartition femmes/hommes des candidatures et des admissions
        Args: 
        formation_data (Dict[str, Union[int, str]]): Les données de la formation à analyser

        Returns:
        tuple: Deux objets go.Figure (un pour chaque graphique)
    """
    # Première figure (Sunburst)
    fig1 = go.Figure(go.Sunburst(
        labels=['Total', 'Femmes', 'Hommes', 'Femmes Admis', 'Hommes Admis'],
        parents=['', 'Total', 'Total', 'Femmes', 'Hommes'],
        values=[
            formation_data['effectif_total_candidat'],
            formation_data['effectif_total_candidat_femme'],
            formation_data['effectif_total_candidat'] - formation_data['effectif_total_candidat_femme'],
            formation_data['acceptation_total_f'],
            formation_data['acceptation_total'] - formation_data['acceptation_total_f']
        ],
        branchvalues='total',
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    ))

    # Deuxième figure (Bar chart)
    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            name='Femmes',
            x=['Candidatures', 'Admissions'],
            y=[formation_data['effectif_total_candidat_femme'], formation_data['acceptation_total_f']],
            textposition='auto',
            marker_color='#FF69B4',
        )
    )

    fig2.add_trace(
        go.Bar(
            name='Hommes',
            x=['Candidatures', 'Admissions'],
            y=[
                formation_data['effectif_total_candidat'] - formation_data['effectif_total_candidat_femme'],
                formation_data['acceptation_total'] - formation_data['acceptation_total_f']
            ],
            textposition='auto',
            marker_color='#4169E1',
        )
    )

    fig2.update_layout(
        barmode='group',
        height=400,
    )

    # Mise à jour de la première figure pour la rendre responsive
    fig1.update_layout(
        title={
            'text': "Répartition femmes/hommes des candidatures et admissions",
            'font': {'size': 12}
        },
        height=600,
        margin=dict(t=30, b=30, l=30, r=30),
        autosize=True,
    )

    # Mise à jour de la deuxième figure pour la rendre responsive
    fig2.update_layout(
        title={
            'text': "Évolution du ratio femmes/hommes",
            'font': {'size': 12}
        },
        height=400,
        margin=dict(t=30, b=30, l=30, r=30),
        autosize=True,
    )

    return fig1, fig2


def generate_double_bar_chart(df: pd.DataFrame, selected_formation: str, selected_year: int) -> go.Figure:
    """Génère un graphique à barres comparant les voeux et les propositions d'admission pour une formation et une année données

    Args:
        df (pd.DataFrame): Le dataframe contenant les données
        selected_formation (str): La formation choisie dans le sélecteur
        selected_year (int): l'année choisie

    Returns:
        go.Figure: Le graphique
    """
    filtered_df = df[(df['annee_du_bac'] == selected_year) & (df['formation'] == selected_formation)]

    melted_df = filtered_df.melt(
        id_vars=['couple_specialites'],
        value_vars=['voeux', 'propositions_d_admissions'],
        var_name='Légende',
        value_name='Valeur'
    )

    fig = px.bar(
        melted_df,
        x='couple_specialites',
        y='Valeur',
        color='Légende',
        barmode='group',
        title=f"Comparaison des voeux et propositions pour l'année {selected_year}"
    )

    fig.update_layout(
        xaxis_title="Duo de spécialités",
        yaxis_title="Nombre de candidats",
    )

    fig.update_xaxes(showticklabels=False)

    return fig
