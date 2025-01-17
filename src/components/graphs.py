import plotly.express as px
import plotly.graph_objects as go
from src.utils.fuzzy_word import categorize
from plotly.subplots import make_subplots

def generate_pie_chart(result):
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
        title=f"Répartition des mentions au bac des admis pour la formation {result['intitule_formation']}"
    )
    return fig

def create_nested_pie_chart(data):
    # Extraction des données de base
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

    # Calcul des catégories opposées proposition vs refusés, admis vs voeux non accepté
    refuses = [max(c - p, 0) for c, p in zip(candidats, propositions)]  # Refusé
    voeux_non_acceptes = [max(p - a, 0) for p, a in zip(propositions, admis)]  # Vœux non acceptés

    labels = [
        "Candidats BG", "Propositions BG", "Admis BG", "Vœux non acceptés BG", "Refusé BG",
        "Candidats BT", "Propositions BT", "Admis BT", "Vœux non acceptés BT", "Refusé BT",
        "Candidats BP", "Propositions BP", "Admis BP", "Vœux non acceptés BP", "Refusé BP",
        "Candidats Autres", "Propositions Autres", "Admis Autres", "Vœux non acceptés Autres", "Refusé Autres",
    ]

    # Définition des parents pour la hiérarchie
    parents = [
        "", "Candidats BG", "Propositions BG", "Propositions BG", "Candidats BG",  # BG
        "", "Candidats BT", "Propositions BT", "Propositions BT", "Candidats BT",  # BT
        "", "Candidats BP", "Propositions BP", "Propositions BP", "Candidats BP",  # BP
        "", "Candidats Autres", "Propositions Autres", "Propositions Autres", "Candidats Autres",  # Autres
    ]

    values = [
        candidats[0], propositions[0], admis[0], voeux_non_acceptes[0], refuses[0],  # BG
        candidats[1], propositions[1], admis[1], voeux_non_acceptes[1], refuses[1],  # BT
        candidats[2], propositions[2], admis[2], voeux_non_acceptes[2], refuses[2],  # BP
        candidats[3], propositions[3], admis[3], voeux_non_acceptes[3], refuses[3],  # Autres
    ]

    colors = [
        "#1B4965", "#0081A7", "#00AFB9", "#62B6CB", "#BEE9E8",  # BG  --> Candidats, Propositions, Admis, Vœux non acceptés, Refusé, 
        "#FF7B00", "#FF9500", "#FFA200", "#FFB700", "#FF8800",  # BT
        "#55753C", "#96BE8C", "#ACECA1", "#C9F2C7", "#629460",  # BP
        "#6E0D0D", "#F73E3E", "#A81111", "#FF7777", "#DE1021",  # Autres
    ]
    
    shape=dict(
        shape=[
            "", "", "", "/", "/",  # BG
            "", "", "", "/", "/",  # BT
            "", "", "", "/", "/",  # BP
            "", "", "", "/", "/",  # Autres
        ],
        solidity=0.9)

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",  # Les parents incluent les enfants
        marker=dict(colors=colors,pattern=shape)
    ))

    # Mise en forme de la figure
    fig.update_layout(
        title="Répartition des candidats, propositions et admis par type de bac",
        margin=dict(t=40, l=0, r=0, b=0),
    )

    return fig

def generate_heatmap(df, formation, annee):
    # Filtrer les données par formation et année
    df_filtered = df[df["annee_du_bac"] == annee]

    value_index_map = {row["formation"]: index for index, row in df_filtered.iterrows()}
    processed_formation = categorize(formation['intitule_formation'], formation['form_lib_voe_acc'], value_index_map)
    df_filtered = df[(df["formation"] == processed_formation) & (df["annee_du_bac"] == annee)].copy()
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
    
    # Normalisation par rapport à la valeur maximale
    max_value = pivot_table.max().max()  # Trouver la valeur maximale dans le tableau
    pivot_table_percentage = (pivot_table / max_value) * 100

    fig = px.imshow(
        pivot_table_percentage,
        labels={
            "x": "Spécialité 1 (Axe X)",
            "y": "Spécialité 2 (Axe Y)",
            "color": "Pourcentage (%)"
        },
        title=f"Répartition des propositions d'admission ({formation['intitule_formation']} - {annee})",
        color_continuous_scale="Portland",
        text_auto=".2f",  # Formater les valeurs en pourcentage avec 2 décimales
        zmin=0,  # Définir le minimum de l'échelle de couleur à 0%
        zmax=100,  # Définir le maximum de l'échelle de couleur à 100%
        range_color=[0, 100]
    )
    fig.update_layout(
        xaxis_title="Spécialité 1", 
        yaxis_title="Spécialité 2",
        autosize=True,
        height=700,  # Set a fixed minimum height
        margin=dict(
            l=150,    # Increased left margin for y-axis labels
            r=50,
            t=100,    # Increased top margin for title
            b=150     # Increased bottom margin for x-axis labels
        ),
        coloraxis_colorbar=dict(
            tickformat=".0%",  # Formater les ticks de la barre en pourcentage
            title="Pourcentage"
        ),
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(size=10),automargin=True)  # Labels de l'axe X inclinés à 45°
    fig.update_yaxes(tickangle=0, tickfont=dict(size=10),automargin=True)  # Labels de l'axe Y laissés verticaux
    
    # fig.update_xaxes(ticktext=[textwrap.fill(label, width=15) for label in pivot_table.columns])
    # fig.update_yaxes(ticktext=[textwrap.fill(label, width=15) for label in pivot_table.index])
    return fig

def generate_gender_metrics(formation_data):
    """
    Generate visualizations focusing on gender distribution in formation data.
    
    Args:
        formation_data (dict): Data for a single formation.
    """
    # Create figure with 1 row and 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Répartition par genre des candidatures et admissions",
            "Évolution du ratio femmes/hommes"
        ),
        specs=[
            [{"type": "sunburst"}, {"type": "bar"}]
        ]
    )
    
    # 1. Combined Sunburst Chart for Candidatures and Admissions
    labels = ['Total', 'Femmes', 'Hommes', 'Femmes Admis', 'Hommes Admis']
    parents = ['', 'Total', 'Total', 'Femmes', 'Hommes']
    values = [
        formation_data['effectif_total_candidat'],
        formation_data['effectif_total_candidat_femme'],
        formation_data['effectif_total_candidat'] - formation_data['effectif_total_candidat_femme'],
        formation_data['acceptation_total_f'],
        formation_data['acceptation_total'] - formation_data['acceptation_total_f']
    ]

    fig.add_trace(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues='total',
            name="Répartition par genre",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # 2. Évolution du ratio femmes/hommes (Bar chart for absolute counts)
    fig.add_trace(
        go.Bar(
            name='Femmes',
            x=['Candidatures', 'Admissions'],
            y=[formation_data['effectif_total_candidat_femme'], formation_data['acceptation_total_f']],
            text=[formation_data['effectif_total_candidat_femme'], formation_data['acceptation_total_f']],
            textposition='auto',
            marker_color='#FF69B4',
            hovertemplate="Femmes<br>%{x}: %{y}<extra></extra>"
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            name='Hommes',
            x=['Candidatures', 'Admissions'],
            y=[formation_data['effectif_total_candidat'] - formation_data['effectif_total_candidat_femme'],
               formation_data['acceptation_total'] - formation_data['acceptation_total_f']],
            text=[formation_data['effectif_total_candidat'] - formation_data['effectif_total_candidat_femme'],
                  formation_data['acceptation_total'] - formation_data['acceptation_total_f']],
            textposition='auto',
            marker_color='#4169E1',
            hovertemplate="Hommes<br>%{x}: %{y}<extra></extra>"
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f"Analyse de la répartition femmes/hommes - {formation_data['intitule_formation']}",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=True,
        height=600,
        template='plotly_white',
        barmode='group'
    )
    
    return fig
