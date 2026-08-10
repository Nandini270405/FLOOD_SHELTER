from flask import Flask, jsonify, render_template, request

from . import models
from .config import Config
from .db import init_db
from .routes.api import api_bp
from .routes.auth import auth_bp
from .routes.auth_api import api_auth_bp
from .routes.management_api import management_api_bp
from .routes.management_web import management_web_bp
from .routes.web import web_bp
from .schemas.recommendation import CHOICES
from .services.auth import register_auth_handlers
from .services.factory import build_recommendation_service, recommend_shelters


def create_app(config_class=Config) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(config_class.TEMPLATE_DIR),
        static_folder=str(config_class.STATIC_DIR),
    )
    app.config.from_object(config_class)
    init_db(app)
    register_auth_handlers(app)

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(management_web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(api_auth_bp, url_prefix="/api/auth")
    app.register_blueprint(management_api_bp, url_prefix="/api")

    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify({
                "error": "Not Found",
                "message": f"The requested API route '{request.path}' was not found on this server.",
                "path": request.path
            }), 404
        return e

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        if request.path.startswith("/api/"):
            if app.debug:
                import traceback
                return jsonify({
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }), 500
            return jsonify({
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later."
            }), 500
        
        # For non-API routes, try to render index.html with error
        try:
            return render_template(
                "index.html", 
                choices=CHOICES,
                data=None,
                dataset_info=None,
                error=f"An internal server error occurred: {str(e)}" if app.debug else "An internal server error occurred."
            ), 500
        except Exception as render_err:
            app.logger.error(f"Error rendering error page: {render_err}")
            return "Internal Server Error", 500

    return app


__all__ = ["Config", "build_recommendation_service", "create_app", "recommend_shelters"]
