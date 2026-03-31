from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app

# Flask app — usado por el CLI: flask --app wsgi:app run
app = create_app()

# WSGI application con ProxyFix — usado por gunicorn en producción
application = ProxyFix(app, x_for=1, x_host=1, x_prefix=1)
