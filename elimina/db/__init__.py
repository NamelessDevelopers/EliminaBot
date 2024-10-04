from sqlalchemy import create_engine

from elimina import config

engine = create_engine(config.DB_URI, echo=False)
