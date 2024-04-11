import os
from factcheckexplorer.factcheckexplorer import FactCheckLib
from dash import Dash, dcc, html, Input, Output, callback, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import ast
import time
import dash_cytoscape as cyto

app = Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server

layout = {
    'name': 'cose',
    'idealEdgeLength': 350,
    'nodeOverlap': 10,
    'refresh': 20,
    'fit': True,
    'padding': 30,
    'randomize': False,
    'componentSpacing': 100,
    'nodeRepulsion': 800000,
    'edgeElasticity': 100,
    'nestingFactor': 20,
}

stylesheet = [
    {'selector': 'node',
     'style': {'content': 'data(label)', 'text-valign': 'center', 'text-halign': 'center', 'font-size': '10px',
               'font-family': 'Helvetica'}},
    {'selector': 'node.source',
     'style': {'background-color': '#636efa', 'color': '#000000', 'width': '50px', 'height': '50px',
               'border-color': '#4e57c6', 'border-width': 2, 'shape': 'ellipse'}},
    {'selector': 'node.tag',
     'style': {'background-color': '#ef553b', 'color': '#000000', 'width': '40px', 'height': '40px',
               'border-color': '#bc422e', 'border-width': 2, 'shape': 'ellipse'}},
    {'selector': 'edge',
     'style': {'curve-style': 'bezier', 'width': 2, 'line-color': '#ABB2B9', 'target-arrow-color': '#ABB2B9',
               'target-arrow-shape': 'triangle'}},
    {'selector': 'core', 'style': {'background-color': '#F8F9F9', 'font-family': 'Helvetica'}}
]

global df, csv_filename

def create_info_card(title, icon_class, body_id):
    return dbc.Card(
        [
            dbc.CardHeader(html.Span([html.I(className=icon_class), " ", title]), className="fw-bold"),
            dbc.CardBody(id=body_id, className="text-center", style={'font-size': '20px', 'font-weight': 'bold'})
        ], className="h-100 shadow-sm"
    )

@app.callback(
    [Output(f"collapse-{chart_id}", "is_open") for chart_id in [
        "verdict-chart", "tags-chart", "claims-timeline", "sources-bar-chart", "network-graph"]],
    [Input(f"toggle-{chart_id}", "value") for chart_id in [
        "verdict-chart", "tags-chart", "claims-timeline", "sources-bar-chart", "network-graph"]]
)
def toggle_collapse(*values):
    return [1 in value for value in values]

@app.callback(Output("download-csv", "data"), Input("btn-download-csv", "n_clicks"), prevent_initial_call=True)
def generate_csv(n_clicks):
    if n_clicks and 'df' in globals() and not df.empty:
        return dcc.send_data_frame(df.to_csv, filename=csv_filename)


@app.callback(
    [
        Output("verdict-pie-chart", "figure"),
        Output("tags-bar-chart", "figure"),
        Output("claims-timeline", "figure"),
        Output("sources-bar-chart", "figure"),
        Output("panel-search-query", "children"),
        Output("panel-num-results", "children"),
        Output("panel-unique-sources", "children"),
        Output("panel-unique-tags", "children"),
        Output("factcheck-table", "columns"),
        Output("factcheck-table", "data"),
        Output("network-graph", "elements")
    ],
    [
        Input("search-button", "n_clicks"),
        State("query-input", "value"),
        State("language-input", "value"),
        State("num-results-input", "value"),
        State("graph-checkbox", "value")
    ],
    prevent_initial_call=True
)
def update_charts(n_clicks, query, language, num_results, graph_checkbox):
    global df, csv_filename
    if n_clicks < 1 or not query:
        empty_fig = px.scatter(title="Waiting for data...")
        # Return empty_fig for each graph and suitable placeholders for text outputs
        return empty_fig, empty_fig, empty_fig, empty_fig, "N/A", "0 Results", "0 Unique Sources", "0 Unique Tags"

    df = pd.DataFrame()

    try:
        csv_filename = f"{query.replace(' ', '_').lower() + '_' + str(time.time()).replace('.', '')}.csv"
        fact_check_lib = FactCheckLib(query=query, language=language or 'all', num_results=num_results or 100,
                                      csv_filename=csv_filename)
        fact_check_lib.process()
        df = pd.read_csv(csv_filename, encoding='utf-8')
    except Exception as e:
        print(f"Error processing FactCheckLib: {e}")
        error_fig = px.scatter(title="Error fetching data")
        return error_fig, error_fig, error_fig, error_fig, query, "Error", "Error", "Error"

    df['Tags'] = df['Tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    tags_df = df.explode('Tags')

    def normalize_text(text):
        text = text.rstrip('.')
        text = text.lower()
        return text

    df['Verdict'] = df['Verdict'].apply(normalize_text) \
        .str.replace(r"falso", r"false", regex=False) \
        .str.replace(r"fake", r"false", regex=False) \
        .str.replace(r"falsa", r"false", regex=False) \
        .str.replace(r"verdadero", r"true", regex=False) \
        .str.replace(r"c'est faux", r"false", regex=False) \
        .str.replace(r"doğru", r"true", regex=False) \
        .str.replace(r"dogru", r"true", regex=False) \
        .str.replace(r"doğruluk payı vardır", r"half true", regex=False) \
        .str.replace(r"errado", r"false", regex=False) \
        .str.replace(r"মিথ্যা", r"false", regex=False) \
        .str.replace(r"অসত্য", r"false", regex=False) \
        .str.replace(r"fals", r"false", regex=False) \
        .str.replace(r"falsch", r"false", regex=False) \
        .str.replace(r"false content/false", r"false", regex=False) \
        .str.replace(r"false context/false", r"false", regex=False) \
        .str.replace(r"falso!", r"false", regex=False) \
        .str.replace(r"faux", r"false", regex=False) \
        .str.replace(r"mostly true", r"half true", regex=False) \
        .str.replace(r"partialmente falso", r"mostly false", regex=False) \
        .str.replace(r"misleading/partly false", r"mostly false", regex=False) \
        .str.replace(r"Çok YanlÄ±ÅŞ", r"false", regex=False) \
        .str.replace(r"incorrect", r"false", regex=False) \
        .str.replace(r"مضلل", r"false", regex=False) \
        .str.replace(r"نادرست", r"false", regex=False) \
        .str.replace(r"زائف", r"false", regex=False) \
        .str.replace(r"錯誤", r"false", regex=False) \
        .str.replace(r"部分錯誤", r"false", regex=False) \
        .str.replace(r"pants on fire", r"false", regex=False) \
        .str.replace(r"four pinocchios", r"false", regex=False) \
        .str.replace(r"three pinocchios", r"mostly false", regex=False) \
        .str.replace(r"falsee", r"false", regex=False) \
        .str.replace(r"неверно", r"false", regex=False) \
        .str.replace(r"правильно", r"true", regex=False) \
        .str.replace(r"помилковий", r"false", regex=False) \
        .str.replace(r"вірно", r"true", regex=False) \
        .str.replace(r"錯誤的", r"false", regex=False) \
        .str.replace(r"正確的", r"true", regex=False) \
        .str.replace(r"錯誤な", r"false", regex=False) \
        .str.replace(r"正しい", r"true", regex=False) \
        .str.replace(r"incorrecto", r"false", regex=False) \
        .str.replace(r"notizia false", r"false", regex=False) \
        .str.replace(r"c'eri quasi", r"half true", regex=False) \
        .str.replace(r"pinocchio andante", r"false", regex=False) \
        .str.replace(r"notizia vera", r"true", regex=False) \
        .str.replace(r"vera", r"true", regex=False) \
        .str.replace(r"vero", r"true", regex=False) \
        .str.replace(r"cierto", r"true", regex=False) \
        .str.replace(r"engañoso", r"mostly false", regex=False) \
        .str.replace(r"es falso", r"false", regex=False) \
        .str.replace(r"scam", r"false", regex=False) \
        .str.replace(r"enganoso", r"false", regex=False) \
        .str.replace(r"falsz", r"false", regex=False) \
        .str.replace(r"falsekt", r"false", regex=False) \
        .str.replace(r"falsekt", r"false", regex=False) \
        .str.replace(r"misleidend", r"misleading", regex=False) \
        .str.replace(r"trompeur", r"false", regex=False) \
        .str.replace(r"yanlış", r"false", regex=False) \
        .str.replace(r"es false", r"false", regex=False) \
        .str.replace(r"correct attribution", r"true", regex=False) \
        .str.replace(r"correct", r"true", regex=False) \
        .str.replace(r"delimično netačno", r"mostly false", regex=False) \
        .str.replace(r"enganador", r"mostly false", regex=False) \
        .str.replace(r"epätosi", r"false", regex=False) \
        .str.replace(r"fałsz", r"false", regex=False) \

    verdict_counts = df['Verdict'].value_counts(normalize=True) * 100
    small_verdicts = verdict_counts[verdict_counts < 2].index
    df['Verdict Grouped'] = df['Verdict'].apply(lambda x: 'other' if x in small_verdicts else x)

    verdict_fig = px.pie(df, names='Verdict Grouped', title='Verdict Distribution')
    verdict_fig.update_traces(textinfo='percent+label')

    tags_fig = px.bar(tags_df['Tags'].value_counts().reset_index(), x='index', y='Tags',
                      title='Tags Volume', labels={'index': 'Tag', 'Tags': 'Count'})
    tags_fig.update_layout(xaxis_title="Tag", yaxis_title="Count")

    df['Review Publication Date'] = pd.to_datetime(df['Review Publication Date'])
    timeline_fig = px.scatter(df, x='Review Publication Date', y='Verdict Grouped', color='Verdict Grouped',
                              title='Timeline of Claims', labels={'Review Publication Date': 'Date'})
    timeline_fig.update_layout(xaxis_title="Date", yaxis_title="Verdict")

    sources_counts = df['Source Name'].value_counts().reset_index()
    sources_fig = px.bar(sources_counts, x='Source Name', y='index', orientation='h',
                         labels={'index': 'Source', 'Source Name': 'Number of Checks'},
                         title='Source Volume', text_auto='.2s')
    sources_fig.update_layout(xaxis_title="Number of Checks", yaxis_title="Source",
                              font=dict(family="Roboto, sans-serif", size=12, color="#333"))

    search_query_display = query if query else "Not specified"
    num_results_display = f"{len(df)} Results"
    unique_sources_display = f"{df['Source Name'].nunique()} Unique Sources"

    df['Tags'] = df['Tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
    unique_tags_display = f"{df.explode('Tags')['Tags'].nunique()} Unique Tags"

    if 'Tags' in df.columns:
        df['Tags'] = df['Tags'].apply(
            lambda tags_list: ', '.join(tags_list) if isinstance(tags_list, list) else tags_list)

    columns = [{"name": col, "id": col} for col in df.columns]

    data = df.to_dict('records')

    if 'ON' in graph_checkbox:
        def process_tags(tags):
            if isinstance(tags, str):
                return [tag.strip() for tag in tags.split(',')]
            elif isinstance(tags, list):
                return tags
            return []

        df['Tags'] = df['Tags'].apply(process_tags)

        nodes = [{'data': {'id': src, 'label': src}, 'classes': 'source'} for src in df['Source Name'].unique()]
        nodes += [{'data': {'id': tag, 'label': tag}, 'classes': 'tag'} for tag in
                  set().union(*(df['Tags'].dropna()))]  # Assumes 'Tags' are lists

        added_edges = set()

        edges = []
        for _, row in df.iterrows():
            src = row['Source Name']
            tags = row['Tags'] if isinstance(row['Tags'], list) else []
            for tag in tags:
                # Create a unique identifier for each potential edge
                edge_identifier = (src, tag)
                # Check if this edge has already been added
                if edge_identifier not in added_edges:
                    edges.append({
                        'data': {'source': src, 'target': tag}
                    })
                    # Mark this edge as added
                    added_edges.add(edge_identifier)

        network_elements = nodes + edges
    else:
        network_elements = []

    try:
        os.remove(csv_filename)
    except Exception as e:
        print(f"Could not remove CSV file: {e}")

    return verdict_fig, tags_fig, timeline_fig, sources_fig, search_query_display, num_results_display, unique_sources_display, unique_tags_display, columns, data, network_elements,


app.layout = dbc.Container(fluid=True, children=[
    dbc.Row(dbc.Col(html.Img(src='/assets/FEAT.png', style={'maxHeight': '250px'}), className="text-center", width=12),
            justify="center"),
    html.Hr(),
    html.H2("Search", className="mb-3 mt-4", style={'font-family': 'monospace'}),
    dbc.Row([
        dbc.Col(dcc.Input(id="query-input", type="text", placeholder="Enter a query...", className="form-control mb-2",
                          debounce=True), width=3, style={'font-family': 'monospace'}),
        dbc.Col(dcc.Input(id="language-input", type="text", placeholder="Language (default: all)",
                          className="form-control mb-2", debounce=True), width=2, style={'font-family': 'monospace'}),
        dbc.Tooltip(
            "Use ISO 639-1 language codes (e.g., 'en' for English, 'es' for Spanish).",
            target="language-input",
            placement="top"
        ),
        dbc.Col(dcc.Input(id="num-results-input", type="number", placeholder="# Results (default: 100)",
                          className="form-control mb-2", debounce=True), width=2, style={'font-family': 'monospace'}),
        dbc.Tooltip(
            "Max: 10.000",
            target="num-results-input",
            placement="top"
        ),
        dbc.Col(
            [
                dbc.Checklist(
                    options=[
                        {"label": " Generate Graph", "value": "ON"},
                    ],
                    value=[],
                    id="graph-checkbox",
                    switch=True,
                    className="mb-2",
                ),
                dbc.Tooltip(
                    "Enabling this option will generate a network graph of sources and tags. "
                    "Be cautious with large datasets as it might slow down the response.",
                    target="graph-checkbox",
                    placement="right"
                ),
            ],
            width={"size": 2, "offset": 1},
            style={'font-family': 'monospace'}
        ),
        dbc.Col(html.Button("Search", id="search-button", n_clicks=0, className="btn btn-primary me-2"), width=1,
                style={'font-family': 'monospace', 'background-color': '636efa'}),
        dbc.Col(
            html.Button(
                "Download CSV",
                id="btn-download-csv",
                n_clicks=0,
                className="btn",
                style={
                    'font-family': 'monospace',
                    'background-color': '#00cc96',
                    'color': '#FFFFFF',
                    'border': 'none'
                }
            ),
            width=1
        ),
        dcc.Download(id="download-csv"),
    ], justify="start"),

    html.Hr(),
    dbc.Row([
        dbc.Col(create_info_card("Search Query", "fas fa-search", "panel-search-query"), width=3,
                style={'font-family': 'monospace'}),
        dbc.Col(create_info_card("Number of Results", "fas fa-sort-numeric-up", "panel-num-results"), width=3,
                style={'font-family': 'monospace'}),
        dbc.Col(create_info_card("Unique Sources", "fas fa-broadcast-tower", "panel-unique-sources"), width=3,
                style={'font-family': 'monospace'}),
        dbc.Col(create_info_card("Unique Tags", "fas fa-tags", "panel-unique-tags"), width=3,
                style={'font-family': 'monospace'}),
    ], className="mb-4 g-4"),

    html.Hr(),
    html.H2("Analytics", className="mb-3", style={'font-family': 'monospace'}),
    dbc.Row([
        dbc.Col([
            dbc.Checklist(
                options=[{"label": " Show Verdict Distribution", "value": 1}],
                value=[1],
                id="toggle-verdict-chart",
                switch=True,
            ),
            dbc.Collapse(
                dcc.Loading(dcc.Graph(id="verdict-pie-chart")),
                id="collapse-verdict-chart",
                is_open=True
            ),
        ], width=6, style={"border-right": "2px solid #dee2e6"}),

        dbc.Col([
            dbc.Checklist(
                options=[{"label": " Show Tags Distribution", "value": 1}],
                value=[1],
                id="toggle-tags-chart",
                switch=True,
            ),
            dbc.Collapse(
                dcc.Loading(dcc.Graph(id="tags-bar-chart")),
                id="collapse-tags-chart",
                is_open=True
            ),
        ], width=6, style={"border-right": "2px solid #dee2e6"}),

    ], className="mb-4"),

    html.Hr(),
    dbc.Row([
        dbc.Col([
            dbc.Checklist(
                options=[{"label": " Show Claims Timeline", "value": 1}],
                value=[1],
                id="toggle-claims-timeline",
                switch=True,
            ),
            dbc.Collapse(
                dcc.Loading(dcc.Graph(id="claims-timeline")),
                id="collapse-claims-timeline",
                is_open=True
            ),
        ], width=6, style={"border-right": "2px solid #dee2e6"}),

        dbc.Col([
            dbc.Checklist(
                options=[{"label": " Show Sources Distribution", "value": 1}],
                value=[1],
                id="toggle-sources-bar-chart",
                switch=True,
            ),
            dbc.Collapse(
                dcc.Loading(dcc.Graph(id="sources-bar-chart")),
                id="collapse-sources-bar-chart",
                is_open=True
            ),
        ], width=6, style={"border-right": "2px solid #dee2e6"}),

    ], className="mb-4"),
    html.Hr(),
    html.P("Source > Node graph", className="mb-3", style={'font-family': 'monospace'}),
    dbc.Row(

        dbc.Col([
            dbc.Checklist(
                options=[{"label": " Show Sources Distribution", "value": 1}],
                value=[0],
                id="toggle-network-graph",
                switch=True,
            ),
            dbc.Collapse(

                cyto.Cytoscape(
                    id='network-graph',
                    layout=layout,
                    style={'width': '100%', 'height': '400px'},
                    elements=[],
                    stylesheet=stylesheet
                ),
                id="collapse-network-graph",
            ),
        ], width=12, className="mb-4", style={"border-right": "2px solid #dee2e6"}),
    ),

    html.Hr(),
    html.H2("Fact Check Details", className="mb-3", style={'font-family': 'monospace'}),
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id='factcheck-table',
            columns=[],
            data=[],
            filter_action="native",
            sort_action="native",
            page_action="native",
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                'minWidth': '80px', 'width': '120px', 'maxWidth': '180px',
                'whiteSpace': 'normal',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxHeight': '60px',
                'textAlign': 'left'
            },
            style_cell_conditional=[
                {'if': {'column_id': c},
                 'textAlign': 'left'} for c in ['column1', 'column2']
            ],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
            ],
            style_header={
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
        ), width=12),
    ]),
])


if __name__ == "__main__":
    app.run_server()
