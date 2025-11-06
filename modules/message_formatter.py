import requests
import os

# Odds API для получения коэффициентов легальных БК в России
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds"

# Список легальных БК в России
LEGAL_BOOKMAKERS = [
    "Winline",
    "BetBoom",
    "Liga Stavok",
    "Fonbet",
    "Leon"
]

def get_odds_for_match(home_team, away_team):
    """Получение коэффициентов с Odds API для конкретного матча"""
    try:
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }
        response = requests.get(ODDS_URL, params=params, timeout=15)
        data = response.json()

        match_odds = []
        for event in data:
            if home_team.lower() in event["home_team"].lower() or away_team.lower() in event["away_team"].lower():
                for bookmaker in event["bookmakers"]:
                    name = bookmaker["title"]
                    if any(legal.lower() in name.lower() for legal in LEGAL_BOOKMAKERS):
                        outcomes = bookmaker["markets"][0]["outcomes"]
                        odds = {
                            "bookmaker": name,
                            "home": outcomes[0]["price"],
                            "draw": outcomes[1]["price"] if len(outcomes) > 2 else "-",
                            "away": outcomes[-1]["price"]
                        }
                        match_odds.append(odds)
        return match_odds[:3]  # возвращаем максимум 3 лучших БК
    except Exception as e:
        print(f"[Ошибка получения коэффициентов]: {e}")
        return []


def format_match_analysis(match_data, predictions):
    """Формирует красивое сообщение о матче"""
    fixture = match_data.get("fixture", {})
    teams = predictions.get("teams", "")
    odds_list = get_odds_for_match(
        match_data["teams"]["home"]["name"],
        match_data["teams"]["away"]["name"]
    )

    date = fixture.get("date", "Неизвестно")[:16].replace("T", " ")
    analysis = f"""
🏆 <b>{teams}</b>
📅 <b>Дата:</b> {date}

📊 <b>Статистический прогноз:</b>
────────────────────────
⚽ {predictions["total_goals"]}
📐 {predictions["corners"]}
🟨 {predictions["cards"]}
🎯 {predictions["both_to_score"]}
🏅 {predictions["expected_result"]}
🏠 {predictions["home_total"]}
🏃 {predictions["away_total"]}
👟 <b>Вероятный автор гола:</b> {predictions["probable_scorer"]}
📈 <b>Уверенность:</b> {predictions["confidence"]}%

────────────────────────
💰 <b>Коэффициенты российских БК:</b>
"""

    if odds_list:
        for o in odds_list:
            analysis += (
                f"\n<b>{o['bookmaker']}:</b>\n"
                f"🏠 {o['home']} | 🤝 {o['draw']} | 🏃 {o['away']}"
            )
    else:
        analysis += "\nНет доступных коэффициентов для этого матча."

    analysis += "\n\n🕒 Время по МСК"

    return analysis
