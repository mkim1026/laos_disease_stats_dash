import dash_bootstrap_components as dbc
from dash import dcc, html

def create_tabs():
    return dcc.Tabs(
        id='tabs',
        value='Overview',
        children=[
            dcc.Tab(label='Laos Overview', value='Overview', className='custom-tab'),
            dcc.Tab(label='Key Diseases', value='Key Diseases', className='custom-tab'),
            dcc.Tab(label='Neighboring Stats', value='Neighboring Stats', className='custom-tab'),
            dcc.Tab(label='Weather Information', value='Weather Information', className='custom-tab'),
            dcc.Tab(label='Global Health News', value='Global Health News', className='custom-tab'),
        ],
        className='custom-tabs-container',
    )


def create_layout():
    return dbc.Container([
        dcc.Interval(
            id='interval-refresh',
            interval=3600 * 1000,  # 1 hour = 3600000 ms
            n_intervals=0
        ),
        dbc.Row([
            dbc.Col(html.H1("Disease Statistics in Laos"), width=9, className="text-center"),
            dbc.Col(html.Img(src='./assets/logo/logo1.png', height='50px'), className="text-right", width=1),
            dbc.Col(html.Img(src='./assets/logo/logo2.png', height='50px'), className="text-right", width=1),
            dbc.Col(html.Img(src='./assets/logo/logo3.png', height='50px'), className="text-right", width=1),
        ], className="header"),
        dbc.Row([create_tabs()], className="mb-4"),
        dbc.Row([dbc.Col(html.Div(id='content'), width=12)]),
    ], fluid=True)


# def create_layout():
#     return dbc.Container([
#         dbc.Row([
#             dbc.Col(html.H1("Disease Statistics in Laos"), width=9, className="text-center"),
#             dbc.Col(html.Img(src='./assets/logo/logo1.png', height='50px'), className="text-right", width=1),
#             dbc.Col(html.Img(src='./assets/logo/logo2.png', height='50px'), className="text-right", width=1),
#             dbc.Col(html.Img(src='./assets/logo/logo3.png', height='50px'), className="text-right", width=1),
#             ], className="header"),
#         dbc.Row([create_tabs()], className="mb-4"),
#         dbc.Row([dbc.Col(html.Div(id='content'), width=12)]),
#     ], fluid=True)