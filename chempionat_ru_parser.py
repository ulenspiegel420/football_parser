from bs4 import BeautifulSoup as Bs, Tag
import re
from datetime import datetime
import locale


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
