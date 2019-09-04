from bs4 import BeautifulSoup as Bs, Tag
import re
import parsing_functions
from datetime import datetime
from enum import Enum
import locale
import logging
import logging.config


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


# StatAssociations = {
#     'Attacks': 'Голевые моменты',
#     'DangerousAttacks': 'Опасные атаки',
#     'Shoots': 'Удары по воротам',
#     'ShootsOnGoal': 'Удары в створ',
#     'Bars': 'Штанги/перекладины',
#     'Fouls': 'Фолы',
#     'Corners': 'Угловые',
#     'Offsides': 'Офсайды',
#     'Control': '% владения мячом',
#     'LockedShoots': 'Заблокированные удары',
#     'FreeKicks': 'Штрафные удары',
#     'GoalKicks': 'Удары от ворот',
#     'Outs': 'Ауты',
#     'Cautions': 'Предупреждения',
#     'Offs': 'Удаления'
# }
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


def GetIdFromHref(_Tag: Tag):
    Href: str = _Tag.attrs.get('href') if _Tag else None
    RawId: str = re.findall(r"/(\d*?)/$", Href)[0] if Href else None
    Id: int = int(RawId) if RawId else None
    return Id


def GetIdFromString(Href: str):
    RawId: str = re.findall(r"tournament/(\d*?)/", Href)[0] if Href else None
    Id: int = int(RawId) if RawId else None
    return Id


def GetTrnmtNameFromLink(href: str):
    return re.findall(r"https://www.championat.com/football/(\w+)/tournament", href)[0]


def GetLineups(soup):
    Result = {0: [], 1: []}
    Tags = soup.find_all('table', 'match-lineup__players') if soup else None
    for i, tag in enumerate(Tags):
        TagRows = tag.tbody.find_all('tr')
        for tagRow in TagRows:
            Id: int = GetIdFromHref(tagRow.find('a', 'table-item'))
            PlayerNumTag = tagRow.find('td', '_num')
            PlayerNumRaw: str = PlayerNumTag.text.rstrip().lstrip() if PlayerNumTag else None
            Num = int(PlayerNumRaw) if PlayerNumRaw.isdigit() else None
            PlayerAmpluaTag = tagRow.find('span', 'table-item__amplua')
            Amplua = PlayerAmpluaTag.text.rstrip().lstrip() if PlayerAmpluaTag else None
            PlayerNameTag = tagRow.find('span', 'table-item__name')
            Name = PlayerNameTag.text.rstrip().lstrip() if PlayerNameTag else None
            OutTag = tagRow.find('span', '_out')
            Out = OutTag.text.strip() if OutTag else None
            InTag = tagRow.find('span', '_in')
            In = InTag.text.strip() if InTag else None

            Result[i].append(Node(ParsingTypes.Lineup, data={'Id': Id, 'Name': Name, 'Number': Num, 'Amplua': Amplua,
                                                             'In': In, 'Out': Out}))
    return Result


def GetMatchStat(tag, statAssoc: dict):
    try:
        GraphTag = tag.find('div', 'stat-graph') if tag else None
        StatRowTags = GraphTag.find_all('div', 'stat-graph__row') if GraphTag else None
        Result = {'Home': None, 'Guest': None}
        if StatRowTags:
            HomeStatData = {}
            GuestStatData = {}
            for tagRow in StatRowTags:
                TitleTag = tagRow.find('div', 'stat-graph__title')
                Title = statAssoc[TitleTag.text.strip()] if TitleTag else None
                HomeValTag = tagRow.find('div', '_left')
                HomeStatData[Title] = int(HomeValTag.text.rstrip().lstrip()) if HomeValTag else None

                GuestValTag = tagRow.find('div', '_right')

                GuestStatData[Title] = int(GuestValTag.text.rstrip().lstrip()) if GuestValTag else None

            HomeStat = Node(ParsingTypes.MatchStat, data=HomeStatData)
            GuestStat = Node(ParsingTypes.MatchStat, data=GuestStatData)
            Result = {'Home': HomeStat, 'Guest': GuestStat}
        return Result
    except Exception as Err:
        raise Exception(f"Error parsing teams stat: {Err}")


def GetTeams(tag):
    try:
        TeamTags = tag.find_all('div', 'match-info__team')
        if len(TeamTags) != 2: raise Exception('Parsed not 2 teams.')
        Teams = []
        for i in range(len(TeamTags)):
            RawTeamName: Tag = TeamTags[i].find('div', 'match-info__team-name')
            RawTeamCity: Tag = TeamTags[i].find('div', 'match-info__team-country')
            RawUrl: Tag = TeamTags[i].find('a', 'match-info__team-link')
            Name = RawTeamName.text.strip() if RawTeamName else None
            if not Name: return None
            City = RawTeamCity.text.lstrip().rstrip() if RawTeamCity else "-"
            Teams.append({'Name': Name, 'City': City})

        Result = [
            Node(key=ParsingTypes.team, data={'Name': Teams[0]['Name'], 'City': Teams[0]['City'],
                                              'Side': 'Home'}),
            Node(key=ParsingTypes.team, data={'Name': Teams[1]['Name'], 'City': Teams[1]['City'],
                                              'Side': 'Guest'})]
        return Result
    except Exception as Err:
        raise Exception(f"Error parsing teams' names: {Err}")


def GetPunishmentsStat(tag):
    try:
        NearTag = tag.find('h2', text=re.compile('Наказания')) if tag else None
        Tag = NearTag.find_next_sibling('div', 'match-stat') if NearTag else None

        Selectors = {'Home': 'div._team1.match-stat__row-wrapper',
                     'Guest': 'div._team2.match-stat__row-wrapper'} if Tag else {}
        Result = []
        for key, selector in Selectors.items():
            StatTags = Tag.select(selector)
            StatList = []
            for statTag in StatTags:
                PlayerTag = statTag.find('a', 'match-stat__player')
                Player = PlayerTag.text.lstrip().rstrip() if PlayerTag else None

                CardTag = statTag.find('span', 'match-icon')

                if '_yellow' in CardTag.attrs['class']: Card = 'yellow'
                elif '_yellow2' in CardTag.attrs['class']: Card = 'second_yellow'
                elif '_red' in CardTag.attrs['class']: Card = 'red'
                else: Card = None

                MinuteTag = statTag.find('div', 'match-stat__main-value')
                Minute = MinuteTag.text.strip() if MinuteTag else None

                StatList.append({'Player': Player, 'Card': Card, 'Minute': Minute})
            Result.extend(StatList)
        return Result
    except Exception as Err:
        raise Exception(f"Error parsing punishment list: {Err}")


def GetMissPenaltiesStat(tag):
    try:
        NearTag = tag.find('h2', text=re.compile('Незабитые пенальти')) if tag else None
        Tag = NearTag.find_next_sibling('div', 'match-stat') if NearTag else None

        Selectors = {'Home': 'div._team1.match-stat__row-wrapper',
                     'Guest': 'div._team2.match-stat__row-wrapper'} if Tag else {}
        Result = []
        for key, selector in Selectors.items():
            StatTags = Tag.select(selector)
            StatList = []
            for statTag in StatTags:
                PlayerWrapperTag = statTag.find('div', 'match-stat__info')
                PlayerTag = PlayerWrapperTag.a if PlayerWrapperTag else None
                Player = PlayerTag.text.lstrip().rstrip() if PlayerTag else None

                MinuteTag = statTag.find('div', 'match-stat__main-value')
                Minute = MinuteTag.text.strip() if MinuteTag else None

                StatList.append({'Player': Player, 'Minute': Minute})
            Result.extend(StatList)
        return Result
    except Exception as Err:
        raise Exception(f"Error parsing not realised penalty list: {Err}")


def GetMatchId(tag):
    try:
        IdTag = tag.find('div', 'match-info__date')

        if IdTag:
            RawId: str = IdTag['data-id']
            if RawId != '':
                Id = int(RawId.split('-')[1])
                return Id
    except Exception as Err:
        raise Exception(f"Error parsing match id: {Err}")


def GetMatchDate(tag):
    locale.setlocale(locale.LC_ALL, locale="ru_RU")
    DateTimeRaw = None
    try:
        DateElem = tag
        if DateElem:
            DateTimeRaw: str = tag.text.strip() if tag else None
            DateFindResults = re.findall(r"\d+\s\w+\s\d+", DateTimeRaw) if DateTimeRaw else None
            TimeFindResults = re.findall(r"\d+:\d+\s\w+", DateTimeRaw) if DateTimeRaw else None
            DateRaw: str = DateFindResults[0] if DateFindResults else None
            TimeRaw: str = TimeFindResults[0] if TimeFindResults else None

            DateItems = DateRaw.split(' ') if DateRaw else None
            DateString: str = DateItems[0] + '.' + MonthInCase[DateItems[1].lower()] + '.' + DateItems[2] \
                if DateItems else ''

            TimeItems = TimeRaw.split(' ') if TimeRaw else None
            TimeString: str = TimeItems[0] + ' ' + TimeZones[TimeItems[1]] if TimeItems else ''

            if DateString and TimeString == '':
                ResultDateStr: str = DateString
                Date = datetime.strptime(ResultDateStr, "%d.%m.%Y")
            elif DateString and TimeString:
                ResultDateStr: str = DateString + ' ' + TimeString
                Date = datetime.strptime(ResultDateStr, "%d.%m.%Y  %H:%M %z")
            else: Date = None
            return Date
    except Exception as Err:
        raise Exception(f"Error parsing match date {DateTimeRaw}: {Err}")
    finally:
        locale.setlocale(locale.LC_ALL, 'C')


def IsExtraTime(tag):
    try:
        if tag:
            if tag.text.lstrip().rstrip() == '': return False
            else: return True
        else:
            return False
    except Exception as Err:
        raise Exception(f"Error parsing extra time: {Err}")


def GetMainScore(tag):
    try:
        ScoreTag = tag.find('div', 'match-info__count-total')
        if not ScoreTag: return [None, None]
        ScoreRaw: str = ScoreTag.find(text=re.compile(r"\d\s*:\s*\d"))
        if not ScoreRaw: return [None, None]

        ScoreListRaw = [score.strip() for score in ScoreRaw.split(':')]
        if len(ScoreListRaw) != 2: return [None, None]

        ScoreList = []
        if ScoreListRaw[0].isdigit(): ScoreList.append(int(ScoreListRaw[0]))
        else: ScoreList.append(None)
        if ScoreListRaw[1].isdigit(): ScoreList.append(int(ScoreListRaw[1]))
        else: ScoreList.append(None)
        if len(ScoreList) != 2: return [None, None]
        return ScoreList
    except Exception as Err:
        raise Exception(f"Error parsing main score: {Err}")


def GetPenaltyScore(tag):
    if tag is not None:
        ScoreStr = tag.text.lstrip().rstrip()
        if re.match(r"\d\s:\s\d", ScoreStr) is not None:
            ScoreList = [int(score.lstrip().rstrip()) for score in ScoreStr.split(':')]
            return ScoreList
    return [None, None]


def GetTechnicalScore(htmlElem):
    if htmlElem:
        ScoreStr = htmlElem.text.lstrip().rstrip()
        if re.match(r"[+-]\s:\s[+-]", ScoreStr) is not None:
            ScoreList = [score.lstrip().rstrip() for score in ScoreStr.split(':')]
            return ScoreList
    return [None, None]


def GetStadium(tag):
    try:
        if tag:
            StadiumElem = tag.next_sibling
            if StadiumElem:
                StadiumStr = StadiumElem.text.lstrip().rstrip()
                return StadiumStr
    except Exception as Err:
        raise Exception(f"Error parsing stadium: {Err}")


def GetReferee(tag):
    try:
        if tag:
            RefereeElem = tag.next_sibling
            if RefereeElem:
                RefereeStr = RefereeElem.text.lstrip().rstrip()
                return RefereeStr
    except Exception as Err:
        raise Exception(f"Error parsing referee: {Err}")


def GetGoalsStat(tag: Tag):
    try:
        if tag:
            NearTag = tag.find('h2', text=re.compile('Голы')) if tag else None
            _Tag = NearTag.find_next_sibling('div', 'match-stat') if NearTag else None

            Selectors = {'Home': 'div.match-stat__row-wrapper._team1',
                         'Guest': 'div.match-stat__row-wrapper._team2'} if _Tag else {}
            Result = []
            for key, selector in Selectors.items():
                StatTags = _Tag.select(selector) if _Tag else None
                StatList = []
                for statTag in StatTags:
                    PlayerTag = statTag.find('a', 'match-stat__player')
                    Player = PlayerTag.text.rstrip().lstrip() if PlayerTag else None

                    AssistantTag = statTag.find('a', 'match-stat__player2')
                    Assistant = AssistantTag.text.lstrip().rstrip() if AssistantTag else None

                    BecameScoreTag = statTag.find('div', 'match-score')
                    BecameScore = BecameScoreTag.text.rstrip().lstrip() if BecameScoreTag else None

                    IsPenalty = True if '_pen' in BecameScoreTag.get('class') else False

                    IsAuto = True if '_own' in BecameScoreTag.get('class') else False

                    MinuteTag = statTag.find('div', 'match-stat__main-value')
                    Minute: str = MinuteTag.div.text.strip() if MinuteTag else ''

                    StatList.append({'Kicker': Player, 'Assistant': Assistant, 'BecameScore': BecameScore,
                                     'Minute': Minute, 'IsAuto': IsAuto, 'IsPenalty': IsPenalty})
                Result.extend(StatList)
            return Result
    except Exception as Err:
        raise Exception(f"Error parsing goal list: {Err}")


def GetPenalties(tag: Tag):
    try:
        if tag:
            NearTag = tag.find('h2', text=re.compile('Послематчевые пенальти')) if tag else None
            _Tag = NearTag.find_next_sibling('div', 'match-stat') if NearTag else None

            Selectors = {'Home': 'div.match-stat__row-wrapper._team1',
                         'Guest': 'div.match-stat__row-wrapper._team2'} if _Tag else {}
            Result = []
            for key, selector in Selectors.items():
                StatTags = _Tag.select(selector) if _Tag else None
                StatList = []
                for statTag in StatTags:
                    PlayerTag = statTag.find('div', 'match-stat__info')
                    PlayerId = GetIdFromHref(PlayerTag.find('a')) if PlayerTag else None

                    ResultTag = statTag.find('div', 'match-stat__add-info')
                    ResultPenalty = ResultTag.text.strip() if ResultTag else None
                    if ResultPenalty == '': ResultPenalty = 'Гол'

                    ScoreTag = statTag.find('div', 'match-stat__main-value')
                    Score = ScoreTag.text.strip() if ScoreTag else None

                    StatList.append({'PlayerId': PlayerId, 'Result': ResultPenalty, 'Score': Score})
                Result.extend(StatList)
            return Result
    except Exception as Err:
        raise Exception(f"Error parsing after match penalties: {Err}")

def GetMatchStage(tag: Tag):
    try:
        return tag.text.strip() if tag else '-'

    except Exception as Err:
        raise Exception("Error parsing match stage")


class Parser:
    def __init__(self):
        self.log = logging.getLogger('app.championat_com_parser')
        self.StartUrl = "https://www.championat.com/stat/football/tournaments/2/domestic/"
        self.Site = "https://www.championat.com"

    def ParseLinks(self, season=None):
        try:
            self.log.info("Getting links for parsing.")
            Request = parsing_functions.get_request(self.StartUrl)
            Soup = Bs(Request.text, 'html.parser')
            ContentTag = Soup.find('div', 'js-tournament-header-year')
            if ContentTag:
                Items = [item['data-href'] for item in ContentTag.find_all('option')if item['value'] == season]
                if Items:
                    Links = []
                    if season:
                        Links = self.GetTournamentLinks(self.Site + Items[0])
                    return Links
        except Exception as Err:
            raise Exception(f"Error parsing season links: {Err}")
            # self.log.exception(f"Error parsing season links: {Err}")

    def GetTournamentLinks(self, url):
        try:
            Request = parsing_functions.get_request(url)
            Soup = Bs(Request.text, 'html.parser')

            Content = Soup.find('div', 'mc-sport-tournament-list')
            Items = Content.find_all('a')
            Links = []
            for item in Items:
                TournamentLink = self.Site + item['href'] + 'calendar'
                MatchLinks = self.GetMatchLinks(TournamentLink)
                Links.append([TournamentLink, MatchLinks])
            return Links
        except Exception as Err:
            raise Exception(Err)
            # self.log.exception(f"Error parsing tournament links: {Err}")

    def GetMatchLinks(self, url):
        try:
            Request = parsing_functions.get_request(url)
            Soup = Bs(Request.text, 'html.parser')

            Items = Soup.find_all('td', 'stat-results__link')
            Links = [self.Site + item.a['href'] for item in Items]
            return Links
        except Exception as Err:
            raise Exception(Err)
            # self.log.exception(f"Error parsing match links: {Err}")

    @staticmethod
    def GetSeasons(url, proxy):
        try:
            Request = parsing_functions.get_request(url, proxy)
            Soup = Bs(Request.text, 'html.parser')
            ContentTag = Soup.find('div', 'js-tournament-header-year')
            if ContentTag:
                Items = ContentTag.find_all('option')
                if Items:
                    Seasons = [item['value'] for item in Items]
                    return Seasons
        except Exception as Err:
            raise Exception(Err)

    # def GetMatchLinks(self,):
    #     try:
    #         Links = self.Links
    #         MatchLinks = [m for s in Links if len(s) > 1 for t in s[1] if len(t) > 1 for m in t[1]]
    #         return MatchLinks
    #     except Exception as Err:
    #         raise Exception(Err)

    # def GetMatchLinkCount(self):
    #     Count = len(self.MatchLinks)
    #     return Count

    # def parse_tournaments(self, season):
    #     request = parsing_functions.get_request(season.data['url'])
    #     row_id = 1
    #     try:
    #         soup = Bs(request.text, 'html.parser')
    #         content = soup.find('div', 'mc-sport-tournament-list').find_all('div', 'mc-sport-tournament-list__item')
    #         for item in content:
    #             country = item.find('div', 'item__title').get_text().lstrip().rstrip()
    #             html_links = item.find_all(attrs={"data-type": "tournament"})
    #             # uncovered_tournaments += len(html_links)
    #             for html_link in html_links:
    #                 t_name = html_link['data-title'].lstrip().rstrip()
    #                 html_link.find('span', 'separator').extract()
    #                 t_dates_html = html_link.findNext('div', 'item__dates _dates').findAll('span')
    #                 # t_start_date = datetime.strptime(t_dates_html[0].get_text().lstrip().rstrip(), "%d.%m.%Y")
    #                 # t_end_date = datetime.strptime(t_dates_html[1].get_text().lstrip().rstrip(), "%d.%m.%Y")
    #                 t_start_date = t_dates_html[0].text.lstrip().rstrip()
    #                 t_end_date = t_dates_html[1].text.lstrip().rstrip()
    #
    #                 data = {'id': row_id,
    #                         'name': t_name,
    #                         'country': country,
    #                         'start_date': t_start_date,
    #                         'end_date': t_end_date,
    #                         'url': self.site + html_link['href']}
    #
    #                 tournament = Node(ParsingTypes.tournament, data)
    #                 tournament.set_parent(season)
    #                 season.set_child(tournament)
    #                 row_id += 1
    #     except Exception as e:
    #         raise Exception('Ошибка парсинга турниров. ' + str(e))
    #
    # def parse_teams(self, tournaments):
    #     row_id = 1
    #     try:
    #         for tournament in tournaments:
    #             url = tournament.data['url'] + 'teams'
    #             content = parsing_functions.get_contents(url, 'a', 'teams-item__link')
    #             if content is not None:
    #                 # uncovered_teams += len(content)
    #                 for item in content:
    #                     data = {'id': row_id,
    #                             'tournament_id': tournament.data['id'],
    #                             'name': self.parse_team_name(item),
    #                             'city': self.parse_team_city(item),
    #                             'url': self.site + item['href']}
    #
    #                     team = Node(ParsingTypes.team, data)
    #                     team.set_parent(tournament)
    #                     tournament.set_child(team)
    #                     row_id += 1
    #             else:
    #                 common.logging_warning(f'Ошибка получения контента команды по url: {url}')
    #     except Exception as e:
    #         print('Ошибка парсинга команд')
    #         print(e)
    #
    # def parse_team_name(self, html_elem):
    #     player_name_elem = html_elem.find('div', 'teams-item__name')
    #     if player_name_elem is not None:
    #         return player_name_elem.text.lstrip().rstrip()
    #
    # def parse_team_city(self, html_elem):
    #     team_city_elem = html_elem.find('div', 'teams-item__country')
    #     if team_city_elem is not None:
    #         return team_city_elem.text.lstrip().rstrip()

    # def parse_players(self, teams):
    #     row_id = 1
    #     try:
    #         for team in teams:
    #             url = team.data['url'].replace('result', 'players')
    #             content = parsing_functions.get_content(url, 'div', 'js-tournament-filter-content')
    #             if content is not None:
    #                 player_rows = content.tbody.findAll('tr')
    #                 # uncovered_players += len(player_rows)
    #                 for item in player_rows:
    #                     name = self.parse_player_name(item)
    #                     role = self.parse_player_role(item)
    #                     birth = self.parse_player_birth(item)
    #                     growth = self.parse_player_growth(item)
    #                     weight = self.parse_player_weight(item)
    #                     nationality = self.parse_player_nationality(item)
    #
    #                     if name is None or birth is None or growth is None or weight is None or nationality is None:
    #                         self.parsing_log(f"Ошибка парсинга игроков: Не получены данные об игроке. url: {url}")
    #                         continue
    #
    #                     data = {'id': row_id,
    #                             'team_id': team.data['id'],
    #                             'name': name,
    #                             'nationality': nationality,
    #                             'role': role,
    #                             'birth': birth,
    #                             'growth': growth,
    #                             'weight': weight}
    #
    #                     player = Node(ParsingTypes.Lineup, data)
    #                     player.set_parent(team)
    #                     team.set_child(player)
    #                     row_id += 1
    #             else:
    #                 self.parsing_log(f"Ошибка парсинга игроков: Не найден контента для парсинга. url: {url}")
    #     except Exception as e:
    #         print(f'Ошибка парсинга игроков: ' + str(e))
    #
    # def parse_player_name(self, html_elem):
    #     player_name_elem = html_elem.find(attrs={'class': 'table-item__name'})
    #     if player_name_elem is not None:
    #         return player_name_elem.text.lstrip().rstrip()
    #
    # def parse_player_role(self, html_elem):
    #     player_role_elem = html_elem.find(attrs={'data-label': 'Амплуа'})
    #     if player_role_elem is not None:
    #         return player_role_elem.text.lstrip().rstrip()
    #
    # def parse_player_nationality(self, html_elem):
    #     player_nationality = '/'.join(
    #         [country_elem['title'] for country_elem in html_elem.find_all(class_='_country_flag')
    #          if country_elem is not None])
    #     return player_nationality
    #
    # def parse_player_birth(self, html_elem):
    #     player_birth_elem = html_elem.find(attrs={'data-label': 'ДР'})
    #     if player_birth_elem is not None:
    #         return player_birth_elem.text.lstrip().rstrip()
    #
    # def parse_player_growth(self, html_elem):
    #     player_growth_elem = html_elem.find(attrs={'data-label': 'Рост'})
    #     if player_growth_elem is not None:
    #         return player_growth_elem.text.lstrip().rstrip()
    #
    # def parse_player_weight(self, html_elem):
    #     player_weight_elem = html_elem.find(attrs={'data-label': 'Вес'})
    #     if player_weight_elem is not None:
    #         return player_weight_elem.text.lstrip().rstrip()

    # def parse_matches(self, teams):
    #     row_id = 1
    #     try:
    #         for team in teams:
    #             url = team.data['url']
    #             content = parsing_functions.get_content(url, 'div', 'results-team')
    #             if content is not None:
    #                 rows = content.tbody.find_all('tr')
    #                 # uncovered_matches += len(rows)
    #                 for html_row in rows:
    #                     tour = self.parse_match_tour(html_row)
    #                     match_date = GetMatchDate(html_row)
    #
    #                     playing_team_names = GetTeams(html_row)
    #                     if playing_team_names is None:
    #                         self.parsing_log(f"Ошибка парсинга матчей: не удалось получить команды. url: {url}")
    #                         continue
    #
    #                     if playing_team_names['home'] == team.data['name']:
    #                         opponent = playing_team_names['guest']
    #                         match_type = 'home'
    #                     else:
    #                         opponent = playing_team_names['home']
    #                         match_type = 'guest'
    #
    #                     # home_team = team.search_node(playing_team_names['home'], 'name')
    #                     # if home_team is None:
    #                     #     parsing_log(f'Ошибка парсинга матчей: не найдена команда {home_team}. url: {url}')
    #                     #     continue
    #                     #
    #                     # guest_team = team.search_node(playing_team_names['guest'], 'name')
    #                     # if guest_team is None:
    #                     #     parsing_log(f'Ошибка парсинга матчей: не найдена команда {guest_team}. url: {url}')
    #                     #     continue
    #
    #                     main_score = GetMainScore(html_row)
    #                     if main_score is None:
    #                         self.parsing_log(f'Ошибка парсинга матчей: не найден счет в матче. url: {url}')
    #                         continue
    #                     home_result, guest_result = main_score['home_result'], main_score['guest_result']
    #
    #                     penalty_home_result, penalty_guest_result = None, None
    #                     penalty_score = GetPenaltyScore(html_row)
    #                     if penalty_score is not None:
    #                         penalty_home_result = penalty_score['penalty_home_score']
    #                         penalty_guest_result = penalty_score['penalty_guest_score']
    #
    #                     is_extra_time = IsExtraTime(html_row)
    #
    #                     data = {'id': row_id,
    #                             'team_id': team.data['id'],
    #                             'opponent': opponent,
    #                             'tour': tour,
    #                             'match_date': match_date,
    #                             'home_score': home_result,
    #                             'guest_score': guest_result,
    #                             'home_penalty_score': penalty_home_result,
    #                             'guest_penalty_score': penalty_guest_result,
    #                             'match_type': match_type,
    #                             'is_extra_time': is_extra_time}
    #
    #                     match = Node(ParsingTypes.match, data)
    #                     match.set_parent(team)
    #                     team.set_child(match)
    #                     row_id += 1
    #             else:
    #                 self.parsing_log(f'Ошибка парсинга матчей: не найден контент. url: {url}')
    #     except Exception as e:
    #         print('Ошибка парсинга матчей по url: ' + str(e))
    #
    # def parse_match_group(self, html_elem):
    #     group_elem = html_elem.find('td', 'stat-results__group')
    #     if group_elem is not None:
    #         return group_elem.text.lstrip().rstrip()
    #
    # def parse_match_tour(self, html_elem):
    #     # tour_elem = html_elem.find('td', 'stat-results__tour-num')
    #     tour_elem = html_elem.find_all('td')[1]
    #     if tour_elem is not None:
    #         return tour_elem.text.lstrip().rstrip()

    def GetTournamentDates(self, htmlElem):
        try:
            TDatesElem = htmlElem.next_sibling
            if TDatesElem:
                RawTDates = str(TDatesElem).rstrip().lstrip()
                Result = re.findall(r"\d{2}.\d{2}.\d{4}", RawTDates)
                Dates = {'start': datetime.strptime(Result[0], "%d.%m.%Y"),
                         'end': datetime.strptime(Result[1], "%d.%m.%Y")}
                return Dates
        except Exception as Err:
            self.log.exception(f"Error parsing tournament dates: {Err}")

    def GetTournamentMembersCount(self, htmlElem):
        try:
            CountTag = htmlElem.next_sibling
            if CountTag:
                Count = int(str(CountTag).rstrip().lstrip())
                return Count
        except Exception as Err:
            self.log.exception(f"Error parsing team count: {Err}")

    # def GetTournamentId(self, tag):
    #     try:
    #         Href: str = tag.a['href'] if tag else None
    #         RawId: str = re.findall(r"/(\d*?)/$", Href.lstrip().rstrip())[0] if Href else None
    #         Id = int(RawId)
    #         return Id
    #     except Exception as Err:
    #         raise Exception(f"Error parsing tournament id: {Err}")

    def GetTournament(self, soup):
        try:
            Result = {}
            if soup:
                _Tag: Tag = soup.find('div', 'tournament-header__title-name')
                # Id = self.GetTournamentId(soup.find('div', 'tournament-header__title-name'))
                Name = _Tag.a.text.strip() if _Tag else None
                Url: str = _Tag.a['href']
                Members = self.GetTournamentMembersCount(soup.find('div', string='Участники:'))
                Dates = self.GetTournamentDates(soup.find('div', string='Даты проведения:'))
                Start = Dates['start']
                End = Dates['end']
                Result = {'Name': Name, 'Start': Start, 'End': End, 'Members': Members, 'Url': Url}
            return Result
        except Exception as Err:
            raise Exception(f"Error parsing tournament: {Err}")

    def ParseMatches(self, matchLink: str):
        Url = ''
        try:
            Root = Node(key=ParsingTypes.tournament)
            Url = matchLink
            Request = parsing_functions.get_request(Url)
            Soup = Bs(Request.text, 'html.parser')

            if not Root.data: Root.data = {k: v for k, v in self.GetTournament(Soup).items()}
            MatchNode = Node(key=ParsingTypes.match)

            ExtraInfoTag = Soup.find('div', 'match-info__extra')
            Stadium: str = GetStadium(ExtraInfoTag.find(text=re.compile('Стадион:')))
            Referee: str = GetReferee(ExtraInfoTag.find(text=re.compile('Главный судья:')))

            StatTag = Soup.find('div', attrs={'data-type': 'stats'})
            Stats = GetMatchStat(StatTag, StatAssociations)

            Lineups = GetLineups(Soup)
            Teams = GetTeams(Soup.find('div', 'match-info__scoreboard'))
            if Teams is None: return None
            Teams[0].set_child(Stats['Home'])
            Teams[1].set_child(Stats['Guest'])
            MatchNode.AddChildren(Teams)
            [Teams[0].set_child(lineup) for lineup in Lineups[0]]
            [Teams[1].set_child(lineup) for lineup in Lineups[1]]

            for goal in GetGoalsStat(StatTag):
                Player = MatchNode.search_node(goal['Kicker'], 'Name', ParsingTypes.Lineup)
                Assistant = MatchNode.search_node(goal['Assistant'], 'Name', ParsingTypes.Lineup)

                if Player:
                    Goal = Node(key=ParsingTypes.Goal, data={k: v for k, v in goal.items()})
                    Player.set_child(Goal)

                    if Assistant:
                        Assist = Node(key=ParsingTypes.Assist, data={k: v for k, v in goal.items()})
                        Assistant.set_child(Assist)

            for punish in GetPunishmentsStat(StatTag):
                PunishNode = Node(key=ParsingTypes.Punishment, data={k: v for k, v in punish.items()})
                Player = MatchNode.search_node(punish['Player'], 'Name', ParsingTypes.Lineup)
                if Player: Player.set_child(PunishNode)

            for miss in GetMissPenaltiesStat(StatTag):
                MissNode = Node(key=ParsingTypes.MissPenalty, data={k: v for k, v in miss.items()})
                Player = MatchNode.search_node(miss['Player'], 'Name', ParsingTypes.Lineup)
                if Player: Player.set_child(MissNode)

            # Penalties = [{'PlayerId': 974, 'Result': 'Гол', 'Score':'1:0'},
            #              {'PlayerId': 74222, 'Result': 'Мимо', 'Score': '1:0'},
            #              {'PlayerId': 823, 'Result': 'Гол', 'Score': '1:1'},
            #              {'PlayerId': 209, 'Result': 'Гол', 'Score': '1:2'}]
            for penalty in GetPenalties(StatTag):
                Penalty = Node(key=ParsingTypes.Penalty, data={k: v for k, v in penalty.items()})
                Lineup = MatchNode.search_node(penalty['PlayerId'], 'Id', ParsingTypes.Lineup)
                if Lineup: Lineup.set_child(Penalty)

            MainScore: list = GetMainScore(Soup.find('div', 'match-info__scoreboard'))
            PenaltyScore: list = GetPenaltyScore(Soup.find('div', 'match-info__count-extra'))
            TechScore: list = GetTechnicalScore(Soup.find('div', 'match-info__count-extra'))

            MatchNode.data = {
                'Url': Url,
                'Stadium': Stadium,
                'Referee': Referee,
                'Date': GetMatchDate(Soup.find('div', 'match-info__date')),
                'Stage': GetMatchStage(Soup.find('div', 'match-info__stage')),
                'IsExtra': IsExtraTime(Soup.find('div', 'match-info__count-extra')),
                'HomeScore': MainScore[0],
                'GuestScore': MainScore[1],
                'HomePenaltyScore': PenaltyScore[0],
                'GuestPenaltyScore': PenaltyScore[1],
                'HomeTechScore': TechScore[0],
                'GuestTechScore': TechScore[1]}
            Root.set_child(MatchNode)
            return Root
        except Exception as Err:
            self.log.exception(f"Error parsing match {Url}: {Err}")


class Node:

    def __init__(self, key, data=None, parent=None):
        self.key = key
        self.data = data if data else {}
        self.children = []
        self.parents = [parent] if parent is not None else []

    def get_parents(self):
        return self.parents

    def get_children(self):
        return self.children

    def GetCountChildren(self):
        return len(self.children) if self.children else 0

    def set_parent(self, node):
        self.parents.append(node)

    def set_child(self, node):
        if node:
            self.children.append(node)
            node.parents.append(self)

    def AddChildren(self, nodes: list):
        [self.set_child(node) for node in nodes]

    def Count(self):
        count = 0
        if self.get_children():
            count += len(self.children)
            for child in self.children:
                count += child.Count()
        return count

    def HasChildren(self):
        if self.children:
            return True
        return False

    def CountWhere(self, field: str, value):
        Count = 0
        Field = field.lower()
        Value = value.lower() if type(value) is str else value
        if Field in self.data:
            if Value == self.data[Field]:
                Count += 1
        for Child in self.children:
            Count += Child.CountWhere(Field, Value)
        return Count

    def CountByKey(self, key: ParsingTypes):
        count = 0
        if self.key is key:
            count += 1
        for child in self.children:
            count += child.CountByKey(key)
        return count

    def GetNodesByKey(self, key: ParsingTypes, recursive=True, reverse=False):
        if reverse:
            if len(self.get_parents()) == 0:
                return []
        else:
            if len(self.get_children()) == 0:
                return []
        result = []
        Items = self.get_parents() if reverse else self.get_children()
        for item in Items:
            if item.key == key:
                result.append(item)
            if recursive:
                items = item.GetNodesByKey(key, recursive, reverse)
                if items is not None: result.extend(items)
        return result

    def search_node(self, value: str, field: str, key: ParsingTypes = None, reverse=False):
        if not value: return

        if self.key is key:
            if self.data:
                if self.data.get(field) == value:
                    return self
        Items = self.get_parents() if reverse else self.get_children()
        for item in Items:
            Result = item.search_node(value, field, key, reverse)
            if Result: return Result

    # def GetNodesWhere(self, field: str, value, parent=None):
    #     ResultNode: Node = Node(self.key) if parent is None else parent
    #     Field = field.lower()
    #     Value = value
    #     for Child in self.children:
    #         if Field in Child.data:
    #             if Value == Child.data[Field]:
    #                 ResultNode.set_child(self)
    #         if Child.HasChildren():
    #             ResultNode.set_child(Child.GetNodesWhere(Field, Value, parent))
    #     return ResultNode
