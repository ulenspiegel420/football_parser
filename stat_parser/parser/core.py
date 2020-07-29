from enum import Enum
import random
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from stat_parser.parser.types import ParseSource
from stat_parser import session
from stat_parser.parser.model import Sport, Entity, Source, Link


class ParsingTypes(Enum):
    root = 0
    tournament = 1
    team = 2
    Lineup = 3
    match = 4
    season = 5
    Goal = 6
    Punishment = 7
    MissPenalty = 8
    MatchStat = 9
    Assist = 10
    Penalty = 11
    attacks = 12


StatAssociations = {
    'Атаки': 'Attacks',
    'Опасные атаки': 'DangerousAttacks',
    'Голевые моменты': 'GoalChances',
    'Удары по воротам': 'Shoots',
    'Удары в створ': 'ShootsOnGoal',
    'Штанги/перекладины': 'Bars',
    'Фолы': 'Fouls',
    'Угловые': 'Corners',
    'Офсайды': 'Offsides',
    '% владения мячом': 'Control',
    'Заблокированные удары': 'LockedShoots',
    'Штрафные удары': 'FreeKicks',
    'Удары от ворот': 'GoalKicks',
    'Ауты': 'Outs',
    'Предупреждения': 'Cautions',
    'Удаления': 'Offs'}

MonthInCase = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04', 'мая': '05', 'июня': '06',
                             'июля': '07', 'августа': '08', 'сентября': '09', 'октября': '10', 'ноября': '11',
                             'декабря': '12'}

TimeZones = {'МСК': '+0300', }


def get_rand_user_agent_from_file(path: str):
    count_lines = 0
    with open(path, 'r') as file:
        count_lines = sum(1 for line in file)
    rand_line_num = random.randint(1, count_lines)

    with open(path, 'r') as file:
        current_line_num = 1
        for line in file:
            if rand_line_num == current_line_num:
                return line.strip()
            current_line_num += 1


def get_request(url, proxy=None):
    # Proxies = {'https': f'https://{proxy}'} if proxy else {}
    try:
        user_agent = get_rand_user_agent_from_file("../assets/useragents.txt")
        Proxies = {}
        request = requests.get(url, headers={'User-Agent': user_agent}, proxies=Proxies)
        # for k,v in request.headers.items():
        #     print(k, ": ", v)
        if request.status_code != 200:
            raise Exception(f"Error get request: {str(request.status_code)}")
        return request

    except requests.exceptions.HTTPError as e:
        raise Exception(e)
    except requests.exceptions.RequestException as e:
        raise Exception(e)
    except Exception as Err:
        raise Exception(Err)


class Parser(ABC):
    def __init__(self, src: Source, sport: Sport):
        self.__urls = []
        self.__desc = {
            'en': 'Attacks',
            'ru': 'Атаки'
        }
        self._parse_func = None
        self._parse_sources_func = {}
        self._source_key: Source = src
        self._source_url: str = session.query(Source).filter_by(name=src.name)
        self._src: Source = src
        self._sport_id: int = sport.id
        self.__uri: str = self.__get_src_uri()
        self._url: str = src.url

    @abstractmethod
    def parse(self):
        r = get_request(self.__uri)
        self._soup = BeautifulSoup(r.text, 'html.parser')
        parse_func = self._get_parse_func(self._source_key)
        result = parse_func()
        return result

    def _add_desc(self, lang_key: str, value: str):
        self.__desc[lang_key] = value

    def _register_parse_func(self, key: ParseSource, func):
        if key == ParseSource.championat_com:
            self._parse_sources_func.setdefault(key.name, func)

    def _register_parse_uri(self, key: ParseSource, uri: str):
        if key == ParseSource.championat_com:
            self.__urls.append({'key': key, 'uri': uri})

    def _get_url(self, key: ParseSource):
        for i in self.__urls:
            if key == ParseSource.championat_com:
                return i.get(key.name)

    def _get_parse_func(self, source: Source):
        if source.name == 'championat_com':
            return self._parse_sources_func.get(source.name)

    def _get_source(self, ):
        return

    def __get_src_uri(self) -> str:
        entity_id = session.query(Entity).filter_by(name='source').first().id
        link = session.query(Link).filter_by(source_id=self._src.id, entity_id=entity_id, sport_id=self._sport_id).first()
        uri: str = self._src.url + link.urn
        return uri


class SeasonsLinkParser(Parser):
    def __init__(self, src: Source, sport: Sport):
        super().__init__(src, sport)

        super()._register_parse_func(ParseSource.championat_com, self.__parse_from_championat_com)
        super()._register_parse_func(ParseSource.file, self.__get_from_file())

    def parse(self):
        return super().parse()

    def __parse_from_championat_com(self) -> list:
        content = self._soup.find('div', 'js-tournament-header-year')
        result = []

        if content:
            items = content.find_all('option')

            for i in items:
                urn: str = i.get('data-href')
                uri: str = self._url + urn
                result.append(uri)

        return result

    def __get_from_file(self):
        pass




class AttacksParser(Parser):
    def __init__(self, url: str, src: ParseSource):
        super().__init__(url, src)
        self.__url = ""
        super()._register_parse_func('chmp_com', self.__championat_com_parse)

    def parse(self):
        super().parse()

    def __championat_com_parse(self):
        parse_data = self._soup


class DangerousAttacksParser(Parser):
    def __init__(self, url: str, src: ParseSource):
        super().__init__(url, src)

    def parse(self):
        super().parse()

    def __championat_com_parse(self):
        parse_data = self._soup


class TournamentsParser(Parser):
    def __init__(self, url: str, src: ParseSource):
        super().__init__(src)

    def parse(self):
        super().parse()

    def __championat_com_parse(self):
        parse_data = self._soup
