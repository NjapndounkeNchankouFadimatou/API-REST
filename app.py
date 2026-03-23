"""
app.py – Application factory
Wires together config, database, routes, and Swagger.
"""
from flask import Flask, jsonify
from flasgger import Swagger

from config import active_config
from database import init_db
from articles_routes import articles_bp


def create_app(config=None):
    app = Flask(__name__)

    # ── 1. Configuration ──────────────────────────────────────────────────
    app.config.from_object(config or active_config)

    # ── 2. Database ───────────────────────────────────────────────────────
    init_db(app)

    # ── 3. Routes (blueprints) ────────────────────────────────────────────
    app.register_blueprint(articles_bp)

    # ── 4. Swagger UI ─────────────────────────────────────────────────────
    Swagger(app)

    # ── 5. Health-check ───────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "healthy", "app": "Blog API – INF222 TAF1"}), 200

    # ── 6. Global error handlers ──────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Route introuvable."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Méthode non autorisée."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "message": "Erreur interne du serveur."}), 500

    return app


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    application = create_app()
    print("\n🚀  Blog API  →  http://127.0.0.1:5000")
    print("📖  Swagger UI →  http://127.0.0.1:5000/apidocs\n")
    application.run(debug=True)
