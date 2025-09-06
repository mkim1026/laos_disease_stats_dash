import os
import dash
import dash_bootstrap_components as dbc
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from components.layout import create_layout
from components.callbacks import register_callbacks

# Flask 서버 생성 및 프록시 보정
server = Flask(__name__)
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

# Dash 앱
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=['https://cdn.plot.ly/plotly-latest.min.js'],
    suppress_callback_exceptions=True,
    requests_pathname_prefix="/",
    routes_pathname_prefix="/",
)

# 레이아웃/콜백
app.layout = create_layout()
register_callbacks(app)

# 헬스체크
@server.route("/health")
def health():
    return "ok", 200

# 로컬 실행 전용
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)
