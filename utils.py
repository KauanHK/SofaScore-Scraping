import json
import csv
import os
from typing import Literal, Union, Any, NamedTuple



class Urls:
    """Urls da api do SofaScore"""

    @staticmethod
    def categories():
        return "https://www.sofascore.com/api/v1/sport/football/categories"
    
    @staticmethod
    def category(id): 
        return f"https://www.sofascore.com/api/v1/category/{id}/unique-tournaments"
    
    @staticmethod
    def tournament(id):
        return f"https://api.sofascore.com/api/v1/unique-tournament/{id}/seasons"
    
    @staticmethod
    def season(tournament_id, season_id, round):
        return f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/round/{round}"
    
    @staticmethod
    def statistics(event_id):
        return f"https://www.sofascore.com/api/v1/event/{event_id}/statistics"
    
    @staticmethod
    def event(id):
        return f"https://www.sofascore.com/api/v1/event/{id}"
    
    @staticmethod
    def main_tournaments(): 
        return "https://www.sofascore.com/api/v1/config/top-unique-tournaments/BR/football"

    @staticmethod
    def rounds(tournament_id: int, season_id: int):
        return f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/team-of-the-week/rounds"

class FileNames:

    @staticmethod
    def season(category_name: str, name: str) -> str:
        name = name.replace('/', '-')
        return f"./database/{category_name}/{name}.json"

    @staticmethod
    def statistics(category_name: str, name: str) -> str:
        name = name.replace('/', '-')
        return f"./database/{category_name}/statistics/{name}.json"


File = Literal["categories", "category", "tournament", "season", "statistics"]

class Score(NamedTuple):
    all: int
    t1: int
    t2: int

class SobreCargaDeAcessos(BaseException): ...

def get_file_path(data: str, category_name: str | None = None, name: str | None = None):
    """Retorna o caminho do arquivo"""
    
    if data == 'Season':
        return os.path.join('database', category_name, f'{name}.json')
    elif data == 'Statistics':
        return os.path.join('database', category_name, 'statistics', f'{name}.json')
    
    return os.path.join('database', f'{data}.json')

def load_json(file_path: str) -> dict:
    """Carrega um json. Se o arquivo não existir, FileNotFoundError"""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_csv(file: File, *args):
    file_path = get_file_path(file, *args)
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r') as f:
        return list(csv.reader(f))[1:]

def save_json(data: Union[dict, list], file_path: str = './test.json', update: bool = False, makedirs: bool = True):

    if makedirs:
        os.makedirs(os.path.split(file_path)[0], exist_ok=True)

    if update and os.path.exists(file_path):
        current_data = load_json(file_path)
        if isinstance(data, dict):
            data.update(current_data)
        else:
            data.extend(current_data)

    with open(file_path, 'w') as f:
        try:
            json.dump(data, f, indent=4, ensure_ascii=False)
        except UnicodeEncodeError:
            json.dump(data, f, indent=4)


def save_csv(data, file: File, *args, update: bool = True, makedirs: bool = True):

    file_path = get_file_path(file, *args, makedirs)
    if update:
        current_data = load_csv(file, *args)
        if current_data is not None:
            data.extend(current_data)

    with open(file_path, 'w') as f:
        csv.writer(f).writerows(data)

