import requests
import pandas as pd
import csv
import os
from utils import Urls, FileNames
from typing import Union, Callable, List, Dict, NamedTuple


class Score(NamedTuple):
    all: int
    t1: int
    t2: int

class SobreCargaDeAcessos(BaseException): ...

class Base:

    def __init__(self, next: Union["NextData", None] = None, id: int | None = None):
        self.id = id
        self._next: NextData = self._get_next(next)

    def _get_next(self, next: "NextData") -> Callable:
        
        dict_next = {
            MainTournaments: lambda id: next(id, Category(id)),
            Categories: lambda id: next(id),
            Category: lambda id: next(id)
        }
        default = lambda id: next(id, self)
        return dict_next.get(next, default)
    
    def json(self) -> Dict:
        raise NotImplementedError(f'{self.__class__.__name__} não implementou o método json')
    
    def load(self, n: int = -1) -> List["NextData"]:
        
        data_json = self.json()
        list_ids = list(data_json.values())
        data = []
        i = 0
        if n < 1:
            n = len(list_ids)
        while i < n and i < len(list_ids):
            print(f'{self.__class__.__name__}... {i}/{n}', end='\r')
            data.append(self._next(list_ids[i]))
            i += 1
        print(f'{self.__class__.__name__}... {i}/{n}')
        return data
    
    def input(self) -> "NextData":

        os.system('cls' if os.name == 'nt' else 'clear')
        print('Carregando...', end='\r')

        data = self.json()
        for i, option in enumerate(data, 1):
            print(f'{i} - {option}')

        n = int(input('Escolha uma opção: '))
        option = list(data)[n-1]
        return self._next(data[option])


class MainTournaments(Base):

    def __init__(self):
        super().__init__(Tournament)

    def json(self) -> Dict[str, int]:

        url = Urls.main_tournaments()
        response = requests.get(url)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise SobreCargaDeAcessos('Aparentemente você usou a api do SofaScore mais do que deveria e agora foi impedido de buscar dados :(')
        response_data = response_data["uniqueTournaments"]
        data = {}
        for t in response_data:
            data[t["name"]] = t["id"]
        return data

class Categories(Base):

    def __init__(self):
        super().__init__(Category)

    def json(self)  -> Dict[str, int]:

        url = Urls.categories()
        data = requests.get(url).json()
        data = data["categories"]
        data = {c["name"]: c["id"] for c in data}
        return dict(sorted(data.items(), key=lambda kv: kv[0]))
    
class Category(Base):
    
    def __init__(self, id: int):
        super().__init__(Tournament, id)
    
    def json(self) -> Dict[str, Dict]:

        url = Urls.category(self.id)
        data = requests.get(url).json()
        data = data["groups"][0]["uniqueTournaments"]
        return {t["name"]: t["id"] for t in data}

class Tournament(Base):

    def __init__(self, id: int, category: Category):
        super().__init__(Season, id)
        self.category = category

    def json(self) -> Dict[str, int]:
        
        url = Urls.tournament(self.id)
        data = requests.get(url).json()
        data = data["seasons"]
        return {s["name"]: s["id"] for s in data}

class Season(Base):

    def __init__(self, id: int, tournament: Tournament):
        super().__init__(Round, id)
        self.tournament = tournament
        self._cr: int | None = None

    @property
    def current_round(self) -> int:
        if self._cr is not None:
            return self._cr
        url = Urls.rounds(self.tournament.id, self.id)
        data = requests.get(url).json()
        self._cr = len(data["rounds"])
        return self._cr
    
    def load(self, n: int = -1) -> List["Round"]:

        rounds: List[Round] = []
        if n < 1:
            n = 1
        else:
            n = self.current_round - n - 1

        while n < self.current_round:
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
        super().__init__(Match)
        self.round = n
        self.season = season
        self.name: str | None = None

    def load(self) -> List["Match"]:
        url = Urls.season(self.season.tournament.id, self.season.id, self.round)
        data = requests.get(url).json()
        data = data["events"]
        self.name = data[0]["season"]["name"]

        round: list[Match] = []
        for match in data:
            
            if not match["homeScore"]:
                continue
            home_id = match["homeTeam"]["id"]
            home_name = match["homeTeam"]["name"]
            all = match["homeScore"]["normaltime"]
            t1 = match["homeScore"]["period1"]
            t2 = match["homeScore"]["period2"]
            home = Team(home_id, home_name, Score(all, t1, t2))

            away_id = match["awayTeam"]["id"]
            away_name = match["awayTeam"]["name"]
            all = match["awayScore"]["normaltime"]
            t1 = match["awayScore"]["period1"]
            t2 = match["awayScore"]["period2"]
            away = Team(away_id, away_name, Score(all, t1, t2))

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

    def json(self) -> Dict:

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

    def csv(self) -> List[List]:

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

        file_path = f'{self.round.name.replace('/', '-')}.csv'
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

NextData = Union["Category", "Tournament", "Season", "Match", "Tournament"]