import time
import pandas as pd
from dash import Input, Output
import dash_bootstrap_components as dbc
from dash import html, dcc

from data_loader import load_data_from_gsheets
from components.utils import create_metric_card, create_kpi_card, clean_neighbour_data
from components.views import calculate_news_metrics, \
    make_article_card, generate_weather_alerts, \
    create_weather_cards_column, create_alerts_column, create_weather_chart_column
from plots import (
    plot_disease_outbreak_overtime, plot_disease_pie_map, plot_key_disease_distribution,
    key_disease_dist_overtime, key_disease_kde_distribution, plot_disease_code_map,
    key_disease_wrt_location, disease_category_by_country, present_diseases_chart,
    create_weather_map, create_weather_charts
)

# ---------------------- Overview ---------------------------------------------

def create_overview_content(laos_data, weather_df):
    current_time = int(time.time())
    region_index = (current_time // 30) % len(weather_df)
    # region_index = 1
    region_data = weather_df.iloc[region_index - 1]

    timely_stats_graph = plot_disease_outbreak_overtime(laos_data, code_filter=True)
    laos_map = plot_disease_pie_map(laos_data)
    laos_map_html = laos_map._repr_html_()

    total_cases = laos_data['case'].sum()
    most_viral = laos_data.groupby('disease_code')['case'].sum().idxmax()
    most_viral_cases = laos_data.groupby('disease_code')['case'].sum().max()
    most_affected = laos_data.groupby('province')['case'].sum().idxmax()
    most_affected_cases = laos_data.groupby('province')['case'].sum().max()

    # Get default values
    all_provinces = ['All'] + sorted(laos_data['province'].unique().tolist())
    all_diseases = ['All'] + sorted(laos_data['disease_code'].unique().tolist())


    return html.Div([
        # First row
        dbc.Row([
            # Weather cards
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Card([
                        html.H2(f"{region_data['region']}",
                                id='region-name', className='card-title'),
                        html.P('🎯 Region Spotlight')
                    ], body=True, color='#2a9d8f', inverse=True), width=2),

                    dbc.Col(dbc.Card([
                        html.H2(f"{region_data['temperature']:.1f}°C",
                                id='region-temperature', className='card-title'),
                        html.P("Temperature")
                    ], body=True, color='#e76f51', inverse=True), width=2),

                    dbc.Col(dbc.Card([
                        html.H2(f"{region_data['humidity']}%",
                                id='region-humidity', className='card-title'),
                        html.P('Humidity')
                    ], body=True, color='#5bc0be', inverse=True), width=2),

                    dbc.Col(dbc.Card([
                        html.H2(f"{region_data['pressure']} hPa",
                                id='region-pressure', className='card-title'),
                        html.P('Pressure')
                    ], body=True, color='#56ab91', inverse=True), width=2),

                    dbc.Col(dbc.Card([
                        html.H2(f"{region_data['wind_speed']:.1f} m/s",
                                id='region-windspeed', className='card-title'),
                        html.P('Wind Speed')
                    ], body=True, color='#83c5be', inverse=True), width=2),

                    dbc.Col(dbc.Card([
                        html.H2(f"{region_data['visibility']:.1f} km",
                                id='region-visibility', className='card-title'),
                        html.P('Visibility')
                    ], body=True, color='#e9c46a', inverse=True), width=2),

                ], className="mb-4")
            ], width=12)
        ]),

        # Second Row with map and stats
        dbc.Row([
            dbc.Col([
                html.Iframe(
                    id="laos-map",
                    srcDoc=laos_map_html,
                    width="100%",
                    height="500",
                    style={"border": "none"}
                )
            ], width=6),

            dbc.Col([
                # KPI cards row
                dbc.Row([
                    dbc.Col(create_kpi_card("Total Cases Reported", f"{total_cases:.0f}", card_id="total-cases-kpi"), width=4),
                    dbc.Col(create_kpi_card("Most Viral Disease", f"{most_viral} ({most_viral_cases:.0f})", card_id="most-viral-kpi"), width=4),
                    dbc.Col(create_kpi_card("Most Affected Province", f"{most_affected} ({most_affected_cases:.0f})", card_id="most-affected-kpi"), width=4),
                ], className="g-2 mb-3"),

                # Timely stats graph
                dcc.Graph(
                    id="timely-stats",
                    figure=timely_stats_graph,
                    config={'displayModeBar': False},
                    style={"height": "400px"}
                ),
            ], width=6)
        ], className="mb-2", style={"margin-top": "15px"})
    ])


# ---------------------- Key Diseases ---------------------------------------------

def create_key_diseases_content(laos_data):
    key_diseases = ["HPAI-P", "ND", "IBD", "MG"]
    data = laos_data[laos_data['disease_code'].isin(key_diseases)]

    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(figure=plot_key_disease_distribution(data)), width=4),
            dbc.Col(dcc.Graph(figure=key_disease_kde_distribution(data)), width=4),
            dbc.Col(dcc.Graph(figure=key_disease_dist_overtime(data)), width=4),
        ], className="mb-2", style={"margin-top": "15px"}),
        
        dbc.Row([
            dbc.Col(dcc.Graph(figure=plot_disease_code_map(data)), width=5),
            dbc.Col(dcc.Graph(figure=key_disease_wrt_location(data)), width=7),
        ], className="mb-2", style={"margin-top": "15px"})
    ])


# ---------------------- Neighboring Stats ---------------------------------------------

def create_neighboring_stats_content(neighbours_data):
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Select Country"),
                dcc.Dropdown(
                    id='neighbour-country-dropdown',
                    options=[
                        {'label': 'Thailand', 'value': 'Thailand'},
                        {'label': 'Vietnam', 'value': 'Vietnam'}
                    ],
                    value=['Thailand', 'Vietnam'],
                    clearable=False,
                    multi=True,
                    style={"margin-bottom": "10px"}
                ),
                dcc.Graph(id='disease-category-by-country', style={"height": "100%"})
            ], width=4, style={"display": "flex", "flexDirection": "column"}),

            dbc.Col([
                dcc.Graph(id='present-diseases-chart', style={"height": "100%"})
            ], width=8)
        ], align="stretch", style={"height": "100%"})
    ])

    

# ---------------------- Weather Information ---------------------------------------------

def create_weather_content(weather_df, laos_df):
    # Data processing
    weather_df['sunrise'] = pd.to_datetime(weather_df['sunrise'])
    weather_df['sunset'] = pd.to_datetime(weather_df['sunset'])
    
    # Get current region data
    current_time = int(time.time())
    region_index = (current_time // 30) % len(weather_df)
    region_data = weather_df.iloc[region_index - 1]

    # Prepare data for visualizations
    weather_data = weather_df.set_index('region').to_dict(orient='index')
    LAOS_REGIONS = laos_df.set_index('province').to_dict(orient='index')


    # Create visualizations
    weather_map = create_weather_map(weather_data, LAOS_REGIONS)
    temp_chart, humidity_chart = create_weather_charts(weather_data)
    alerts = generate_weather_alerts(weather_data)

    return html.Div([
        # First row with map, weather cards, and alerts
        dbc.Row([
            # Weather map column
            dbc.Col(
                dcc.Graph(
                    id="weather-map",
                    figure=weather_map,
                    config={'displayModeBar': False},
                    style={"height": "520px"}
                ),
                width=6),
            
            # Weather cards column
            dbc.Col(create_weather_cards_column(region_data), width=3),
            
            # Alerts column
            dbc.Col(create_alerts_column(alerts), width=3)
        ]),
        
        # Second row with temperature and humidity charts
        dbc.Row([
            dbc.Col(create_weather_chart_column(temp_chart, "regional-temp-chart"), width=6),
            dbc.Col(create_weather_chart_column(humidity_chart, "regional-humidity-chart"), width=6),
        ], className="mb-2", style={"margin-top": "15px"})
    ])


# --------------------------- News ------------------------------------

def create_news_content(news_df):
    # Data processing
    news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce')
    
    # Calculate metrics
    news_metrics = calculate_news_metrics(news_df)
    articles = news_df.to_dict("records")

    return html.Div([
        # Metrics row
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([html.H6("Quick Info", className="card-title")])
            ], className="shadow-sm", style={"margin-top": "20px"}), width=2),

            create_metric_card(str(news_metrics['total_articles']), "Total Articles", "#00b4d8", width=2),
            create_metric_card(str(news_metrics['press_releases']), "Press Releases", "#00b4d8", width=2),
            create_metric_card(str(news_metrics['newsletters']), "Newsletters", "#00b4d8", width=2),
            create_metric_card(str(news_metrics['statements']), "Statements", "#00b4d8", width=2),
            create_metric_card(
                f"{news_metrics['days_ago']} days ago" if news_metrics['days_ago'] else "Recent",
                "Latest Article",
                "#00b4d8",
                width=2)
        ], className="mb-4"),
        
        # Articles row
        dbc.Row(dbc.Col([
            html.H5(f"📰 Latest Articles ({len(articles)})", className="mb-3"),

            dcc.Input(
                id="news-search",
                type="text",
                placeholder="🔍 Search articles...",
                debounce=True,
                className="form-control mb-3"
            ),
            html.Div(id="news-articles-container")
        ], width=12),
            className="mb-2",
            style={"margin-top": "15px"})
    ], className="p-4")




# --------------------------- Callbacks ------------------------------------

def register_callbacks(app):
    laos_data, laos_df, weather_df, news_df, neighbours_data = load_data_from_gsheets()

    @app.callback(
        Output('content', 'children'),
        [Input('tabs', 'value')]
    )
    def render_content(tab):
        if tab == 'Overview':
            return create_overview_content(laos_data, weather_df)
        elif tab == 'Key Diseases':
            return create_key_diseases_content(laos_data)
        elif tab == 'Neighboring Stats':
            return create_neighboring_stats_content(neighbours_data)
        elif tab == 'Weather Information':
            return create_weather_content(weather_df, laos_df)
        elif tab == 'Global Health News':
            return create_news_content(news_df)
        return html.Div([html.H3('Select a tab to see the content.')])


    @app.callback(
        [Output('disease-category-by-country', 'figure'),
         Output('present-diseases-chart', 'figure')],
        [Input('neighbour-country-dropdown', 'value')]
    )
    def update_neighboring_charts(country):
        data = clean_neighbour_data(neighbours_data)
        return (
            disease_category_by_country(data[data['Country'].isin(country)]),
            present_diseases_chart(data[data['Country'].isin(country)])
        )
        
    @app.callback(
        Output("news-articles-container", "children"),
        Input("news-search", "value")
    )
    def update_article_cards(search_query):
        filtered_articles = news_df.to_dict("records")

        if search_query:
            query = search_query.lower()
            filtered_articles = [
                a for a in filtered_articles
                if query in a['title'].lower() or query in a['main_text'].lower()
            ]

        if not filtered_articles:
            return dbc.Alert("No articles found.", color="warning")

        return [make_article_card(article) for article in filtered_articles]      
