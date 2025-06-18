import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import sqlite3

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "MLB Stats Dashboard"

#-----Load data from SQLite database-----
def load_data():
    conn = sqlite3.connect("../db/mlb_data.db")
    events = pd.read_sql_query("SELECT * FROM events_cleaned", conn)
    stats = pd.read_sql_query("SELECT * FROM statistics_cleaned", conn)
    conn.close()

    # Normalize teams right after loading, since there was overlap with team names
    team_map = {
        'Los Angeles Dodgers': 'Los Angeles',
        'Houston Astros': 'Houston',
        'New York Yankees': 'New York',
        'Cleveland Indians': 'Cleveland',
        'Toronto Blue Jays': 'Toronto',
        'Minnesota Twins': 'Minnesota',
        'Detroit Tigers': 'Detroit',
        'Baltimore Orioles': 'Baltimore'
    }
    stats['Team'] = stats['Team'].replace(team_map)
    return events, stats

events_df, stats_df = load_data()

# Precompute dropdown options
year_options = sorted(stats_df['year'].unique())
team_options = sorted([
    'Los Angeles', 'Houston', 'New York', 'Cleveland', 'Toronto',
    'Minnesota', 'Detroit', 'Baltimore', 'San Diego'
])

#-----App layout-----
app.layout = html.Div([
    html.H1("MLB Statistics Dashboard", style={"textAlign": "center"}),
    html.P("Explore MLB player statistics and events by year and team."),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(y), 'value': y} for y in year_options],
            value=year_options[0],
            clearable=False
        ),
    ], style={"width": "30%", "display": "inline-block"}),

    html.Div([
        html.Label("Select Team(s):"),
        dcc.Dropdown(
            id='team-dropdown',
            options=[{'label': t, 'value': t} for t in team_options],
            value=[team_options[0]],
            multi=True
        ),
    ], style={"width": "60%", "display": "inline-block", "paddingLeft": "20px"}),

    html.Br(),

    dcc.Graph(id='top-home-runs'),
    dcc.Graph(id='team-home-runs-bar'),
    html.Div(id='event-distribution-table')
])

#----- Callbacks-----

#Home Run Bar Graph
@app.callback(
    Output('top-home-runs', 'figure'),
    Input('year-dropdown', 'value')
)
def update_home_runs(year):
    df = stats_df[(stats_df['year'] == year) & (stats_df['Statistic'].str.strip().str.lower() == 'home runs')]
    df = df.sort_values(by='stat_value', ascending=False).head(10)
    fig = px.bar(df, x='Name', y='stat_value', color='Team', title=f"Top 2 Home Run Hitters ({year})")
    fig.update_layout(xaxis_title="Player", yaxis_title="Home Runs")
    return fig

#Total Team Home Runs for all (2015 - 2025)
@app.callback(
    Output('team-home-runs-bar', 'figure'),
    Input('year-dropdown', 'value')
)
def update_team_home_runs(_):
    df = stats_df[(stats_df['Statistic'] == 'Home Runs') & (stats_df['year'].between(2015, 2025))]

    team_map = {
        'Los Angeles Dodgers': 'Los Angeles',
        'Houston Astros': 'Houston',
        'New York Yankees': 'New York',
        'Cleveland Indians': 'Cleveland',
        'Toronto Blue Jays': 'Toronto',
        'Minnesota Twins': 'Minnesota',
        'Detroit Tigers': 'Detroit',
        'Baltimore Orioles': 'Baltimore'
    }
    df['Team'] = df['Team'].replace(team_map)

    # Group by year and team
    team_hr = df.groupby(['year', 'Team'])['stat_value'].sum().reset_index()

    fig = px.bar(
        team_hr,
        x='year',
        y='stat_value',
        color='Team',
        barmode='group',
        title='Total Team Home Runs (2015–2025)',
        labels={'stat_value': 'Home Runs', 'year': 'Year'}
    )

    return fig

# Event Detail Table Reflecting event details if team is selected by user for that year
@app.callback(
    Output('event-distribution-table', 'children'),
    [Input('year-dropdown', 'value'),
     Input('team-dropdown', 'value')]
)
def update_event_table(year, teams):
    df = events_df[events_df['year'] == year]

    # Filter by team name in event_detail
    if teams:
        df = df[df['event_detail'].str.contains('|'.join(teams), case=False, na=False)]

    event_counts = df['event_detail'].value_counts().reset_index()
    event_counts.columns = ['Event Detail', 'Count']

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in event_counts.columns],
        data=event_counts.to_dict('records'),
        style_table={'overflowX': 'auto', 'maxHeight': '500px', 'overflowY': 'scroll','paddingBottom': '40px'},
        style_cell={
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
            'padding': '5px',
            'fontSize': 14
        },
        style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold'
        },
        page_size=20  
    )

# Run server
if __name__ == '__main__':
    app.run(debug=True)
