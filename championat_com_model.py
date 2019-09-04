from sqlalchemy import Column, String, Integer, DateTime, Date, Boolean, Index, exists, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.expression import ClauseElement
from datetime import datetime

Base = declarative_base()


class Tournament(Base):
    __tablename__ = 'tournaments'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(150), nullable=False)
    Start = Column(Date, nullable=False, default=datetime(1000, 1, 1))
    End = Column(Date, nullable=False, default=datetime(1000, 1, 1))
    Url = Column(String(300), nullable=False)
    Members = Column(Integer)


class Team(Base):
    __tablename__ = 'teams'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(150), nullable=False)
    City = Column(String(150), nullable=False)


class Stat(Base):
    __tablename__ = 'stats'
    Id = Column(Integer, primary_key=True)
    Attacks = Column(Integer)
    DangerousAttacks = Column(Integer)
    GoalChances = Column(Integer)
    Shoots = Column(Integer)
    ShootsOnGoal = Column(Integer)
    Bars = Column(Integer)
    Fouls = Column(Integer)
    Corners = Column(Integer)
    Offsides = Column(Integer)
    Control = Column(Integer)
    LockedShoots = Column(Integer)
    FreeKicks = Column(Integer)
    GoalKicks = Column(Integer)
    Outs = Column(Integer)
    Cautions = Column(Integer)
    Offs = Column(Integer)


class Player(Base):
    __tablename__ = 'players'
    Id = Column(Integer, primary_key=True)
    Name = Column(String(150), nullable=False)


class Lineup(Base):
    __tablename__ = 'lineups'
    Id = Column(Integer, primary_key=True)
    MatchId = Column(Integer, ForeignKey('matches.Id'))
    PlayerId = Column(Integer, ForeignKey('players.Id'))
    TeamId = Column(Integer, ForeignKey('teams.Id'))
    Amplua = Column(String(10))
    In = Column(String(10))
    Out = Column(String(10))

    Player = relationship('Player', uselist=False, foreign_keys='Lineup.PlayerId')
    Match = relationship('Match', uselist=False, foreign_keys='Lineup.MatchId')
    Team = relationship('Team', uselist=False, foreign_keys='Lineup.TeamId')
    Goals = relationship('Goal', backref='lineups')
    Assists = relationship('Assist', backref='lineups')
    MissPenalties = relationship('MissPenalty', backref='lineups')
    Punishments = relationship('Punishment', backref='lineups')
    Penalties = relationship('Penalty', backref='lineups')


class MissPenalty(Base):
    __tablename__ = 'misses_penalties'
    Id = Column(Integer, primary_key=True)
    LineupId = Column(Integer, ForeignKey('lineups.Id'))
    Minute = Column(String(10))


class Penalty(Base):
    __tablename__ = 'penalties'
    Id = Column(Integer, primary_key=True)
    LineupId = Column(Integer, ForeignKey('lineups.Id'))
    Result = Column(String(10))
    Score = Column(String(10))


class Punishment(Base):
    __tablename__ = 'punishments'
    Id = Column(Integer, primary_key=True)
    LineupId = Column(Integer, ForeignKey('lineups.Id'))
    Card = Column(String(30))
    Minute = Column(String(10))


class Goal(Base):
    __tablename__ = 'goals'
    Id = Column(Integer, primary_key=True)
    LineupId = Column(Integer, ForeignKey('lineups.Id'))
    BecameScore = Column(String(30))
    Minute = Column(String(10))
    IsAuto = Column(Boolean)
    IsPenalty = Column(Boolean)


class Assist(Base):
    __tablename__ = 'assists'
    Id = Column(Integer, primary_key=True)
    LineupId = Column(Integer, ForeignKey('lineups.Id'))
    GoalId = Column(Integer, ForeignKey('goals.Id'))

    Goal = relationship('Goal', uselist=False, backref='assists')


class Match(Base):
    __tablename__ = 'matches'
    Id = Column(Integer, primary_key=True)
    TournamentId = Column(Integer, ForeignKey('tournaments.Id'))
    HomeTeamId = Column(Integer, ForeignKey('teams.Id'))
    GuestTeamId = Column(Integer, ForeignKey('teams.Id'))
    HomeStatId = Column(Integer, ForeignKey('stats.Id'))
    GuestStatId = Column(Integer, ForeignKey('stats.Id'))
    Stadium = Column(String(50))
    Referee = Column(String(100))
    Date = Column(DateTime)
    Stage = Column(String(150))
    IsExtra = Column(Boolean)
    HomeScore = Column(Integer)
    GuestScore = Column(Integer)
    HomePenaltyScore = Column(Integer)
    GuestPenaltyScore = Column(Integer)
    HomeTechScore = Column(String(10))
    GuestTechScore = Column(String(10))
    Url = Column(String(300), nullable=False)

    Tournament = relationship('Tournament', backref='matches')

    HomeStat = relationship('Stat', uselist=False, foreign_keys='Match.HomeStatId')
    GuestStat = relationship('Stat', uselist=False, foreign_keys='Match.GuestStatId')
    HomeTeam = relationship('Team', uselist=False, foreign_keys='Match.HomeTeamId')
    GuestTeam = relationship('Team', uselist=False, foreign_keys='Match.GuestTeamId')


Index('TournamentUniqueIdx', Tournament.Name, Tournament.Start, Tournament.End, unique=True)
Index('TeamUniqueIdx', Team.Name, Team.City, unique=True)


def GetOrCreate(session: Session, model, **kwargs):
    Entity = session.query(model).filter_by(**kwargs).first()
    if Entity: return Entity
    else:
        Params = dict((k, v) for k, v in iter(kwargs.items()) if not isinstance(v, ClauseElement))
        Entity = model(**Params)
        return Entity


def IsEntityExist(session: Session, **kwargs):
    Result = session.query(exists().where(and_(**kwargs))).scalar()
    return Result


def CreateAll(engine):
    Base.metadata.create_all(engine)
