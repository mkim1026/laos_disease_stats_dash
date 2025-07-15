import pandas as pd
import dash_bootstrap_components as dbc
from dash import html

def clean_neighbour_data(df):
    df = df.copy()
    df['Year'] = df['Year'].astype(int)
    df['Semester'] = df['Semester'].str.replace('Jan-Jun-', 'S1-').str.replace('Jul-Dec-', 'S2-')
    return df[df['Year'].isin([2024, 2025])]



def create_kpi_card(title, value, card_id=None):
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.H4(value, className="card-text")
        ])
    ], className="shadow-sm", id=card_id)


def create_metric_card(value, title, color, width=12):
    return dbc.Col([dbc.Card([
        html.H2(value, className='card-title'),
        html.P(title)
    ], body=True, color=color, inverse=True)], width=width)



def get_date_marks(min_date, max_date):
    """Generate marks for the date slider at yearly intervals"""
    marks = {}
    current = min_date.replace(day=1)
    while current <= max_date:
        timestamp = current.timestamp()
        marks[timestamp] = {'label': current.strftime('%Y'), 'style': {'transform': 'rotate(45deg)'}}
        current = current + pd.DateOffset(years=1)
    return marks