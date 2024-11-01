import requests
from data import _data, get_current_round
from utils import Urls
from typing import Union, Literal, List, Dict


class Base:

    def __init__(self, next: Union["NextData", None] = None, id: int | None = None):
        self.id = id
        self._next: NextData = next

    def json(self) -> Dict:
        args = []
        if self.id is not None:
            args.append(self.id)
        return _data[self.__class__.__name__](*args)
    
    def load(self, n: int = -1) -> List["NextData"]:
        
        dict_next = {
            MainTournaments: lambda id: self._next(id, Category(id)),
            Categories: lambda id: self._next(id),
        }
        default = lambda id: self._next(id, self)
        next = dict_next.get(self._next, default)

        data_json = self.json()
        list_ids = list(data_json.values())
        data = []
        i = 0
        if n < 1:
            n = len(list_ids)
        while i < n and i < len(list_ids):
            data.append(next(list_ids[i]))
            i += 1
        return data
    
    def save(self) -> None: ...

class MainTournaments(Base):

    def __init__(self):
        super().__init__(Tournament)

class Categories(Base):

    def __init__(self): ...
    
class Category(Base):
    
    def __init__(self, id: int): ...

class Tournament(Base):

    def __init__(self, id: int, category: Category):
        super().__init__(Season, id)

class Season(Base):

    def __init__(self, id: int, tournament: Tournament):
        super().__init__(Round, id)
        self.tournament = tournament

    def load(self, n: int = -1) -> List["Round"]:

        current_round = get_current_round(self.tournament.id, self.id)
        rounds: List[Round] = []
        for r in range(1, current_round+1):
            round = Round(r, self)
            rounds.append(round)
        return rounds

    
class Round(Base):

    def __init__(self, n: int, season: Season):
        super().__init__(Match)
        self.round = n
        self.season = season

    def load(self) -> "Round":
        url = Urls.season(self.season.tournament.id, self.season.id, self.round)
        data = requests.get(url).json()
        data = data["events"]

        round: list[Team] = []
        for match in data:
            
            home_id = match["homeTeam"]["id"]
            home_name = match["homeTeam"]["name"]
            home = Team(home_id, home_name)

            away_id = match["awayTeam"]["id"]
            away_name = match["awayTeam"]["name"]
            away = Team(away_id, away_name)

            id = match["id"]
            match = Match(id, home, away)
            round.append(match)

        return round

class Match:

    def __init__(self, id: int, home: "Team", away: "Team"):
        self.id = id
        self.home = home
        self.away = away

class Team:
     
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


NextData = Union["Category", "Tournament", "Season", "Match", "Tournament"]