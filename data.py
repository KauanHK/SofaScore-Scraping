import requests
from utils import Urls
from typing import Dict


def load_main_tournaments():

    url = Urls.main_tournaments()
    response_data = requests.get(url).json()
    response_data = response_data["uniqueTournaments"]
    data = {}
    for t in response_data:
        data[t["name"]] = t["id"]
    return data

def load_categories()  -> Dict[str, int]:

    url = Urls.categories()
    data = requests.get(url).json()
    data = data["categories"]
    return {c["name"]: c["id"] for c in data}

def load_category(id: int) -> Dict[str, Dict]:

    url = Urls.category(id)
    data = requests.get(url).json()
    data = data["groups"][0]["uniqueTournaments"]
    return {t["name"]: t["id"] for t in data}

def load_tournament(id: int) -> Dict[str, int]:
        
    url = Urls.tournament(id)
    data = requests.get(url).json()
    data = data["seasons"]
    return {s["name"]: s["id"] for s in data}

def load_round(tournament_id: int, season_id: int, round: int):

    url = Urls.season(tournament_id, season_id, round)
    data = requests.get(url).json()
    data = data["events"]

    filter_data = {}
    for match in data:
        
        home_team = match["homeTeam"]["name"]
        away_team = match["awayTeam"]["name"]
        match_name = f'{home_team} x {away_team}'

        status = match["status"]["type"]
        if status == 'notstarted':
            if not len(filter_data):
                return None
            continue
        elif status != 'finished':
            continue
        
        
        home_data = {
            "name": home_team,
            "id": match["homeTeam"]["id"],
            "period1": match["homeScore"]["period1"],
            "period2": match["homeScore"]["period2"],
            "normaltime": match["homeScore"]["normaltime"]
        }

        away_data = {
            "name": away_team,
            "id": match["awayTeam"]["id"],
            "period1": match["awayScore"]["period1"],
            "period2": match["awayScore"]["period2"],
            "normaltime": match["awayScore"]["normaltime"]
        }

        filter_data[match_name] = {
            "home": home_data,
            "away": away_data,
            "id": match["id"]
        }

    return filter_data

def load_stats(event_id: int):

    url = Urls.statistics(event_id)
    response_data = requests.get(url).json()
    response_data = response_data["statistics"]
    
    data = {}
    for dict_ in response_data:
        period = dict_["period"]
        groups = dict_["groups"]
        data[period] = {group.pop("groupName"): group["statisticsItems"] for group in groups}
        for group in data[period]:
            stats = {}
            for stat in data[period][group]:
                stats[stat["name"]] = {
                    "home": stat["homeValue"],
                    "away": stat["awayValue"]
                }
            data[period][group] = stats

    return data

def get_category(tournament_id: int):

    url = Urls.tournament(tournament_id)
    data = requests.get(url).json()
    season = data["seasons"][0]
    id = season["id"]
    url = Urls.season(tournament_id, id, 1)
    data = requests.get(url).json()
    id = data["events"][0]["tournament"]["category"]["id"]
    return load_category(id)

def get_current_round(tournament_id: int, season_id: int):
    url = Urls.rounds(tournament_id, season_id)
    data = requests.get(url).json()
    return len(data["rounds"])

_data = {
    'MainTournaments': load_main_tournaments,
    'Categories': load_categories,
    'Category': load_category,
    'Tournament': load_tournament,
    'Season': load_round
}