from chempionat_ru_parser import ParsingTypes, Node
from PyQt5 import QtSql, QtCore
from mysql.connector import MySQLConnection, Error
from configparser import ConfigParser
import logging
import logging.config
from datetime import datetime
from sqlalchemy.orm import relationship, Session

class Database:
    DB_PREFIX = 'football_stats_'

    def __init__(self, db_name):
        self.db_name = db_name
        self.__path_to_mysql_config = "config/mysql_cfg.ini"
        logging.config.fileConfig('config/log_cfg.ini')
        self.log = logging.getLogger('ex')
        self.result = {'added': 0, 'missed': 0, 'duplicated': 0, 'total': 0}
        try:


            # rpl = Tournament(Id=542, Name='Россия-Премьер лига', Members=16)
            # match = Match(Date=datetime(2002, 1, 1))
            # HomeStat = Stat(Attacks=4)
            # GuestStat = Stat(Attacks=3)
            # HomeTeam = Team(Name='ЦСКА', City='Москва')
            # GuestTeam = Team(Name='Спартак', City='Москва')
            # Pl2 = Player(Name='Мамедов')
            # Pl1 = Player(Name='Аршавин')
            # Miss1 = MissPenalty(Minute=24)
            # Punish1 = Punishment(Card='yellow', Minute=65)
            # Goal1 = Goal(BecameScore='1:2', Minute=22)
            # Goal1.GoalKicker = Pl1
            # Goal1.Assistant = Pl2
            # Goal2 = Goal(BecameScore='1:3', Minute=43)
            # Goal2.GoalKicker = Pl1
            # Goal2.Assistant = Pl2
            # Pl1.MissPenalties = [Miss1]
            # Pl1.Punishments = [Punish1]
            #
            # match.Tournament = rpl
            # match.HomeStat = HomeStat
            # match.GuestStat = GuestStat
            # match.HomeTeam = HomeTeam
            # match.GuestTeam = GuestTeam
            # match.Players = [Pl1, Pl2]
            # match.MissPenalties = [Miss1]
            # match.Punishments = [Punish1]
            # match.Goals = [Goal1, Goal2]

            pass
        except Exception as Err:
            raise Exception(Err)

    def __get_connection(self):
        try:
            connection = MySQLConnection(**self.__read_db_config())
            return connection
        except Exception as e:
            self.log.exception(e)

    def __get_qt_connection(self):
        sql_params = self.__read_db_config()
        connection = QtSql.QSqlDatabase().addDatabase('QMYSQL')
        connection.setDatabaseName(self.db_name)
        connection.setHostName(sql_params['host'])
        connection.setUserName(sql_params['user'])
        connection.setPassword(sql_params['password'])
        return connection

    def __GetValidValue(self, key: str, value):
        if key == 'id' or key == 'home_score' or key == 'guest_score':
            Value = int(value) if type(value) is not int else value
        elif key == 'match_date':
            Value = datetime.strptime(value, "%d.%m.%Y %H:%M")
        elif key == 'is_extra_time':
            Value = bool(value)
        else:
            Value = value if value != '' else None
        return Value

    def is_exist(self):
        connection = self.__get_connection()
        cursor = connection.cursor()
        cursor.execute('SHOW DATABASES;')
        for _name in cursor:
            if _name[0] == self.db_name:
                return True
        return False

    def GetTournamentId(self, tournamentName: str):
        Id = self.ExecuteSelectSql(f"select id from tournaments where name='{tournamentName}'")
        return Id if Id else None

    def GetTeamId(self, teamName: str, tournamentId: int):
        Id = self.ExecuteSelectSql(f"select id from teams where name='{teamName}' and tournament_id={tournamentId}")
        return Id if Id else None

    def GetTeamRow(self, teamId: int, tournamentId: int = None):
        if tournamentId:
            Rows = self.ExecuteSelectSql(f"select * from teams where id={teamId} and tournament_id={tournamentId}")
        else:
            Rows = self.ExecuteSelectSql(f"select * from teams where id={teamId}")
        return Rows

    def GetMatchRows(self, teamId: int = None):
        Connection = self.__get_qt_connection()
        Connection.setDatabaseName(self.db_name)
        Connection.open()
        if teamId:
            Sql = f"select * from matches where team_id={teamId}"
        else:
            Sql = f"select * from matches"
        try:
            if Connection.isOpen():
                Query = QtSql.QSqlQuery(Sql)
                if Query.isActive():
                    if Query.size() not in [-1, 0]:
                        FieldCount = Query.record().Count()
                        Result = []
                        while Query.next():
                            if Query.isValid():
                                Row = {}
                                for i in range(FieldCount):
                                    FieldName = Query.record().fieldName(i)
                                    Row[FieldName] = self.__GetValidValue(FieldName, Query.value(i))
                                Result.append(Row)
                            else:
                                raise Exception(Query.lastError().text())
                        return Result
                else:
                    raise Exception(Query.lastError().text())
            else:
                raise Exception(Connection.lastError().text())

        except Exception as Err:
            self.log.exception(f'Error getting match rows for id={str(teamId)}:' + str(Err))
        finally:
            Connection.close()

    def IsTeamExist(self, teamId, tournamentId):
        Row = self.ExecuteSelectSql(f"select id from teams where id={teamId} and tournament_id={tournamentId}")
        return True if Row else False

    def IsTournExist(self, Id: int):
        Row = self.ExecuteSelectSql(f"select id from tournaments where id={Id}")
        return True if Row else False

    def get_all_rows(self, t_name, *args):
        conn = self.__get_qt_connection()
        conn.setDatabaseName(self.db_name)
        conn.open()
        if conn.isOpen():
            query = QtSql.QSqlQuery()
            query.exec(f'select * from {t_name};')
            if query.isActive():
                result = []
                query.first()
                while query.isValid():
                    row = {}
                    for arg in args:
                        row[arg] = query.value(arg)
                    result.append(row)
                    query.next()
        else:
            err = conn.lastError().text()
        conn.close()
        return result

    def ExecuteSelectSql(self, sql: str):
        conn = self.__get_qt_connection()
        conn.setDatabaseName(self.db_name)
        conn.open()
        try:
            if conn.isOpen():
                query = QtSql.QSqlQuery(sql)
                query.exec(sql)
                conn.close()
                tmp = query.size()
                QueryError = query.lastError().text()
                if query.isActive():
                    if query.size() != -1 and query.size() != 0:
                        result = []
                        while query.next():
                            row = {}
                            for index in range(query.record().Count()):
                                col = query.record().fieldName(index)
                                row[query.record().fieldName(index)] = query.value(index)
                            result.append(row)
                        if len(result) == 1:
                            result = result[0]
                            if len(result.values()) == 1:
                                result = list(result.values())[0]
                        return result
        except Exception as Error:
            self.log.exception('Execute sql error:' + str(Error))

    def __read_db_config(self, section='mysql'):
        """ Read database configuration file and return a dictionary object"""
        parser = ConfigParser()
        parser.read(self.__path_to_mysql_config)
        sql_params = {}
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                sql_params[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, self.__path_to_mysql_config))
        return sql_params

    def create_database(self):
        cursor, connection = None, None
        try:
            connection = self.__get_connection()
            cursor = connection.cursor()
            cursor.execute('CREATE DATABASE ' + self.db_name)
        except Error as e:
            if e.errno != 1007:
                self.log.exception(e.msg)
        except Exception as e:
            self.log.exception(f'Ошибка создания базы данных {self.db_name}: ' + str(e))
        finally:
            cursor.close()
            connection.close()

    def CreateTables(self):
        connection = self.__get_connection()
        cursor = connection.cursor()
        connection.database = self.db_name
        try:
            # sql_tournaments = "CREATE TABLE tournaments (" \
            #               "id int not null primary key," \
            #               "name varchar(100) not null," \
            #               "country varchar(50) not null," \
            #               "start_date varchar(20) not null," \
            #               "end_date varchar(20) not null," \
            #               "url varchar(150)," \
            #               "constraint unique_idx unique (name,country,start_date,end_date));"
            #
            # sql_teams = "CREATE TABLE teams (" \
            #                 "id int not null primary key," \
            #                 "tournament_id int not null,"\
            #                 "name varchar(100) not null," \
            #                 "city varchar(100) not null," \
            #                 "url varchar(150)," \
            #                 "constraint unique_idx unique (tournament_id,name)," \
            #                 "constraint team_tournament_fk foreign key(tournament_id) references tournaments(id));"
            #
            # sql_players = "CREATE TABLE players (" \
            #               "id int not null primary key," \
            #               "team_id int not null," \
            #               "name varchar(100) not null," \
            #               "nationality varchar(50)," \
            #               "role varchar(20)," \
            #               "birth varchar(15)," \
            #               "growth varchar(10)," \
            #               "weight varchar(10)," \
            #               "constraint unique_idx unique (team_id,name,birth)," \
            #               "constraint player_team_fk foreign key (team_id) references teams(id));"

            sql_matches = "CREATE TABLE matches (" \
                          "id int not null primary key," \
                          "tourn_name varchar(150)" \
                          "tourn_dates varchar(50)" \
                          "team_count int," \
                          "stadium varchar(100)" \
                          "referee varchar(150)" \
                          "stage varchar(100)," \
                          "home_team varchar(100)," \
                          "guest_team varchar(100)," \
                          "date datetime," \
                          "home_score int," \
                          "guest_score int)," \
                          "home_penalty_score int," \
                          "guest_penalty_score int," \
                          "home_tech_score varchar(10)," \
                          "guest_tech_score varchar(10)," \
                          "is_extra boolean," \
                          "home_attacks int," \
                          "home_dangerous_attacks int," \
                          "home_shoots int," \
                          "home_shoots_on_goal int," \
                          "home_bars int," \
                          "home_fouls int," \
                          "home_corners int," \
                          "home_offsides int," \
                          "home_control int," \
                          "home_locked_shoots int," \
                          "home_free_kicks int," \
                          "home_goal_kicks int," \
                          "home_outs int," \
                          "home_cautions int," \
                          "home_offs int," \
                          "guest_attacks int," \
                          "guest_dangerous_attacks int," \
                          "guest_shoots int," \
                          "guest_shoots_on_goal int," \
                          "guest_bars int," \
                          "guest_fouls int," \
                          "guest_corners int," \
                          "guest_offsides int," \
                          "guest_control int," \
                          "guest_locked_shoots int," \
                          "guest_free_kicks int," \
                          "guest_goal_kicks int," \
                          "guest_outs int," \
                          "guest_cautions int," \
                          "guest_offs int," \
                          ");"

            sql_matches = "CREATE TABLE matches (" \
                          'id int not null primary key,' \
                          'tourn_name varchar(150),' \
                          'tourn_start datetime,' \
                          'tourn_end datetime,' \
                          'stadium varchar(150),' \
                          'referee varchar(150),' \
                          'team_count int,'\
                          'home_team varchar(100),'\
                          'guest_team varchar(100),'\
                          'date datetime,'\
                          'stage varchar(100),'\
                          'is_extra bool,'\
                          'home_score int,'\
                          'guest_score int,'\
                          'home_penalty_score int,'\
                          'guest_penalty_score int,'\
                          'home_tech_score int,'\
                          'guest_tech_score int,'\
                          'home_goal_list int,'\
                          'guest_goal_list int,'\
                          'home_attacks int,'\
                          'home_dangerous_attacks int,'\
                          'home_shoots int,'\
                          'home_shoots_on_goal int,'\
                          'home_bars int,'\
                          # 'home_fouls': MatchStat[0].get('Фолы'),
                          # 'home_corners': MatchStat[0].get('Угловые'),
                          # 'home_offsides': MatchStat[0].get('Офсайды'),
                          # 'home_control': MatchStat[0].get('% владения мячом'),
                          # 'home_locked_shoots': MatchStat[0].get('Заблокированные удары'),
                          # 'home_free_kicks': MatchStat[0].get('Штрафные удары'),
                          # 'home_goal_kicks': MatchStat[0].get('Удары от ворот'),
                          # 'home_outs': MatchStat[0].get('Ауты'),
                          # 'home_cautions': MatchStat[0].get('Предупреждения'),
                          # 'home_offs': MatchStat[0].get('Удаления'),
                          # 'guest_attacks': MatchStat[1].get('Атаки'),
                          # 'guest_dangerous_attacks': MatchStat[1].get('Опасные атаки'),
                          # 'guest_shoots': MatchStat[1].get('Удары по воротам'),
                          # 'guest_shoots_on_goal': MatchStat[1].get('Удары в створ'),
                          # 'guest_bars': MatchStat[1].get('Штанги/перекладины'),
                          # 'guest_fouls': MatchStat[1].get('Фолы'),
                          # 'guest_corners': MatchStat[1].get('Угловые'),
                          # 'guest_offsides': MatchStat[1].get('Офсайды'),
                          # 'guest_control': MatchStat[1].get('% владения мячом'),
                          # 'guest_locked_shoots': MatchStat[1].get('Заблокированные удары'),
                          # 'guest_free_kicks': MatchStat[1].get('Штрафные удары'),
                          # 'guest_goal_kicks': MatchStat[1].get('Удары от ворот'),
                          # 'guest_outs': MatchStat[1].get('Ауты'),
                          # 'guest_cautions': MatchStat[1].get('Предупреждения'),
                          # 'guest_offs': MatchStat[1].get('Удаления')

            sql_list = [sql_matches]

            for sql in sql_list:
                result = cursor.execute(sql)
                connection.commit()
        except Error as e:
            if e.errno != 1050:
                self.log.exception(e.msg)
        except Exception as e:
            self.log.exception(e)
            raise Exception(e)
        finally:
            cursor.close()
            connection.close()

    def AddRows(self, rows, tableName):
        Sql = f"insert into {tableName}() values();"

    def pre_order_adding(self, node: Node, connection):
        table_name = None
        if node.key is ParsingTypes.tournament:
            table_name = 'tournaments'
        elif node.key is ParsingTypes.team:
            table_name = 'teams'
        elif node.key is ParsingTypes.match:
            table_name = 'matches'
        elif node.key is ParsingTypes.Lineup:
            table_name = 'players'

        if node.key is not ParsingTypes.root:
            sql = f"insert into {table_name}({','.join([field for field in node.data.keys()])})" \
                f"values({','.join(['%s' for i in range(len(node.data))])})"
            try:
                cursor = connection.cursor()
                result = cursor.execute(sql, ([value for value in node.data.values()]))
                connection.commit()
                self.result['added'] += 1
                cursor.close()
            except Error as e:
                if e.errno != 1062:
                    self.result['missed'] += 1
                    self.log.exception(str(e) + '\n data: ' + ','.join([str(value) for value in node.data.values]))
                else:
                    self.result['duplicated'] += 1
            except Exception as e:
                self.log.exception(str(e) + '\n data: ' + ','.join([str(value) for value in node.data.values]))

        for child in node.get_children():
            self.pre_order_adding(child, connection)

    def add_rows_to_db(self, node: Node):
        connection = self.__get_connection()
        connection.database = self.db_name
        self.result['total'] = node.Count()
        self.pre_order_adding(node, connection)
        connection.close()

    def get_rows(self, Table, *args, **kwargs):
        conn = self.__get_qt_connection()
        conn.setDatabaseName(self.db_name)
        whereCondition = ' and '.join([str(k) + '=' + str(v) for k, v in kwargs.items()])
        sql = f"select {','.join([field for field in args])} from {Table} where {whereCondition};"
        conn.open()
        if conn.isOpen():
            query = QtSql.QSqlQuery()
            query.exec(sql)
            if query.isActive():
                if query.size() != -1:
                    result = []
                    while query.next():
                        row = {}
                        for index in range(query.record().Count()):
                            col = query.record().fieldName(index)
                            row[query.record().fieldName(index)] = query.value(index)
                        result.append(row)
                    return result
            else:
                err = query.lastError().text()
                return None
        conn.close()
