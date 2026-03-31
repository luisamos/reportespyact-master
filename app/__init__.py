from flask import Flask
from .extensions import db, cache
from .config import config_by_name, URL_PREFIX, IS_DEV
from .utils.formatters import FuncionesPY


def create_app(config_name: str = 'default') -> Flask:
    static_url_path = f'{URL_PREFIX}/static' if URL_PREFIX else '/static'
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
        static_url_path=static_url_path,
    )
    app.config.from_object(config_by_name[config_name])

    # Inicializar extensiones
    db.init_app(app)
    cache.init_app(app)

    # Registrar blueprints
    from .routes.main import main_bp
    app.register_blueprint(main_bp, url_prefix=URL_PREFIX)

    # Context processors globales
    _fn = FuncionesPY()

    @app.context_processor
    def utility_processor():
        return dict(
            format_price=_fn.formatMoneda,
            barra=_fn.barra,
            is_dev=IS_DEV,
        )

    # Manejadores de error
    from flask import make_response, render_template

    @app.errorhandler(404)
    def not_found(e):
        return make_response(render_template('404.html'), 404)

    @app.errorhandler(500)
    def server_error(e):
        return make_response(render_template('404.html'), 500)

    return app
