import os
import dash
import dash_bootstrap_components as dbc

from components.layout import create_layout
from components.callbacks import register_callbacks

# Initialize the Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                external_scripts=['https://cdn.plot.ly/plotly-latest.min.js'],
                suppress_callback_exceptions=True)

server = app.server

# Set up layout
app.layout = create_layout()

# Register all callbacks
register_callbacks(app)

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=True)