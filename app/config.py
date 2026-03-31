import os
from dotenv import load_dotenv

load_dotenv()

SCHEMA_IDE = 'mef'
URL_PREFIX = '/reportespyact'   # '/reportespyact' en producción : '' en dev
IS_DEV     = False

class Config:
  SECRET_KEY = os.getenv('SECRET_KEY', '44260f9187f9a46ce7467311f32eca97')

  db_user = os.getenv('DB_USER')
  db_pass = os.getenv('DB_PASS')
  db_host = os.getenv('DB_HOST')
  db_port = os.getenv('DB_PORT')
  db_name = os.getenv('DB_NAME')

  SQLALCHEMY_DATABASE_URI = (
      f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
  )
  SQLALCHEMY_ENGINE_OPTIONS = {
      'pool_size': 10,
      'pool_recycle': 300,
      'pool_pre_ping': True,
      'max_overflow': 20,
      'pool_timeout': 30,
  }
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  CACHE_TYPE = 'SimpleCache'
  CACHE_DEFAULT_TIMEOUT = 300 if IS_DEV else 600

  #BASE_URL = f'127.0.0.1:5000{URL_PREFIX}'
  BASE_URL = f'visor.geoperu.gob.pe{URL_PREFIX}'

  MEF_DEV_URL = 'http://ofi5.mef.gob.pe/inviertews/Dashboard/traeDevengSSI'
  MEF_DET_URL = 'http://ofi5.mef.gob.pe/inviertews/Dashboard/traeDetInvSSI'


config_by_name = {
    'default': Config,
    'development': Config,
    'production': Config,
}
