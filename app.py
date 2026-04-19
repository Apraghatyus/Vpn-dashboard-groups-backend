"""
WG-ACL Manager — Backend API
Flask app with JWT auth and CORS.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from controllers import ALL_BLUEPRINTS
import db as database


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    database.init_db(Config.DATABASE_URL)

    CORS(app, resources={
        r"/api/*": {"origins": Config.CORS_ORIGINS},
    })

    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/")
    def index():
        return jsonify({
            "name": "WG-ACL Manager API",
            "version": "1.0.0",
            "endpoints": [
                "/health",
                "/api/auth/login",
                "/api/auth/me",
                "/api/peers",
                "/api/roles",
                "/api/services",
                "/api/access",
                "/api/yaml",
                "/api/vpn-users",
                "/api/dns",
                "/api/dns/sync",
                "/api/dns/adguard/rewrites",
            ],
        })

    return app


# Create the app instance (used by gunicorn: `gunicorn app:app`)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
