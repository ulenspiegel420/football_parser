from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from configs.config import Config


engine = create_engine(Config.SQL_ALCHEMY_PARSER, echo=True)
session = scoped_session(sessionmaker(bind=engine))

