from stat_parser import session
from stat_parser.parser.model import Source, Entity, Sport, Link
from stat_parser.parser import types


if __name__ == '__main__':
    source = Source(types.ParseSource.championat_com.name, "https://www.championat.com/")
    entity = Entity(types.Entity.source.name)
    sport = Sport(types.Sport.football.name)

    link = Link('stat/football/tournaments/2/domestic/')
    link.source = source
    link.entity = entity
    link.sport = sport

    session.add(link)
    session.commit()
