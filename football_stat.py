from database_components import Database
from chempionat_ru_parser import Node, ParsingTypes
from enum import Enum
from PyQt5 import QtCore
import math
from datetime import datetime, time


# class MatchesAnalysis:
#     def __init__(self, matches: list):
#         # public
#         self.RoundLevel: int = 2
#         # private
#         self._Matches = self.__MakeMatches(matches)
#         # self.__HomeMatches = [m for m in matches if m.data['match_type'] == 'home']
#         # self.__GuestMatches = [m for m in matches if m.data['match_type'] == 'guest']
#         # # self.__WonCount: int = self.GetWonCount()
#         # # self.__WonHomeCount: int = self.GetWonHomeCount()
#         # # self.__WonGuestCount: int = self.GetWonGuestCount()
#         # #
#         # # self.__LostCount: int = self.GetLostCount()
#         # # self.__LostHomeCount: int = self.GetLostHomeCount()
#         # # self.__LostGuestCount: int = self.GetLostGuestCount()
#         # #
#         # # self.__DrawCount: int = self.GetDrawCount()
#         # # self.__DrawHomeCount: int = self.GetDrawHomeCount()
#         # # self.__DrawGuestCount: int = self.GetDrawGuestCount()
#         # #
#         # # self.__WonPercent: int = self.GetWonPercent()
#         # # self.__WonHomePercent: int = self.GetWonHomePercent()
#         # # self.__WonGuestPercent: int = self.GetWonGuestPercent()
#         # #
#         # # self.__LostPercent: int = self.GetLostPercent()
#         # # self.__LostHomePercent: int = self.GetLostHomePercent()
#         # # self.__LostGuestPercent: int = self.GetLostGuestPercent()
#         # #
#         # # self.__DrawPercent: int = self.GetDrawPercent()
#         # # self.__DrawHomePercent: int = self.GetDrawHomePercent()
#         # # self.__DrawGuestPercent: int = self.GetDrawGuestPercent()
#         # self.__HomeShoots = np.array([m.data['home_score'] for m in self.__HomeMatches])
#         # self.__GuestShoots = np.array([m.data['guest_score'] for m in self.__GuestMatches])
#         # self.__Shoots = np.append(self.__HomeShoots, self.__GuestShoots)
#         #
#         # self.__HomeMisses = np.array([m.data['guest_score'] for m in self.__HomeMatches])
#         # self.__GuestMisses = np.array([m.data['home_score'] for m in self.__GuestMatches])
#         # self.__Misses = np.append(self.__HomeMisses, self.__GuestMisses)
#         #
#         # self.__MatchTimes = [Team.data['match_date'].time() for Team in matches]
#         # self.__Diffs = self.Shoots - self.Misses
#         #
#         # self.MatchCount: int = len(self.__Matches)
#         # self.HomeMatchCount: int = len(self.__HomeMatches)
#         # self.GuestMatchCount: int = len(self.__GuestMatches)
#         # self.ShootCount: int = np.sum(self.__Shoots)
#         # self.MissesCount: int = np.sum(self.__Misses)
#         #
#         # self.Series = self.GetSerieses()
#     # def GetHomeCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         return Team.CountWhere('match_type', 'Home')
#     #
#     # def GetGuestCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         return Team.CountWhere('match_type', 'Guest')
#     #
#     # def GetWonCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         return self.GetWonHomeCount() + self.GetWonGuestCount()
#     #
#     # def GetWonHomeCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches where " \
#     #               f"team_id={Team.data['id']} and home_score > guest_score and match_type='home';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetWonGuestCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches where" \
#     #               f" team_id={Team.data['id']} and guest_score > home_score and match_type='guest';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetLostCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         return self.GetLostGuestCount()+self.GetLostHomeCount()
#     #
#     # def GetLostHomeCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and home_score < guest_score and match_type='home';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetLostGuestCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and guest_score < home_score and match_type='guest';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetDrawCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         return self.GetDrawGuestCount()+self.GetDrawHomeCount()
#     #
#     # def GetDrawHomeCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and guest_score = home_score and match_type='home';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetDrawGuestCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and guest_score = home_score and match_type='guest';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetWonPercent(self):
#     #     WonCount = self.GetWonCount()
#     #     TotalCount = self.GetTotalCount()
#     #     if WonCount == 0 or TotalCount == 0:
#     #         return 0
#     #     return round((WonCount / TotalCount) * 100, self.RoundLevel)
#     #
#     # def GetWonHomePercent(self):
#     #     return round((self.GetWonHomeCount() / self.GetWonCount()) * 100, self.RoundLevel)
#     #
#     # def GetWonGuestPercent(self):
#     #     return round((self.GetWonGuestCount() / self.GetWonCount()) * 100, self.RoundLevel)
#     #
#     # def GetLostPercent(self):
#     #     return round((self.GetLostCount() / self.GetTotalCount()) * 100, self.RoundLevel)
#     #
#     # def GetLostHomePercent(self):
#     #     return round((self.GetLostHomeCount() / self.GetLostCount()) * 100, self.RoundLevel)
#     #
#     # def GetLostGuestPercent(self):
#     #     return round((self.GetLostGuestCount() / self.GetLostCount()) * 100, self.RoundLevel)
#     #
#     # def GetDrawPercent(self):
#     #     return round((self.GetDrawCount() / self.GetTotalCount()) * 100, self.RoundLevel)
#     #
#     # def GetDrawHomePercent(self):
#     #     return round((self.GetDrawHomeCount() / self.GetDrawCount()) * 100, self.RoundLevel)
#     #
#     # def GetDrawGuestPercent(self):
#     #     return round((self.GetDrawGuestCount() / self.GetDrawCount()) * 100, self.RoundLevel)
#     #
#     # def GetTotalOppCount(self):
#     #     Nodes = self.__Team.GetNodesWhere('opponent', self.__OpponentName)
#     #     return len(Nodes)
#     #
#     # def GetWonOppCount(self):
#     #     return self.GetWonHomeOppCount() + self.GetWonGuestOppCount()
#     #
#     # def GetWonHomeOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score < home_score "\
#     #               f"and match_type='home';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetWonGuestOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score > home_score "\
#     #               f"and match_type='guest';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetLostOppCount(self):
#     #     return self.GetLostHomeOppCount() + self.GetLostGuestOppCount()
#     #
#     # def GetLostHomeOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score > home_score "\
#     #               f"and match_type='home';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetLostGuestOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score < home_score "\
#     #               f"and match_type='guest';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetDrawOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #             f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score = home_score;"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetDrawHomeOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score = home_score "\
#     #               f"and match_type='home';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetDrawGuestOppCount(self):
#     #     Team = self.__Team
#     #     if Team:
#     #         sql = f"select count(id) from matches " \
#     #               f"where team_id={Team.data['id']} and opponent='{self.__OpponentName}' and guest_score = home_score "\
#     #               f"and match_type='guest';"
#     #         result = self.__Db.ExecuteSelectSql(sql)
#     #         return result if result else 0
#     #
#     # def GetMisses(self):
#     #     return  self.__HomeMisses + self.__GuestMisses
#
#     # Matches
#
#     def __MakeMatches(self, rawMatches):
#         """Формирование фрейма матчей"""
#         RawMatches = rawMatches
#         Data = {'home': [Match.data['team'] for Match in RawMatches],
#                 'visitor': [Match.data['opponent'] for Match in RawMatches],
#                 'tour': [Match.data['tour'] for Match in RawMatches],
#                 'match_date': [Match.data['match_date'] for Match in RawMatches],
#                 'match_type': [Match.data['match_type'] for Match in RawMatches],
#                 'is_extra_time': [Match.data['is_extra_time'] for Match in RawMatches],
#                 'shoots': [],
#                 'misses': [],
#                 'penalty_shoots': [],
#                 'penalty_misses': []}
#
#         for match in rawMatches:
#             if match.data['match_type'] == 'guest':
#                 Data['shoots'].append(match.data['guest_score'])
#                 Data['misses'].append(match.data['home_score'])
#                 Data['penalty_shoots'].append(match.data['guest_penalty_score'])
#                 Data['penalty_misses'].append(match.data['home_penalty_score'])
#             else:
#                 Data['shoots'].append(match.data['home_score'])
#                 Data['misses'].append(match.data['guest_score'])
#                 Data['penalty_shoots'].append(match.data['home_penalty_score'])
#                 Data['penalty_misses'].append(match.data['guest_penalty_score'])
#
#         Matches = pd.DataFrame(Data, index=[Match.data['id'] for Match in RawMatches],
#                                columns=['match_date', 'tour', 'match_type', 'home', 'visitor', 'shoots', 'misses', 'is_extra_time', 'penalty_shoots', 'penalty_misses'])
#         return Matches
#
#     def GetHomeMatches(self):
#         Matches = self.__Matches
#         HomeMatches = Matches[Matches['match_type'] == 'home']
#         return HomeMatches
#
#     def GetGuestMatches(self):
#         Matches = self.__Matches
#         GuestMatches = Matches[Matches['match_type'] == 'guest']
#         return GuestMatches
#
#     def GetWinMatches(self):
#         Matches: pd.DataFrame = self.__Matches
#         WinMatches = Matches[(Matches['match_type'] == 'guest') & (Matches['guest_score'] > Matches['home_score']) |
#                              (Matches['match_type'] == 'home') & (Matches['guest_score'] < Matches['home_score'])]
#         return WinMatches
#
#     def GetLoseMatches(self):
#         Matches: pd.DataFrame = self.__Matches
#         LoseMatches = Matches[(Matches['match_type'] == 'guest') & (Matches['guest_score'] < Matches['home_score']) |
#                               (Matches['match_type'] == 'home') & (Matches['guest_score'] > Matches['home_score'])]
#         return LoseMatches
#
#     def GetDrawMatches(self):
#         Matches: pd.DataFrame = self.__Matches
#         DrawMatches = Matches[(Matches['home_score'] == Matches['guest_score'])]
#         return DrawMatches
#
#     def GetMatchesOnShoots(self):
#         """Получение списка матчей с количеством забитых мячей"""
#         HomeMatches = self.GetHomeMatches()
#         GuestMatches = self.GetGuestMatches()
#         ShootsOnMatches: pd.Series = pd.concat([HomeMatches.home_score, GuestMatches.guest_score], join='inner')
#         return ShootsOnMatches
#
#     def GetMatchesOnMisses(self):
#         """Получение списка матчей с количеством пропущенных мячей"""
#         HomeMatches = self.GetHomeMatches()
#         GuestMatches = self.GetGuestMatches()
#         ShootsOnMatches: pd.Series = pd.concat([HomeMatches.home_score, GuestMatches.guest_score], join='inner')
#         return ShootsOnMatches
#
#     def GetShootsOnDates(self):
#         ShootsOnMatches = self.GetMatchesOnShoots()
#         DatesOnMatches = self.GetDatesOnMatches()
#         ShootsOnDates = pd.DataFrame({'Dates': DatesOnMatches, 'Shoots': ShootsOnMatches}, index=DatesOnMatches.index)
#         return ShootsOnDates
#
#     def GetShootsOnTimes(self):
#         ShootsOnMatches: pd.Series = self.GetMatchesOnShoots()
#         TimesOnMatches: pd.Series = self.GetTimesOnMatches()
#         ShootsOnTimes = pd.DataFrame({'Shoots': ShootsOnMatches, 'Times': TimesOnMatches}, index=ShootsOnMatches.index)
#         return ShootsOnTimes
#
#     # Other
#     def GetTimesOnMatches(self):
#         Matches: pd.DataFrame = self.__Matches
#         TimesOnMatches = Matches.match_date.dt.time
#         return TimesOnMatches
#
#     def GetDatesOnMatches(self):
#         Matches: pd.DataFrame = self.__Matches
#         DatesOnMatches = Matches.match_date
#         return DatesOnMatches
#
#     def GetStat(self, signs: pd.Series, isInterval=False):
#         return VarSeries(signs, isInterval=isInterval)
#
#     def GetScore(self):
#         pass
#
#     def GetMissesByTime(self):
#         Result = []
#         for Match in self.__HomeMatches:
#             for i in range(Match.data['guest_score']):
#                 Result.append(Match.data['match_date'].time())
#         for Match in self.__GuestMatches:
#             for i in range(Match.data['home_score']):
#                 Result.append(Match.data['match_date'].time())
#         return Result
#
#     def GetSerieses(self):
#         Matches = sorted(self.__Matches, key=lambda match: match.data['match_date'])
#         WinSeries, WinSeriesTotal = [], []
#         LoseSeries, LoseSeriesTotal = [], []
#         DrawSeries, DrawSeriesTotal = [], []
#         for i in range(len(Matches)-1):
#             if Matches[i].data['match_type'] == 'home':
#                 if Matches[i].data['home_score'] > Matches[i].data['guest_score']:
#                     WinSeries.append(Matches[i])
#                     if len(LoseSeries) > 1: LoseSeriesTotal.append(LoseSeries)
#                     if len(DrawSeries) > 1: DrawSeriesTotal.append(DrawSeries)
#                     LoseSeries = []
#                     DrawSeries = []
#                 elif Matches[i].data['home_score'] < Matches[i].data['guest_score']:
#                     LoseSeries.append(Matches[i])
#                     if len(WinSeries) > 1: WinSeriesTotal.append(WinSeries)
#                     if len(DrawSeries) > 1: DrawSeriesTotal.append(DrawSeries)
#                     WinSeries = []
#                     DrawSeries = []
#                 else:
#                     DrawSeries.append(Matches[i])
#                     if len(WinSeries) > 1: WinSeriesTotal.append(WinSeries)
#                     if len(LoseSeries) > 1: LoseSeriesTotal.append(LoseSeries)
#                     LoseSeries = []
#                     WinSeries = []
#             elif Matches[i].data['match_type'] == 'guest':
#                 if Matches[i].data['guest_score'] > Matches[i].data['home_score']:
#                     WinSeries.append(Matches[i])
#                     if len(LoseSeries) > 1: LoseSeriesTotal.append(LoseSeries)
#                     if len(DrawSeries) > 1: DrawSeriesTotal.append(DrawSeries)
#                     LoseSeries = []
#                     DrawSeries = []
#                 elif Matches[i].data['guest_score'] < Matches[i].data['home_score']:
#                     LoseSeries.append(Matches[i])
#                     if len(WinSeries) > 1: WinSeriesTotal.append(WinSeries)
#                     if len(DrawSeries) > 1: DrawSeriesTotal.append(DrawSeries)
#                     DrawSeries = []
#                     WinSeries = []
#                 else:
#                     DrawSeries.append(Matches[i])
#                     if len(WinSeries) > 1: WinSeriesTotal.append(WinSeries)
#                     if len(LoseSeries) > 1: LoseSeriesTotal.append(LoseSeries)
#                     LoseSeries = []
#                     WinSeries = []
#         Result = {'Win': WinSeriesTotal, 'Lose': LoseSeriesTotal, 'Draw': DrawSeriesTotal}
#         return Result
#
#     def GetMissesInTime(self):
#         Result = {}
#         for Time in self.__MatchTimes:
#             Shoots = []
#             for Match in self.__HomeMatches:
#                 if Match.data['match_date'].time() == Time:
#                     Shoots.append(Match.data['guest_score'])
#             for Match in self.__GuestMatches:
#                 if Match.data['match_date'].time() == Time:
#                     Shoots.append(Match.data['home_score'])
#             Result[Time] = Shoots
#         return Result
#
#     def GetShootCountInTime(self):
#         ShootsInTime: dict = self.GetShootsInTime()
#         Result = {}
#         for Time, Shoots in ShootsInTime.items():
#             Result[Time] = np.sum(Shoots)
#         return Result
#
#     # props
#     @property
#     def TotalCount(self):
#         return self.__TotalCount
#
#     @property
#     def TotalHomeCount(self):
#         return self.__TotalHomeCount
#
#     @property
#     def TotalGuestCount(self):
#         return self.__TotalGuestCount
#
#     @property
#     def LostCount(self):
#         return self.__LostCount
#
#     @property
#     def LostHomeCount(self):
#         return self.__LostHomeCount
#
#     @property
#     def LostGuestCount(self):
#         return self.__LostGuestCount
#
#     @property
#     def WonCount(self):
#         return self.__WonCount
#
#     @property
#     def WonHomeCount(self):
#         return self.__WonHomeCount
#
#     @property
#     def WonGuestCount(self):
#         return self.__WonGuestCount
#
#     @property
#     def DrawCount(self):
#         return self.__DrawCount
#
#     @property
#     def DrawHomeCount(self):
#         return self.__DrawHomeCount
#
#     @property
#     def DrawGuestCount(self):
#         return self.__DrawGuestCount
#
#     @property
#     def WonPercent(self):
#         return self.__WonPercent
#
#     @property
#     def WonHomePercent(self):
#         return self.__WonHomePercent
#
#     @property
#     def WonGuestPercent(self):
#         return self.__WonGuestPercent
#
#     @property
#     def LostPercent(self):
#         return self.__LostPercent
#
#     @property
#     def LostHomePercent(self):
#         return self.__LostHomePercent
#
#     @property
#     def LostGuestPercent(self):
#         return self.__LostGuestPercent
#
#     @property
#     def DrawPercent(self):
#         return self.__DrawPercent
#
#     @property
#     def DrawHomePercent(self):
#         return self.__DrawHomePercent
#
#     @property
#     def DrawGuestPercent(self):
#         return self.__DrawGuestPercent
#
#     @property
#     def Shoots(self):
#         return self.__Shoots
#
#     @property
#     def HomeShoots(self):
#         return self.__HomeShoots
#
#     @property
#     def GuestShoots(self):
#         return self.__GuestShoots
#
#     @property
#     def Misses(self):
#         return self.__Misses
#
#     @property
#     def HomeMisses(self):
#         return self.__HomeMisses
#
#     @property
#     def GuestMisses(self):
#         return self.__GuestMisses
#
#     @property
#     def HomeMatches(self):
#         return self.__HomeMatches
#
#     @property
#     def GuestMatches(self):
#         return self.__GuestMatches
#
#     @property
#     def Diffs(self):
#         return self.__Diffs
#
#     @property
#     def MatchTimes(self):
#         return self.__MatchTimes
#
#     @property
#     def Matches(self):
#         return self.__Matches
#
#     @property
#     def HomeMatches(self):
#         return self.GetHomeMatches()

# class VarSeries:
#     class Measurement(Enum):
#         percent = 1
#
#     def __init__(self, population: pd.Series, roundLevel=2, isInterval=False):
#         self._RoundLevel = roundLevel
#         self._IsInterval = isInterval
#
#         self._P = population
#         self._x: np.ndarray = self.Cast_x()
#         self._f: pd.Series = self.Cast_f()
#         self._N: int = self.GetN()
#         self._W: pd.Series = self.CastW()
#
#     def Cast_x(self):
#         P = self._P
#         x: np.ndarray = P.unique()
#         x.sort()
#         return x
#
#     def Cast_f(self):
#         if self._IsInterval:
#             Interval: pd.Categorical = self._CastIntervals()
#             f: pd.Series = Interval.value_counts()
#             return f
#         P: pd.Series = self._P
#         f: pd.Series = P.value_counts()
#         return f
#
#     def _CastIntervals(self):
#         x: np.ndarray = self.Cast_x()
#         P: pd.Series = self._P
#         h = self._Cast_h()
#         Intervals: pd.Categorical = pd.cut(P.values, range(x.min(), x.max() + 2, h), right=False)
#         return Intervals
#
#     def _Cast_h(self):
#         N: int = self.GetN()
#         x: np.ndarray = self.Cast_x()
#         k = math.ceil(1 + 3.222 * math.log10(N))
#         h = math.ceil((x.max() - x.min()) / k)
#         return h
#
#     def GetN(self):
#         N = self._P.count()
#         return N
#
#     def CastW(self):
#         f = self.Cast_f()
#         N = self.GetN()
#         W = f.div(N).mul(100)
#         return W
#
#     #     self.EstimateCharacteristics()
#     #
#     # def EstimateCharacteristics(self):
#     #     if self._IsInterval:
#     #         Intervals: pd.Categorical = pd.cut(self._P.values, [0,2,3,4])
#     #         levels: pd.IntervalIndex = Intervals.categories
#     #         fInterval: pd.Series = Intervals.value_counts()
#     #         tmp = pd.Series(Intervals)
#     #         Val = self._P.min()
#     #         h = self.Get_h()
#     #         k = self.Get_k()
#     #         for i in range(k):
#     #             CondList = [Val < self._P < Val + h]
#     #             ChoiceList = [self._P]
#     #             tmp = np.select(CondList, ChoiceList)
#     #             Start = self.__FloatToTime(Val).strftime("%H:%M")
#     #             Val += h
#     #             End = self.__FloatToTime(Val).strftime("%H:%M")
#     #             Intervals.append(f"{Start}-{End}")
#     #         self._x = np.array(Intervals)
#
#     def __TimeToFloat(self, time: time):
#         Result = time.hour + time.second / 60
#         return Result
#
#     def __FloatToTime(self, num: float):
#         Minute = int(num%1 * 60)
#         Hour = int(math.trunc(num))
#         Result = time(Hour, Minute)
#         return Result
#
#     def GetIndex(self, array, value):
#         return np.isin(array, value)
#
#     @property
#     def x(self):
#         if self._IsInterval:
#             Intervals: pd.Categorical = self._CastIntervals()
#             return Intervals.categories
#         return self._x
#
#     @property
#     def f(self):
#         return self._f
#
#     @property
#     def W(self):
#         return self._W
#
#     @property
#     def N(self):
#         return self._N


# class IntervalVarSeries:
#     def __init__(self, population: pd.Series):
#         self._P = population
#         self._x: np.ndarray = self._P.unique()
#         self._N = self._P.count()
#         tmp = self._x.max()
#         self._k = math.ceil(1+3.222 * math.log10(self._N))
#         self._h = math.ceil((self._x.max() - self._x.min()) / self._k)
#         self._Intervals = pd.cut(self._P, range(self._x.min(), self._x.max()+2, self._h), right=False)
#         self._f = pd.value_counts(self._Intervals)
#         pass


# class TeamStatPeriod:
#     def __init__(self, teamName: str, tournamentName: str, seasons: list, opponentName: str = None):
#         self.__SeasonsForStat = seasons
#         self.__TournamentName = tournamentName
#         self.__TeamName = teamName
#         self.__OpponentName = opponentName
#
#         self.__Seasons = []
#         self.__Wins = []
#         self.__Loses = []
#         self.__Draws = []
#         self.__Shoots = []
#         self.__Misses = []
#
#         self.StatFieldsInit()
#
#     def StatFieldsInit(self):
#         for Season in self.__SeasonsForStat:
#             Db = Database(Database.DB_PREFIX + str(Season))
#             TournamentId = Db.GetTournamentId(self.__TournamentName)
#             TeamId = Db.GetTeamId(self.__TeamName, TournamentId)
#             if TournamentId is None or TeamId is None: continue
#
#             Team = Node(ParsingTypes.team, data=Db.GetTeamRow(TeamId, TournamentId))
#             Matches = Db.GetMatchRows(TeamId)
#             if not Matches: continue
#             [Team.set_child(Node(ParsingTypes.match, data=Row)) for Row in Matches]
#
#             Stat = MatchesAnalysis(Team, Season, self.__OpponentName)
#             self.__Seasons.append(Season)
#             self.__Wins.append(Stat.GetWonCount())
#             self.__Loses.append(Stat.GetLostCount())
#             self.__Draws.append(Stat.GetDrawCount())
#             self.__Shoots.extend(Stat.Shoots)
#             self.__Misses.extend(Stat.GetMisses())
#
#     @property
#     def Shoots(self):
#         return self.__Shoots
#
#     @property
#     def Misses(self):
#         return self.__Misses
#
#     @property
#     def ShootsCount(self):
#         return len(self.__Shoots)
#
#     @property
#     def MissesCount(self):
#         return len(self.__Misses)


# class TournamentStat:
#     def __init__(self, tournament: Node, dbName: str):
#         self.Tournament = tournament
#         self.Db = Database(dbName)
#
#     def GetMatchCount(self):
#         sql = f"select count(id) from teams where tournament_id={self.Tournament.data['id']}"


class TeamStatItem:
    def __init__(self, name: str, data: list = None, parent=None):
        self.ParentItem: TeamStatItem = parent
        self.Data: list = [name] + data
        self.__ChildItems: list = []  # list of StatItem
        if self.ParentItem:
            self.ParentItem.AppendChildItem(self)

    def AppendChildItem(self, item):
        self.__ChildItems.append(item)

    def AppendData(self, key, value):
        self.Data[key] = value

    def GetChild(self, row: int):
        return self.__ChildItems[row]

    def GetChildren(self):
        return self.__ChildItems

    def GetChildCount(self):
        return len(self.__ChildItems)

    def GetRow(self):
        if self.ParentItem:
            return self.ParentItem.__ChildItems.index(self)
        return 0

    def GetColumnCount(self):
        return len(self.Data)

    def GetData(self, column: int):
        return self.Data[column]

    def GetParentItem(self):
        return self.ParentItem


class TeamStatModel(QtCore.QAbstractItemModel):
    def __init__(self, rootItem: TeamStatItem,  parent=None):
        super().__init__(parent)
        self.RootItem: TeamStatItem = None
        self.Headers: list = ['Stat value']
        self.RootItem = rootItem

    # inherits methods
    def index(self, row: int, col: int = 0, parent: QtCore.QModelIndex = QtCore.QModelIndex(), *args, **kwargs):
        try:
            if not self.hasIndex(row, col, parent):
                return QtCore.QModelIndex()

            ParentItem: TeamStatItem = None
            if not parent.isValid():
                ParentItem = self.RootItem
            else:
                ParentItem = parent.internalPointer()

            ChildItem = ParentItem.GetChild(row)
            if ChildItem:
                return self.createIndex(row, col, ChildItem)
            else:
                return QtCore.QModelIndex()
        except Exception as Error:
            raise Exception(str(Error))

    def rowCount(self, parent: QtCore.QModelIndex = None, *args, **kwargs):
        try:
            if not parent:
                parent = QtCore.QModelIndex()
            ParentItem: TeamStatItem = None
            if parent.column() > 0:
                return 0
            if not parent.isValid():
                ParentItem = self.RootItem
            else:
                ParentItem = parent.internalPointer()
            return ParentItem.GetChildCount()
        except Exception as Error:
            raise Exception(str(Error))

    def columnCount(self, parent: QtCore.QModelIndex = None, *args, **kwargs):
        if not parent:
            parent = QtCore.QModelIndex()
        if parent.isValid():
            return parent.internalPointer().GetColumnCount()
        else:
            return self.RootItem.GetColumnCount()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role != QtCore.Qt.DisplayRole:
            return None
        Item: TeamStatItem = index.internalPointer()
        return Item.GetData(index.column())

    def parent(self, index: QtCore.QModelIndex = None):
        if not index.isValid():
            return QtCore.QModelIndex()
        ChildItem: TeamStatItem = index.internalPointer()
        ParentItem: TeamStatItem = ChildItem.GetParentItem()

        if ParentItem is self.RootItem:
            return QtCore.QModelIndex()
        return self.createIndex(ParentItem.GetRow(), 0, ParentItem)

    def headerData(self, section: int, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.RootItem.Data[section]
        return None

    def flags(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return 0
        return super().flags(index)


class TeamListModel(QtCore.QAbstractListModel):
    class TeamRoles(Enum):
        NameRole = QtCore.Qt.DisplayRole
        IdRole = QtCore.Qt.UserRole + 1

    def __init__(self):
        super().__init__()
        self.Teams = []
        roles = {self.TeamRoles.NameRole: 'name', self.TeamRoles.IdRole: 'id'}

    def data(self, QModelIndex: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        result = None
        Team = self.Teams[QModelIndex.row()]
        if role == QtCore.Qt.UserRole:
            result = Team.data['id']
        elif role == QtCore.Qt.DisplayRole:
            result = Team.data['name']
        return result

    def AddTeamNode(self, team: Node):
        self.Teams.append(team)

    def AddTeamNodes(self, teams: list):
        self.Teams.extend(teams)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.Teams)


class SeasonListModel(QtCore.QAbstractListModel):
    def __init__(self, seasonList: list):
        super().__init__()
        self.__Seasons: list = []
        for Season in seasonList:
            self.__Seasons.append(['Season ' + str(Season), Season])

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__Seasons)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        Row = index.row()
        result = None
        if role == QtCore.Qt.DisplayRole:
            result = self.__Seasons[Row][0]
        elif role == QtCore.Qt.UserRole:
            result = self.__Seasons[Row][1]
        return result


class TournamentListModel(QtCore.QAbstractListModel):
    def __init__(self, season: int):
        super().__init__()
        Season = season if type(season) is str else str(season)
        Db = Database(Database.DB_PREFIX + Season)
        TournamentRows = Db.ExecuteSelectSql(f"select name, id from tournaments")
        if type(TournamentRows) is list:
            self.__Tournaments: list = [list(Row.values()) for Row in TournamentRows]
        else:
            self.__Tournaments: list = [list(TournamentRows.values())]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__Tournaments)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        Row = index.row()
        result = None
        if role == QtCore.Qt.DisplayRole:
            result = self.__Tournaments[Row][0]
        elif role == QtCore.Qt.UserRole:
            result = self.__Tournaments[Row][1]
        return result


class BaseListModel(QtCore.QAbstractListModel):
    def __init__(self, items):
        super().__init__()
        self.__Items = []
        if type(items) is list:
            self.__Items.extend(items)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.__Items)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        Row = index.row()
        result = None
        if role == QtCore.Qt.DisplayRole:
            result = self.__Items[Row][0]
        elif role == QtCore.Qt.UserRole:
            result = self.__Items[Row][1]
        return result

