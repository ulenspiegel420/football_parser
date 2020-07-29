from chempionat_ru_parser import Parser, ParsingTypes
import sys
import design
from database_components import Database
import logging
import logging.config
from football_stat import TournamentListModel, TeamListModel, TeamStatItem, BaseListModel
from enum import Enum
from functools import reduce
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
import championat_com_model as model
from chempionat_ru_parser import Node, GetIdFromString, GetTrnmtNameFromLink
, exists, and_
import os


def MessageError(msg: str):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Information)
    msg_box.setText(str(msg))
    msg_box.exec_()


class ParsingThread(QtCore.QThread):
    ResultReady = QtCore.pyqtSignal(dict)

    def __init__(self, season, session, IsFromFile=False, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.Season: str = season
        self._Session: Session = session
        self.logger = logging.getLogger('app.ParsingThread')
        self.IsFromFile = IsFromFile

    def run(self):
        self.logger.info(f"Start parsing season {self.Season}.")
        ParsedMatchCount = 0
        ChampionatParser = Parser()
        Year = self.Season.split('/')[0]
        ParsedPath = f"assets/links/parsed/{Year}/"
        if not os.path.exists(ParsedPath): os.mkdir(ParsedPath)
        try:
            start_parsing = datetime.now()
            if self.IsFromFile:
                for root, dirs, files in os.walk(f"assets/links/{Year}"):
                    for file in files:
                        self.logger.info(f"Start parsing {file}.")
                        ParsedFile = ParsedPath + file
                        if not os.path.exists(ParsedFile): open(ParsedFile, 'a').close()
                        with open(ParsedFile) as handler:
                            SuccessLines = handler.readlines()
                            LastSuccessUrl = SuccessLines[-1] if SuccessLines else None
                        with open(f"assets/links/{Year}/{file}") as handler: Lines = handler.readlines()
                        StartIdx = Lines.index(LastSuccessUrl)+1 if LastSuccessUrl else 0

                        for Line in Lines[StartIdx:]:
                            matchUrl = Line.replace("\n", '')
                            ParsedResult: Node = ChampionatParser.ParseMatches(matchUrl)
                            if not ParsedResult: continue
                            for match in ParsedResult.get_children():
                                if self._Session.query(
                                        exists().where(model.Match.Url == match.data['Url'])).scalar(): continue
                                Match = model.Match(**dict((k, v) for k, v in iter(match.data.items())))

                                Match.Tournament = model.GetOrCreate(self._Session, model.Tournament,
                                                                     **dict((k, v) for k, v in
                                                                            iter(ParsedResult.data.items())))

                                _Teams = match.GetNodesByKey(ParsingTypes.team, recursive=False)
                                for team in _Teams:
                                    Team = model.GetOrCreate(self._Session, model.Team,
                                                             **dict((k, v) for k, v in iter(team.data.items()) if
                                                                    k != 'Side'))
                                    if team.data['Side'] == 'Home':
                                        Match.HomeTeam = Team
                                        _HomeStat: list = team.GetNodesByKey(ParsingTypes.MatchStat,
                                                                             recursive=False)
                                        Match.HomeStat = model.Stat(**_HomeStat[0].data) if _HomeStat else None
                                    if team.data['Side'] == 'Guest':
                                        _GuestStat: list = team.GetNodesByKey(ParsingTypes.MatchStat,
                                                                              recursive=False)
                                        Match.GuestStat = model.Stat(**_GuestStat[0].data) if _GuestStat else None
                                        Match.GuestTeam = Team

                                Goals = []
                                for _goal in match.GetNodesByKey(ParsingTypes.Goal):
                                    GoalData = {'BecameScore': _goal.data['BecameScore'],
                                                'Minute': _goal.data['Minute'],
                                                'IsAuto': _goal.data['IsAuto'],
                                                'IsPenalty': _goal.data['IsPenalty']}
                                    Goals.append(model.Goal(**GoalData))

                                _Lineups = []
                                [_Lineups.extend(team.GetNodesByKey(ParsingTypes.Lineup, recursive=False)) for team
                                 in _Teams]

                                for _lineup in _Lineups:
                                    LineupData = {'Amplua': _lineup.data['Amplua'],
                                                  'In': _lineup.data['In'],
                                                  'Out': _lineup.data['Out']}
                                    Lineup = model.Lineup(**LineupData)

                                    _Team = _lineup.get_parents()[0]
                                    if _Team.data['Name'] == Match.HomeTeam.Name: Lineup.Team = Match.HomeTeam
                                    if _Team.data['Name'] == Match.GuestTeam.Name: Lineup.Team = Match.GuestTeam

                                    if _lineup.data['Id'] == 126202:
                                        _lineup.data['Name'] = 'Джош Куллен'
                                    Lineup.Player = model.GetOrCreate(self._Session, model.Player,
                                                                      Id=_lineup.data['Id'],
                                                                      Name=_lineup.data['Name'])
                                    Lineup.Match = Match

                                    for _goal in _lineup.GetNodesByKey(ParsingTypes.Goal, recursive=False):
                                        if _goal.data['Kicker'] == _lineup.data['Name']:
                                            Minute = _goal.data['Minute']
                                            Score = _goal.data['BecameScore']
                                            Lineup.Goals = [g for g in Goals if
                                                            g.Minute == Minute and g.BecameScore == Score]

                                    Assists = []
                                    for _assist in _lineup.GetNodesByKey(ParsingTypes.Assist, recursive=False):
                                        Minute = _assist.data['Minute']
                                        Score = _assist.data['BecameScore']
                                        Assist = model.Assist()
                                        Goal = [g for g in Goals if g.Minute == Minute and g.BecameScore == Score]
                                        if Goal:
                                            Assist.Goal = Goal[0]
                                        else:
                                            raise Exception(f"Goal not found {_lineup.data['Name']}, "
                                                            f"{match.data['Url']}")
                                        Assists.append(Assist)
                                    Lineup.Assists = Assists

                                    Lineup.Punishments = [
                                        model.Punishment(Card=p.data['Card'], Minute=p.data['Minute'])
                                        for p in _lineup.GetNodesByKey(ParsingTypes.Punishment, recursive=False)]
                                    Lineup.MissPenalties = [model.MissPenalty(Minute=m.data['Minute']) for m in
                                                            _lineup.GetNodesByKey(ParsingTypes.MissPenalty,
                                                                                  recursive=False)]
                                    Lineup.Penalties = [
                                        model.Penalty(Result=m.data['Result'], Score=m.data['Score']) for m in
                                        _lineup.GetNodesByKey(ParsingTypes.Penalty, recursive=False)]

                                    self._Session.add(Lineup)

                                self._Session.add(Match)
                                self._Session.commit()

                                ParsedMatchCount += ParsedResult.CountByKey(ParsingTypes.match)

                                with open(ParsedFile, 'a') as handler:
                                    handler.write(Line)
                        os.remove(f"assets/links/{Year}/{file}")
            elapsed_time = datetime.now() - start_parsing
            ParseResult: dict = {'season': self.Season, 'parsed_match_count': ParsedMatchCount,
                                 'elapsed': elapsed_time.total_seconds()}
            self.logger.info(f"Finish parsing season {self.Season}.")
            self.ResultReady.emit(ParseResult)
        except Exception as Err:
            raise Exception(Err)


class KindVariation(Enum):
    KindVariation = 0
    ShootsOnMatches = 1
    MissesPerMatch = 2
    DifferenceGoals = 3
    MatchesByTime = 4
    ShootsByTime = 5
    MissesByTime = 6
    WinSeriesByCount = 7
    LoseSeriesByCount = 8
    DrawSeriesByCount = 9
    DatesOnMatches = 10


class App(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.logger = logging.getLogger('app')

        self.ParsedSeasonsCount = 0
        self.count_for_parse = 0
        self.years_for_parsed = range(2002, 2019)
        self.ParsedSeasons = []

        # Signals
        self.ParseBtn.clicked.connect(self.OnClickParseBtn)
        self.SaveLinksBtn.clicked.connect(self.OnClickSaveLinksBtn)
        self.LoadSeasonsBtn.clicked.connect(self.OnClickLoadSeasonsBtn)

        # Initialize functions
        self.__init_parsed_seasons()

    def __init_parsed_seasons(self):
        # db = Database(Database.DB_PREFIX)
        # for year in self.years_for_parsed:
        #
        #     if db.is_exist():
        #         self.ParsedSeasons.append(year)
        # if self.ParsedSeasons:
        #     Model = SeasonListModel(self.ParsedSeasons)
        #     ind = Model.index(1)
        #     Rows = Model.data(ind)
        #     self.ParsedSeasonsCbx.setModel(Model)
        #
        #     self.FirstsSeasonSBox.setMaximum(self.ParsedSeasons[-1])
        #     self.LastSeasonSBox.setMaximum(self.ParsedSeasons[-1])
        #
        #     self.FirstsSeasonSBox.setMinimum(self.ParsedSeasons[0])
        #     self.LastSeasonSBox.setMinimum(self.ParsedSeasons[0])
        #
        #     self.FirstsSeasonSBox.setValue(self.ParsedSeasons[0])
        #     self.LastSeasonSBox.setValue(self.ParsedSeasons[-1])
        pass

    def OnClickLoadSeasonsBtn(self):
        try:

            Proxy: str = self.ProxyEdit.displayText() if self.ProxyEdit.displayText() else None
            SeasonsModel = QtCore.QStringListModel()

            SeasonsModel.setStringList(
                Parser.GetSeasons(, Proxy))
            self.select_parse_year_cbx.setModel(SeasonsModel)
        except Exception as Err:
            MessageError(str(Err))

    def OnGetStatBtn(self):
        try:
            SelectedTeamName = self.TeamCbx.currentText()
            SelectedTournamentName = self.tournaments_cbx.currentText()
            # DataList = []
            # RootData = []
            # RootItem: TeamStatItem = None
            #
            # for Season in Seasons:
            #     Db = Database(Database.DB_PREFIX + str(Season))
            #     TournamentId = Db.ExecuteSelectSql(f"select id from tournaments where name='{SelectedTournamentName}'")
            #     TeamId = Db.ExecuteSelectSql(
            #         f"select id from teams where name='{SelectedTeamName}' and tournament_id={TournamentId}")
            #     if not TournamentId or not TeamId:
            #         continue
            #     RootData.append(str(Season))
            #     DataList.append(TeamStat(TeamId, TournamentId, Season))
            #     RootItem = TeamStatItem('Stat Value', RootData)
            #
            # TotalCountItem = TeamStatItem('Total count', [St.TotalCount for St in DataList], RootItem)
            # HomeCountItem = TeamStatItem('Total home count', [Stat.TotalHomeCount for Stat in DataList], TotalCountItem)
            # GuestCountItem = TeamStatItem('Total guest count', [Stat.TotalGuestCount for Stat in DataList], TotalCountItem)
            #
            # WonCountItem = TeamStatItem('Won count', [str(St.WonCount) + ' (' + str(St.WonPercent) + '%)' for St in DataList], RootItem)
            # WonHomeCountItem = TeamStatItem('Won home count', [str(St.WonHomeCount) + ' (' + str(St.WonHomePercent) + '%)' for St in DataList], WonCountItem)
            # WonGuestCountItem = TeamStatItem('Won guest count', [str(St.WonGuestCount) + ' (' + str(St.WonGuestPercent) + '%)' for St in DataList], WonCountItem)
            #
            # LostCountItem = TeamStatItem('Lost count', [str(St.LostCount) + ' (' + str(St.LostPercent) + '%)' for St in DataList], RootItem)
            # LostHomeCountItem = TeamStatItem('Lost home count', [str(St.LostHomeCount) + ' (' + str(St.LostHomePercent) + '%)' for St in DataList], LostCountItem)
            # LostGuestCountItem = TeamStatItem('Lost guest count', [str(St.LostGuestCount) + ' (' + str(St.LostGuestPercent) + '%)' for St in DataList], LostCountItem)
            #
            # DrawCountItem = TeamStatItem('Draw count', [str(St.DrawCount) + ' (' + str(St.DrawPercent) + '%)' for St in DataList], RootItem)
            # DrawHomeCountItem = TeamStatItem('Draw home count', [str(St.DrawHomeCount) + ' (' + str(St.DrawHomePercent) + '%)' for St in DataList], DrawCountItem)
            # DrawGuestCountItem = TeamStatItem('Draw guest count', [str(St.DrawGuestCount) + ' (' + str(St.DrawGuestPercent) + '%)' for St in DataList], DrawCountItem)
            #
            # Model = TeamStatModel(RootItem)
            #
            # self.StatTreeView.setModel(Model)
        except Exception as Error:
            MessageError(str(Error))

    def OnGetStatOppBtn(self):
        try:
            Seasons = []
            # if self.FirstsSeasonSBox.value() == self.LastSeasonSBox.value():
            #     Seasons.append(self.FirstsSeasonSBox.value())
            # else:
            #     [Seasons.append(year) for year in range(self.FirstsSeasonSBox.value(), self.LastSeasonSBox.value() + 1)]
            #
            # RootData = []
            # DataList = []
            # RootItem: TeamStatItem = None
            # for Season in Seasons:
            #     Db = Database(Database.DB_PREFIX + str(Season))
            #     TournamentId = Db.ExecuteSelectSql(f"select id from tournaments "
            #                                        f"where name='{self.tournaments_cbx.currentText()}'")
            #     TeamId = Db.ExecuteSelectSql(
            #         f"select id from teams where name='{self.TeamCbx.currentText()}' and tournament_id={TournamentId}")
            #     if not TournamentId or not TeamId:
            #         continue
            #     RootData.append(str(Season))
            #     RootItem = TeamStatItem('Stat Value', RootData)
            #     DataList.append(MatchesAnalysis(TeamId, TournamentId, Season, self.OpponentCbx.currentText()))
            #
            # TotalOpp = TeamStatItem('Opponent count', [str(St.GetTotalOppCount()) for St in DataList], RootItem)
            #
            # WonOpp = TeamStatItem('Won count', [str(St.GetWonOppCount()) for St in DataList], RootItem)
            # WonOppHome = TeamStatItem('Won home count', [str(St.GetWonHomeOppCount()) for St in DataList], WonOpp)
            # WonOppGuest = TeamStatItem('Won guest count', [St.GetWonGuestOppCount() for St in DataList], WonOpp)
            #
            # LostOpp = TeamStatItem('Lost count', [str(St.GetLostOppCount()) for St in DataList], RootItem)
            # LostOppHome = TeamStatItem('Lost home count', [str(St.GetLostHomeOppCount()) for St in DataList], LostOpp)
            # LostOppGuest = TeamStatItem('Lost guest count', [St.GetLostGuestOppCount() for St in DataList], LostOpp)
            #
            # DrawOpp = TeamStatItem('Draw count', [str(St.GetDrawOppCount()) for St in DataList], RootItem)
            # DrawOppHome = TeamStatItem('Draw home count', [str(St.GetDrawHomeOppCount()) for St in DataList], DrawOpp)
            # DrawOppGuest = TeamStatItem('Draw guest count', [St.GetDrawGuestOppCount() for St in DataList], DrawOpp)
            #
            # Model = TeamStatModel(RootItem)
            # self.StatOpTreeView.setModel(Model)
        except Exception as Error:
            MessageError(str(Error))

    def OnTotalStatBtn(self):
        Seasons = []
        # StartSeason = self.FirstsSeasonSBox.value()
        # EndSeason = self.LastSeasonSBox.value()
        # if self.FirstsSeasonSBox.value() == self.LastSeasonSBox.value():
        #     Seasons.append(self.FirstsSeasonSBox.value())
        # else:
        #     [Seasons.append(year) for year in range(self.FirstsSeasonSBox.value(), self.LastSeasonSBox.value() + 1)]
        #
        # Stat = TeamStatPeriod(self.TeamCbx.currentText(), self.tournaments_cbx.currentText(), Seasons)
        #
        # RootItem: TeamStatItem = TeamStatItem(f'Stat {str(self.FirstsSeasonSBox.value())}-{str(self.LastSeasonSBox.value())}', ['Total'])
        # RoundLevel: int = 2

        # TotalCount: int = 0
        # WonCount: int = 0
        # WonHomeCount: int = 0
        # WonGuestCount: int = 0
        # LostCount: int = 0
        # LostHomeCount: int = 0
        # LostGuestCount: int = 0
        # DrawCount: int = 0
        # DrawHomeCount: int = 0
        # DrawGuestCount: int = 0

        Wins: dict = {}

        # for Season in Seasons:
        #     Db = Database(Database.DB_PREFIX + str(Season))
        #     TournamentId = Db.GetTournamentId(self.tournaments_cbx.currentText())
        #     TeamId = Db.GetTeamId(self.TeamCbx.currentText(), TournamentId)
        #
        #     TeamRow = Db.GetTeamRow(TeamId, TournamentId)
        #     if TeamRow is not None: continue
        #
        #     Team = Node(ParsingTypes.team, data=TeamRow)
        #     MatchRows = Db.GetMatchRows(TeamId)
        #     [Team.set_child(Node(ParsingTypes.match, data=row)) for row in MatchRows]
        #
        #     if not TournamentId or not TeamId: continue
        #     Stat = TeamStat(Team, Season, self.OpponentCbx.currentText())
        #
        #     Wins[Season] = Stat.GetWonCount()

            # TotalCount += Stat.GetTotalCount()
            # WonCount += Stat.GetWonCount()
            # WonHomeCount += Stat.GetWonHomeCount()
            # WonGuestCount += Stat.GetWonGuestCount()
            # LostCount += Stat.GetLostCount()
            # LostHomeCount += Stat.GetLostHomeCount()
            # LostGuestCount += Stat.GetLostGuestCount()
            # DrawCount += Stat.GetDrawCount()
            # DrawHomeCount += Stat.GetDrawHomeCount()
            # DrawGuestCount += Stat.GetDrawGuestCount()

        # WonPercent: int = round((WonCount/TotalCount)*100, RoundLevel)
        # WonHomePercent: int = round((WonHomeCount / WonCount) * 100, RoundLevel)
        # WonGuestPercent: int = round((WonGuestCount / WonCount) * 100, RoundLevel)
        # LostPercent: int = round((LostCount / TotalCount) * 100, RoundLevel)
        # LostHomePercent: int = round((LostHomeCount / LostCount) * 100, RoundLevel)
        # LostGuestPercent: int = round((LostGuestCount / LostCount) * 100, RoundLevel)
        # DrawPercent: int = round((DrawCount / TotalCount) * 100, RoundLevel)
        # DrawHomePercent: int = round((DrawHomeCount / DrawCount) * 100, RoundLevel)
        # DrawGuestPercent: int = round((DrawGuestCount / DrawCount) * 100, RoundLevel)

        # TotalCountItem = TeamStatItem('Total count', [TotalCount], RootItem)
        # WonCountItem = TeamStatItem('Won count', [str(WonCount)+' ('+str(WonPercent)+')%'], RootItem)
        # WonHomeCountItem = TeamStatItem('Won home count', [str(WonHomeCount) + ' (' + str(WonHomePercent) + ')%'], WonCountItem)
        # WonGuestCountItem = TeamStatItem('Won guest count', [str(WonGuestCount) + ' (' + str(WonGuestPercent) + ')%'], WonCountItem)
        # LostCountItem = TeamStatItem('Lost count', [str(LostCount)+' ('+str(LostPercent)+')%'], RootItem)
        # LostHomeCountItem = TeamStatItem('Lost home count', [str(LostHomeCount) + ' (' + str(LostHomePercent) + ')%'], LostCountItem)
        # LostGuestCountItem = TeamStatItem('Lost guest count', [str(LostGuestCount) + ' (' + str(LostGuestPercent) + ')%'], LostCountItem)
        # DrawCountItem = TeamStatItem('Draw count', [str(DrawCount)+' ('+str(DrawPercent)+')%'], RootItem)
        # DrawHomeCountItem = TeamStatItem('Draw home count', [str(DrawHomeCount) + ' (' + str(DrawHomePercent) + ')%'], DrawCountItem)
        # DrawGuestCountItem = TeamStatItem('Draw guest count', [str(DrawGuestCount) + ' (' + str(DrawGuestPercent) + ')%'], DrawCountItem)

        # Model = TeamStatModel(RootItem)
        # self.TotalStatTreeView.setModel(Model)

    def OnSeasonChanged(self):
        try:
            Model = TournamentListModel(self.ParsedSeasonsCbx.currentData())
            self.tournaments_cbx.setModel(Model)
        except Exception as Error:
            MessageError(str(Error))

    def OnTournamentsChanged(self):
        selected_tournament_id = self.tournaments_cbx.currentData()
        SelectedSeason = self.ParsedSeasonsCbx.currentData()
        Db = Database(Database.DB_PREFIX + str(SelectedSeason))
        TeamRows = Db.get_rows('teams', 'id,name', tournament_id=selected_tournament_id)

        TeamModel = TeamListModel()
        TeamModel.AddTeamNodes([Node(ParsingTypes.match, data=row) for row in TeamRows])

        self.TeamCbx.setModel(TeamModel)
        self.OpponentCbx.setModel(TeamModel)

    def OnClickParseBtn(self):
        try:
            self.parse_animated_lbl.show()
            self.parse_status_lbl.show()
            self.ParseBtn.setDisabled(True)
            self.select_parse_year_cbx.setDisabled(True)
            movie = QtGui.QMovie('assets/img/loading.gif')
            self.parse_animated_lbl.setMovie(movie)
            movie.setScaledSize(QtCore.QSize(32, 32))
            movie.start()
            self.parse_status_lbl.setText('Start parsing...')

            SelectedSeason = self.select_parse_year_cbx.currentText()

            self.logger.info("Creating tables")
            model.CreateAll(self.Engine)

            IsFromFile = True if self.LinksFromFileCbx.isChecked() else False

            Thread = ParsingThread(SelectedSeason, self.DbSession, IsFromFile=IsFromFile)
            Thread.ResultReady.connect(self.OnThreadResult, QtCore.Qt.QueuedConnection)
            ListItem = QtWidgets.QListWidgetItem(SelectedSeason + ' - parsing...', self.ParsedStatusList)
            Thread.start()
        except Exception as Err:
            MessageError(str(Err))
            # self.logger.exception(f"Error adding to db: {Err}")

    def OnThreadResult(self, result):
        StatusItems = self.ParsedStatusList.findItems(result['season'], QtCore.Qt.MatchContains)
        for item in StatusItems:
            item.setText(f"{result['season']} - parsed.")

        result_msg = f"Parsed season {result['season']} for {result['elapsed']}sec.\n" \
                     f"Parsed match count: {result['parsed_match_count']} items.\n" \

        self.parse_info_textb.append(result_msg)
        self.ParseBtn.setDisabled(False)
        self.select_parse_year_cbx.setDisabled(False)
        self.parse_animated_lbl.movie().stop()
        self.parse_status_lbl.setText('Parsing done.')
        self.parse_animated_lbl.hide()
        self.parse_status_lbl.hide()
        self.ParsedResultLbl.setText(f"Parsed season {result['season']} complete")
        self.__init_parsed_seasons()

    def OnVariationCbxChanged(self):
        Seasons = []
        # if self.FirstsSeasonSBox.value() == self.LastSeasonSBox.value():
        #     Seasons.append(self.FirstsSeasonSBox.value())
        # else:
        #     [Seasons.append(year) for year in range(self.FirstsSeasonSBox.value(), self.LastSeasonSBox.value() + 1)]
        #
        # Db = Database(Database.DB_PREFIX + str(self.ParsedSeasonsCbx.currentData()))
        # Team = Node(ParsingTypes.team, Db.GetTeamRow(self.TeamCbx.currentData(), self.tournaments_cbx.currentData()))
        # Team.children = [Node(ParsingTypes.match, Row) for Row in Db.GetMatchRows(Team.data['id'])]
        # for match in Team.children: match.data['team'] = Team.data['name']
        #
        # Stat = MatchesAnalysis(Team.children)
        # Matches: pd.DataFrame = Stat.HomeMatches
        # HomeScMean = Matches.groupby('match_date').mean()
        # print(Matches)
        # print(HomeScMean)
        #
        # ShootsSeries = stat.VarSeries(Stat.GetMatchesOnShoots())
        #
        #
        # FieldStat = None
        # FieldStat = ShootsSeries
        # # if self.VariationCbx.currentData() == KindVariation.ShootsOnMatches.value:
        # #     FieldStat = Stat.GetStat(Stat.GetShootsOnMatches(), True)
        # # if self.VariationCbx.currentData() == KindVariation.DatesOnMatches.value:
        # #     FieldStat = Stat.GetStat(Stat.GetDatesOnMatches())
        # # elif self.VariationCbx.currentData() == KindVariation.MissesPerMatch.value:
        # #     FieldStat = Stat.GetStat(Stat.Misses)
        # # elif self.VariationCbx.currentData() == KindVariation.DifferenceGoals.value:
        # #     FieldStat = Stat.GetStat(Stat.Diffs)
        # # elif self.VariationCbx.currentData() == KindVariation.MatchesByTime.value:
        # #     FieldStat = Stat.GetStat(Stat.MatchTimes)
        # # elif self.VariationCbx.currentData() == KindVariation.ShootsByTime.value:
        # #     FieldStat = Stat.GetStat(Stat.GetShootsOnTimes(), True)
        # # elif self.VariationCbx.currentData() == KindVariation.MissesByTime.value:
        # #     FieldStat = Stat.GetStat(Stat.GetMissesByTime())
        # # elif self.VariationCbx.currentData() == KindVariation.WinSeriesByCount.value:
        # #     FieldStat = Stat.GetStat([len(Series) for Series in Stat.GetSerieses()['Win']])
        # # elif self.VariationCbx.currentData() == KindVariation.LoseSeriesByCount.value:
        # #     FieldStat = Stat.GetStat([len(Series) for Series in Stat.GetSerieses()['Lose']])
        # # elif self.VariationCbx.currentData() == KindVariation.DrawSeriesByCount.value:
        # #     DrawSerieses = [len(Series) for Series in Stat.GetSerieses()['Draw']]
        # #     if DrawSerieses:
        # #         FieldStat = Stat.GetStat(DrawSerieses)
        #
        # if FieldStat is not None:
        #     self.VariationTable.setRowCount(len(FieldStat.x)+1)
        #     for i in range(len(FieldStat.x)):
        #         self.VariationTable.setItem(i, 0, QtWidgets.QTableWidgetItem(str(FieldStat.x[i])))
        #         self.VariationTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(FieldStat.f[i])))
        #         self.VariationTable.setItem(i, 2, QtWidgets.QTableWidgetItem(str(FieldStat.W[i]) + '%'))
        #     N = str(reduce((lambda x, y: x + y), FieldStat.f))
        #     W = str(reduce((lambda x, y: x + y), FieldStat.W)) + ' %'
        #     self.VariationTable.setItem(len(FieldStat.x), 1, QtWidgets.QTableWidgetItem('N=' + N))
        #     self.VariationTable.setItem(len(FieldStat.x), 2, QtWidgets.QTableWidgetItem(W))

        # fig = plt.figure()
        # plt.title(Team.data['name'] + ' wins for 2002')
        # plt.bar(ShootsStat.x, ShootsStat.W)
        # plt.show()

    def OnClickSaveLinksBtn(self):
        try:
            Season: str = self.select_parse_year_cbx.currentText()
            Year = Season.split('/')[0]
            ChampionatParser = Parser()
            if not os.path.exists(f"assets/links/{Year}"): os.mkdir(f"assets/links/{Year}")

            for trnmtLink in ChampionatParser.ParseLinks(Season):
                Id = GetIdFromString(trnmtLink[0])
                TrnmtName = GetTrnmtNameFromLink(trnmtLink[0])
                with open(f"assets/links/{Year}/{TrnmtName+'_'+str(Id)}.txt", 'w') as handler:
                    [handler.write(matchLink+'\n') for matchLink in trnmtLink[1]]
        except Exception as Err:
            self.logger.exception(f"Error saving links to files: {Err}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
