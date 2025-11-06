import requests
import os
from datetime import datetime, timedelta

API_KEY = os.getenv("API_FOOTBALL_KEY")
API_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

# Топ-10 лиг + сборные + еврокубки
LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "RPL": 235,
    "Eredivisie": 88,
    "Champions League": 2,
    "Europa League": 3,
    "Conference League": 848,
    "International": 1
}

def get_upcoming_matches(hours_ahead=24):
    """Возвращает список ближайших матчей по всем топ-лигам"""
    now = datetime.utcnow()
    end = now + timedelta(hours=hours_ahead)

    matches = []

    for league_name, league_id in LEAGUES.items():
        url = f"{API_URL}/fixtures"
        params = {
            "league": league_id,
            "season": datetime.now().year,
            "from": now.strftime("%Y-%m-%d"),
            "to": end.strftime("%Y-%m-%d")
        }

        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json().get("response", [])
        except Exception as e:
            print(f"[Ошибка API] {league_name}: {e}")
            continue

        for match in data:
            fixture = match.get("fixture", {})
            teams = match.get("teams", {})
            matches.append({
                "id": fixture.get("id"),
                "league": league_name,
                "date": fixture.get("date"),
                "home": teams.get("home", {}).get("name"),
                "away": teams.get("away", {}).get("name")
            })

    return matches


def get_match_data(fixture_id):
    """Возвращает расширенные данные по конкретному матчу"""
    url = f"{API_URL}/fixtures?id={fixture_id}"

    try:
        fixture_resp = requests.get(url, headers=HEADERS, timeout=15).json()
        data = fixture_resp.get("response", [])[0]

        stats_url = f"{API_URL}/fixtures/statistics?fixture={fixture_id}"
        stats_resp = requests.get(stats_url, headers=HEADERS, timeout=15).json()
        stats = stats_resp.get("response", [])

        lineup_url = f"{API_URL}/fixtures/lineups?fixture={fixture_id}"
        lineup_resp = requests.get(lineup_url, headers=HEADERS, timeout=15).json()
        lineup = lineup_resp.get("response", [])

        match_data = {
            "fixture": data.get("fixture", {}),
            "league": data.get("league", {}),
            "teams": data.get("teams", {}),
            "goals": data.get("goals", {}),
            "statistics": stats,
            "lineups": lineup
        }

        return match_data

    except Exception as e:
        print(f"[Ошибка при получении данных по матчу {fixture_id}]: {e}")
        return None
