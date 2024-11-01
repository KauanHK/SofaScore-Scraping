from typing import Union, Literal, List, Dict


class Base:

    def __init__(self, id: int, next: NextData | None = None): ...
    def json(self) -> Dict: ...
    def load(self) -> List["NextData"]: ...
    def save(self) -> None: ...

class MainTournaments(Base):

    def __init__(self): ...

class Categories(Base):

    def __init__(self): ...
    
class Category(Base):
    
    def __init__(self, id: int): ...

class Tournament(Base):

    def __init__(self, id: int, category: Category): ...

class Season(Base):

    tournament: Tournament

    def __init__(self, id: int, tournament: Tournament): ...
    def get_rounds(self, rounds: int) -> List[List["Match"]]: ...
    def load_round(self, round: int) -> List["Match"]: ...
    
class Round(Base):

    season: Season

    def __init__(self, season: Season): ...

class Match(Base):

    def __init__(self): ...

class Team(Base):
     
    def __init__(self, data: dict[str, str | int]): ...


NextData = Union["Category", "Tournament", "Season", "Match", "Tournament"]