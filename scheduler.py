"""
Запускается по cron (Actions), делает один проход:
 - получает ближайшие матчи
 - для матчей за 50..70 минут до кик-офф проверяет наличие составов
 - если составы есть -> делает анализ и рассылает в канал и всем подписанным пользователям
"""
import os
from modules.data_fetcher import get_upcoming_matches, get_lineups, get_team_stats
from modules.odds_fetcher import fetch_odds as fetch_odds_global
from modules.predictor import generate
from modules.message_formatter import format_match_analysis
import json
from datetime import datetime, timezone, timedelta
import pytz
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
if not TOKEN:
    raise SystemExit("TELEGRAM_TOKEN not set")
bot = telebot.TeleBot(TOKEN)
USERS_FILE = "users.json"
UTC = pytz.UTC

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def run_once():
    now = datetime.utcnow().replace(tzinfo=UTC)
    matches = get_upcoming_matches(next_n=200, window_hours=72)
    for m in matches:
        minutes = (m["kick_off"] - now).total_seconds()/60
        if 50 <= minutes <= 70:
            lineup = get_lineups(m["id"])
            if not lineup.get("published"):
                continue
            home_stats = get_team_stats(m["home_id"])
            away_stats = get_team_stats(m["away_id"])
            odds = fetch_odds_global(m["id"])
            analysis = generate(m, home_stats, away_stats, odds)
            text = format_match_analysis(m, home_stats, away_stats, odds, analysis)
            # send to channel
            try:
                if CHANNEL_ID:
                    bot.send_message(CHANNEL_ID, text, parse_mode="HTML")
            except Exception:
                pass
            # send to users
            users = load_users()
            for u in users:
                try:
                    bot.send_message(u, text, parse_mode="HTML")
                except Exception:
                    continue

if __name__ == "__main__":
    run_once()
