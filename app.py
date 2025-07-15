import dash
import dash_bootstrap_components as dbc
from dash import html

from components.layout import create_layout
from components.callbacks import register_callbacks

# Initialize the Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                external_scripts=['https://cdn.plot.ly/plotly-latest.min.js'],
                suppress_callback_exceptions=True)

# Set up layout
app.layout = create_layout()

# Register all callbacks
register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)