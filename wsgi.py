from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app
from app.config import URL_PREFIX

# Flask app — usado por el CLI: flask --app wsgi:app run
app = create_app()


class NormalizeDuplicatedPrefixMiddleware:
  """
  Normaliza PATH_INFO cuando el prefijo llega duplicado, por ejemplo:
  /reportespyact/reportespyact/2025/19 -> /reportespyact/2025/19
  """

  def __init__(self, wsgi_app, prefix: str):
      self.wsgi_app = wsgi_app
      self.prefix = (prefix or '').rstrip('/')

  def __call__(self, environ, start_response):
      if self.prefix:
          doubled = f'{self.prefix}{self.prefix}'
          path = environ.get('PATH_INFO', '') or ''
          if path.startswith(doubled):
              environ['PATH_INFO'] = path[len(self.prefix):]
      return self.wsgi_app(environ, start_response)


# WSGI application con ProxyFix — usado por gunicorn en producción
application = ProxyFix(app, x_for=1, x_host=1, x_prefix=1)
application = NormalizeDuplicatedPrefixMiddleware(application, URL_PREFIX)
