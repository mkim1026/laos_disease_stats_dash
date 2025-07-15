import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime

from components.utils import create_metric_card


def create_weather_cards_column(region_data):
    return [
        dbc.Row([
            dbc.Col(create_weather_card("Region Spotlight", region_data['region']),
                    width=12)
        ], className="mb-2"),

        dbc.Row([
            dbc.Col(create_metric_card(
                f"{region_data['temperature']:.1f}°C", "Temperature", "#e76f51"),
                width=6),
            dbc.Col(create_metric_card(
                f"{region_data['humidity']}%", "Humidity", "#f4a261"),
                width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_metric_card(
                f"{region_data['pressure']} hPa", "Pressure", "#e9c46a"),
                width=6),
            dbc.Col(create_metric_card(
                f"{region_data['wind_speed']:.1f} m/s", "Wind Speed", "#e9c46a"),
                width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(create_metric_card(
                f"{region_data['visibility']:.1f} km", "Visibility", "#ffbf69"),
                width=6),
            dbc.Col(dbc.Card([
                html.H5(f"Sunrise: {region_data['sunrise'].strftime('%H:%M')}"),
                html.H5(f"Sunset: {region_data['sunset'].strftime('%H:%M')}")
            ], body=True, color='#ffbf69', inverse=True), width=6),
        ], className="mb-4")
    ]


def create_alerts_column(alerts):
    return html.Div([
        html.H5("⚠️ Weather Alerts"),
        html.Div([
            dbc.Alert(alert, color="danger", className="mb-2") for alert in alerts
        ]) if alerts else dbc.Alert("✅ No weather alerts at this time", color="success")
    ], style={"height": "500px", "overflowY": "auto"})


def create_weather_chart_column(chart, chart_id):
    return dcc.Graph(
        id=chart_id,
        figure=chart,
        config={'displayModeBar': False},
        style={"height": "400px"}
    )


def create_weather_card(title, value):
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.H4(value, className="card-text")
        ])
    ], className="shadow-sm")


def generate_weather_alerts(data):
    alerts = []

    for region, d in data.items():
        if d:
            if d['temperature'] > 35:
                alerts.append(f"🔥 High Temperature Alert: {region} - {d['temperature']:.1f}°C")
            elif d['temperature'] < 10:
                alerts.append(f"🧊 Low Temperature Alert: {region} - {d['temperature']:.1f}°C")

            if d['humidity'] > 90:
                alerts.append(f"💧 High Humidity Alert: {region} - {d['humidity']}%")

            if d['wind_speed'] > 10:
                alerts.append(f"💨 Strong Wind Alert: {region} - {d['wind_speed']:.1f} m/s")

    return alerts



def calculate_news_metrics(news_df):
    return {
        'total_articles': len(news_df),
        'press_releases': len([a for a in news_df['tag'] if a == 'Press Release']),
        'newsletters': len([a for a in news_df['tag'] if a == 'Newsletter']),
        'statements': len([a for a in news_df['tag'] if a == 'Joint Statement' or a == 'Statement']),
        'days_ago': (datetime.now() - (news_df.iloc[0]['date'] if not news_df.empty else datetime.today())).days
    }


def make_article_card(article):
    return dbc.Card(
        dbc.Row([
            dbc.Col(
                html.Img(
                    src=article['image_url'],
                    style={
                        "width": "200",
                        "height": "200",
                        "objectFit": "cover"
                    }),
                width=4,
                className='d-flex align-items-center justify-content-center'
            ),
            dbc.Col([
                html.H5(article['title'], className="card-title"),
                html.P(article['date_text'], className="text-muted", style={"fontSize": "0.8rem"}),
                html.P(f"{article['main_text'][:500]}...", className="card-text"),
                dbc.Badge(article['tag'], color="info", className="me-1"),
                html.Br(),
                dbc.Button(
                    "Read More",
                    href=article['url'],
                    target="_blank",
                    color="primary",
                    size="sm",
                    className="mt-2"
                )
            ], width=8)
        ], className="g-0"),
        className="mb-3 border-0 border-bottom",
        style={
            "border": "1px solid #dee2e6",
            "borderRadius": "5px",
            "boxShadow": "none",
            "padding": "2%"
            # "maxHeight": "200px"
        }
    )