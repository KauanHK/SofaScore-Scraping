import requests
import pandas as pd
import csv
import os
from utils import Urls, Score, SobreCargaDeAcessos
from typing import Union, Literal


class Base:

    url: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def json(self) -> dict:
        raise NotImplementedError(f'{self.__class__.__name__} não implementou o método json')
    
    def _input(self, options: list[str]) -> int:

        os.system('cls' if os.name == 'nt' else 'clear')

        for i, option in enumerate(options, 1):
            print(f'{i} - {option}')

        n = int(input('Escolha uma opção: '))
        return n-1

    def api_json(self, msg: str | None = None) -> dict:

        print(msg)
        response = requests.get(self.url)
        if response.status_code == 403:
            raise SobreCargaDeAcessos('Você fez requisições demais para o SofaScore e seu acesso foi bloquado temporariamente')
        return response.json()

class MainTournaments(Base):

    def __init__(self) -> None:
        self.url = Urls.main_tournaments()

    def load(self) -> list["Tournament"]:

        data: dict[str, int] = self.json()
        result: list[Tournament] = []
        for name_id, category in zip(data.items(), self._categories):
            name, id = name_id
            tournament = Tournament(id, name, category)
            result.append(tournament)
        return result
    
    def input(self) -> "Tournament":

        data = self.api_json('Carregando principais torneios...')
        data = data["uniqueTournaments"]
        options = map(lambda t: t["name"], data)
        i = self._input(options)

        data_tournament = data[i]
        data_category = data_tournament["category"]

        id = data_tournament["id"]
        name = data_tournament["name"]

        category_id = data_category["id"]
        category_name = data_category["name"]

        return Tournament(id, name, Category(category_id, category_name))
    
    def json(self) -> dict[str, int]:

        response_data = self.api_json('Carregando principais torneios...')
        response_data = response_data["uniqueTournaments"]
        data = {}
        self._categories = []
        for t in response_data:
            data[t["name"]] = t["id"]
            self._categories.append(Category(t["id"], t["name"]))
        return data

class Categories(Base):

    def load(self) -> list["Category"]:

        data: dict[str, int] = self.json()
        result: list[Category] = []
        for name, id in data.items():
            category = Category(id, name)
            result.append(category)
        return result

    def json(self)  -> dict[str, int]:

        data = self.api_json('Carregando categorias...')
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
        return dict(sorted(data.items(), key=lambda kv: kv[0]))
    
    def input(self) -> "Category":
        return self._input()
    
class Category(Base):
    
    def __init__(self, id: int, name: str | None = None):
        super().__init__(id, name)

    def load(self) -> list["Tournament"]:

        data: dict[str, int] = self.json()
        result: list[Tournament] = []
        for name, id in data.items():
            category = Tournament(id, name, self)
            result.append(category)
        return result
    
    def json(self) -> dict[str, int]:

        data = self.api_json(f'Carregando categoria {self.name}...')
        data = data["groups"][0]["uniqueTournaments"]
        return {t["name"]: t["id"] for t in data}

class Tournament(Base):

    def __init__(
            self,
            id: int,
            name: str | None = None,
            category: Category | None = None
            ) -> None:
        super().__init__(id, name)
        self.category = category
        self.url = Urls.tournament(self.id)

    def load(self) -> list["Season"]:

        data: dict[str, int] = self.json()
        result: list[Season] = []
        for name, id in data.items():
            season = Season(id, name, self)
            result.append(season)
        return result

    def json(self) -> dict[str, int]:
        
        data = self.api_json(f'Carregando {self.name}...')
        data = data["seasons"]
        return {s["name"]: s["id"] for s in data}
    
    def input(self) -> "Season":
        data = self.api_json(f"Carregando {self.name if self.name else ''}")
        data = data["seasons"]
        options = map(lambda s: s["name"], data)
        i = self._input(options)
        return Season(data[i]["id"], data[i]["name"], self)

class Season(Base):

    def __init__(
            self,
            id: int,
            name: str | None = None,
            tournament: Tournament | None = None,
            ) -> None:
        super().__init__(id, name)
        self.tournament = tournament
        self._cr: int | None = None

    @property
    def current_round(self) -> int:
        if self._cr is not None:
            return self._cr
        url = Urls.rounds(self.tournament.id, self.id)
        print('Estamos na rodada...', end='\r')
        data = requests.get(url).json()
        self._cr = len(data["rounds"])
        print(f'Estamos na rodada {self._cr}!')
        return self._cr
    
    def load(self, n: int | None = None) -> list["Round"]:

        rounds: list[Round] = []
        if n is None:
            n = self.current_round
        else:
            n = self.current_round - n + 1

        while n <= self.current_round:
            print(f'Round {n}/{self.current_round}', end='\r')
            round = Round(n, self)
            rounds.append(round)
            n += 1
        print()
        return rounds
    
    def input(self) -> list["Round"]:
        print('Todas as partidas serão carregadas por padrão')
        n = input('Quantas rodadas você deseja carregar? ')
        n = -1 if not n else int(n)
        return self.load(n)

    
class Round(Base):

    def __init__(self, n: int, season: Season):
        self.round = n
        self.season = season
        self.url = Urls.season(self.season.tournament.id, self.season.id, self.round)

    def _teams(self, match: dict[str, dict[str, str]]) -> tuple["Team", "Team"]:

        teams: list[Team] = []
        for team in ['home', 'away']:

            team_id = match[f"{team}Team"]["id"]
            team_name = match[f"{team}Team"]["name"]
            all = match[f"{team}Score"]["normaltime"]
            t1 = match[f"{team}Score"]["period1"]
            t2 = match[f"{team}Score"]["period2"]

            team = Team(team_id, team_name, Score(all, t1, t2))
            teams.append(team)

        return teams

    def load(self) -> list["Match"]:

        print(f'Carregando rodada {self.round}...')
        data = requests.get(self.url).json()
        data = data["events"]

        round: list[Match] = []
        for match in data:
            
            if not match["homeScore"]:
                continue

            home, away = self._teams(match)
            id = match["id"]
            m = Match(id, self, home, away)
            round.append(m)

        return round
    
    def __iter__(self):
        self._data = self.load()
        self._index = 0
        return self
    
    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration
        match = self._data[self._index]
        self._index += 1
        return match

class Match:

    def __init__(self, id: int, round: Round, home: "Team", away: "Team"):
        self.id = id
        self.round = round
        self.home = home
        self.away = away

    def json(self) -> dict:

        url = Urls.statistics(self.id)
        data = requests.get(url).json()
        if "statistics" not in data:
            return None
        data = data["statistics"]

        table: dict[str, list] = {
            'Team': [],
            'Home': [],
            'Away': [],
            'Period': []
        }

        columns = set()

        for i, stats in enumerate(data):

            table['Team'].append(self.home.name)
            table["Home"].append(self.home.name)
            table["Away"].append(self.away.name)
            table["Period"].append(stats["period"])

            table['Team'].append(self.away.name)
            table["Home"].append(self.home.name)
            table["Away"].append(self.away.name)
            table["Period"].append(stats["period"])

            groups = stats["groups"]
            h = set()
            for group in groups:

                stats = group["statisticsItems"]
                for stat in stats:

                    column = stat["name"]
                    home = stat["home"]
                    away = stat["away"]

                    if column in h:
                        continue
                    h.add(column)

                    columns.add(column)
                    
                    default = [] + [None]*i*2
                    table[column] = table.get(column, default) + [home, away]

            for column in columns:
                if column not in h:
                    table[column] += [None, None]

        return table

    def csv(self) -> list[list]:

        data = self.json()
        columns = data['columns']
        result = [columns]
        for period in data:
            home_stats = []
            away_stats = []
            for c in columns:
                home_stats.append(data[period]['home'].get(c, None))
                away_stats.append(data[period]['away'].get(c, None))
            result.append(home_stats)
            result.append(away_stats)
                    
        return result
    
    def load_players_stats(self): ...

    def save(self) -> None:

        file_path = f'{self.round.season.name.replace('/', '-')}.csv'
        print(f'Rodada {self.round.round}: Salvando em {file_path}...')

        new_data = self.json()
        if new_data is None:
            print(f'Erro ao buscar dados de {self.home.name} x {self.away.name}')
            return

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = list(csv.reader(f, ))

            current_data = {column: [s[i] for s in current_data[1:]] for i, column in enumerate(current_data[0])}

            length = -1
            for column in current_data:
                new_data[column] = current_data[column] + new_data.get(column, [])
                length = max(length, len(new_data[column]))

            for column in new_data:
                if len(new_data[column]) < length:
                    new_data[column] = [None]*(length-len(new_data[column])) + new_data[column]

        df = pd.DataFrame(new_data)
        df.to_csv(file_path, index=False)

class Team:
     
    def __init__(self, id: int, name: str, score: Score):
        self.id = id
        self.name = name
        self.score = score

NextData = Union[Category, Tournament, Season, Match, Tournament]