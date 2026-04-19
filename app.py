"""
WG-ACL Manager — Backend API
Flask app with JWT auth, CORS, and auto-seed.
"""

import sys
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from controllers import ALL_BLUEPRINTS
from data.seed import seed_all
import db as database


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize MariaDB connection and create tables
    database.init_db(Config.DATABASE_URL)

    # CORS — allow frontend origins
    CORS(app, resources={
        r"/api/*": {"origins": Config.CORS_ORIGINS},
    })

    # Register all route blueprints
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    # Health check (no auth required)
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

    # Seed data on startup
    with app.app_context():
        seed_all()

    return app


# Create the app instance (used by gunicorn: `gunicorn app:app`)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
