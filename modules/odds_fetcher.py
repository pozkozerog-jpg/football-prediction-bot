"""
Попытка взять линии/коэффициенты:
- сначала пробуем API-Football /odds (если доступно),
- иначе пробуем external odds API если задан ODDS_API_KEY (пример: the-odds-api).
"""
import os
from modules.data_fetcher import _get
import requests

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
LEGAL_BOOKMAKERS = [
    "Fonbet", "Winline", "BetCity", "Pari", "Melbet", "Liga Stavok",
    "Marathon", "Tennisi", "Betboom", "Leon", "Baltbet", "Zenit",
    "Olimp", "Bettery", "Sportbet", "BET-M"
]

def get_odds_from_api_football(fixture_id):
    try:
        data = _get("/odds", params={"fixture": fixture_id})
    except Exception:
        return {}
    res = {}
    for book in data.get("response", []):
        name = book.get("bookmaker", {}).get("name")
        markets = book.get("bets", []) or []
        obj = {"1": None, "X": None, "2": None, "O2.5": None, "BTTS": None}
        for m in markets:
            label = m.get("label", "")
            for val in m.get("values", []):
                v = val.get("value")
                odd = val.get("odd")
                if "Home" in v or v == "1":
                    obj["1"] = odd
                if "Draw" in v or v == "X":
                    obj["X"] = odd
                if "Away" in v or v == "2":
                    obj["2"] = odd
                if "Over 2.5" in v:
                    obj["O2.5"] = odd
                if "Yes" in v and ("Both" in label or "Both Teams To Score" in label):
                    obj["BTTS"] = odd
        if name:
            res[name] = obj
    # ensure legal bookmakers keys exist as placeholders
    for lb in LEGAL_BOOKMAKERS:
        res.setdefault(lb, {"1": None, "X": None, "2": None, "O2.5": None, "BTTS": None})
    return res

def get_odds_from_external():
    # Example: the-odds-api
    try:
        if not ODDS_API_KEY:
            return {}
        url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?regions=eu&markets=h2h,totals&oddsFormat=decimal&apiKey={ODDS_API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        # map some data (simplified)
        out = {}
        for item in data[:10]:
            try:
                bk = item["bookmakers"][0]["title"]
                market = item["bookmakers"][0]["markets"][0]
                # store first outcomes
                out[bk] = {"raw": market}
            except Exception:
                continue
        return out
    except Exception:
        return {}

def fetch_odds(fixture_id):
    """Главная функция: возвращает объединённую таблицу коэффициентов."""
    res = get_odds_from_api_football(fixture_id)
    if not res or all(v["1"] is None and v["X"] is None and v["2"] is None for v in res.values()):
        # fallback to external
        res = get_odds_from_external()
    return res
