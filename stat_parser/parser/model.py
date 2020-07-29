from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import exists, and_
from stat_parser import session


Base = declarative_base()


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(2048), nullable=False)

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def is_exist(self) -> bool:
        # result = session.query(exists().where(and_(**kwargs))).scalar()
        result = session.query(Source.query.filter(Source.name == self.name).exists()).scalar()
        return result


class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __init__(self, name: str):
        self.name = name


class Sport(Base):
    __tablename__ = 'sports'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __init__(self, name: str):
        self.name = name


class Link(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    urn = Column(String(2048), nullable=False)

    source_id = Column(Integer, ForeignKey('sources.id'))
    sport_id = Column(Integer, ForeignKey('sports.id'))
    entity_id = Column(Integer, ForeignKey('entities.id'))

    source = relationship(Source, primaryjoin=source_id == Source.id)
    sport = relationship(Sport, primaryjoin=sport_id == Sport.id)
    entity = relationship(Entity, primaryjoin=entity_id == Entity.id)

    def __init__(self, uri: str):
        self.urn = uri





