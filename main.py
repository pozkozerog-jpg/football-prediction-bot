import telebot
from modules.data_fetcher import get_upcoming_matches, get_match_data
from modules.predictor import generate_predictions
from modules.message_formatter import format_match_analysis
import os

# Получаем токены из переменных окружения (GitHub Secrets)
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "⚽ Привет! Я бот футбольных прогнозов!\n"
        "Используй /analyze чтобы получить свежие прогнозы."
    )

@bot.message_handler(commands=['analyze'])
def analyze(message):
    bot.send_message(message.chat.id, "🔎 Собираю данные, подожди немного...")
    matches = get_upcoming_matches()

    for match in matches:
        try:
            data = get_match_data(match['id'])
            analysis = generate_predictions(data)
            text = format_match_analysis(data, analysis)
            bot.send_message(message.chat.id, text, parse_mode='HTML')

            # Отправляем также в канал, если он задан
            if CHANNEL_ID:
                bot.send_message(CHANNEL_ID, text, parse_mode='HTML')
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при анализе матча: {e}")

bot.polling(none_stop=True)
