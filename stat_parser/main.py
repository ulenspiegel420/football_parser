import logging.config
import logging
import os
import json
from stat_parser import session
from stat_parser.parser.core import SeasonsLinkParser
from stat_parser.parser import types
from stat_parser.parser.model import Source, Sport, Entity, Link


def logging_setup(default_cfg_path='../configs/logging.json', default_level=logging.INFO, log_key='STAT_PARSER_LOG'):
    custom_log_path = os.getenv(log_key)
    if custom_log_path is not None:
        path = custom_log_path
    else:
        path = default_cfg_path

    if os.path.exists(default_cfg_path):
        with open(path, 'rt') as handler:
            log_dict = json.load(handler)
            logging.config.dictConfig(log_dict)
    else:
        logging.basicConfig(level=default_level)


def parse_football_season_links(src: Source):
    logger.info('Parsing football season links')
    sport: Sport = session.query(Sport).filter_by(name='football').first()
    entity = session.query(Entity).filter_by(name=types.Entity.season_link.name).first()

    parser = SeasonsLinkParser(src, sport)
    uris = parser.parse()

    logger.info(f'Parsed {len(uris)} items')

    for uri in uris:
        link = Link(uri)
        link.source = src
        link.sport = sport
        link.entity_id = entity.id
        session.add(link)
    session.commit()


def run():
    logger.info("Start programm...")

    source: Source = session.query(Source).filter_by(name='championat_com').first()
    s = Source('championat_com', 'sdsd')

    parse_football_season_links(source)


if __name__ == '__main__':
    logging_setup()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    try:
        run()
    except Exception as e:
        logger.error(str(e))
    finally:
        logger.info("Stop programm.")
