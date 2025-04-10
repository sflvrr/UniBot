import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading
from parse_uni_functions import *


BOT_TOKEN = '7791271285:AAFc44MUP0H8Si0b9GBf4NBSK-Cc8bPHwzk'
bot = telebot.TeleBot(BOT_TOKEN)

universities = {
    "HSE": ("Высшая школа экономики", parse_hse),
    "MIPT": ("МФТИ", parse_mipt),
    "MIREA": ("МИРЭА", parse_mirea),
    "MEPHI": ("МИФИ", parse_mephi),
    "MISIS": ("МИСиС", parse_misis),
    "MAI": ("МАИ", parse_mai)}


user_subscriptions = {}  # user_id: set(университетов)
last_titles = {code: None for code in universities}


# Меню кнопок
def get_keyboard(user_id):
    markup = InlineKeyboardMarkup()
    subs = user_subscriptions.get(user_id, set())
    for code, (name, _) in universities.items():
        if code in subs:
            status = "✅"
            subs.add(code)
            print(universities.items())
        else:
            status = "❌"
            subs.discard(code)
        markup.add(InlineKeyboardButton(f"{status} {name}", callback_data=code))
        print(subs)
    return markup


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_subscriptions.setdefault(user_id, set())
    bot.send_message(user_id, "Выберите ВУЗы для подписки:", reply_markup=get_keyboard(user_id))


# Обработка кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    code = call.data
    subs = user_subscriptions.setdefault(user_id, set())
    if code in subs:
        subs.remove(code)
    else:
        subs.add(code)
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=get_keyboard(user_id))


# Фоновая проверка новостей
def check_news_loop():
    while True:
        for code, (name, parser) in universities.items():
            try:
                title, link = parser()
                last_titles = {code: None for code in universities} # Проверка, что новость новая
                if last_titles[code] != title:
                    last_titles[code] = title
                    message = f"🆕 Новость из {name}:\n<b>{title}</b>\n🗓🔗 {link}" # Отправка сообщения пользователю с заголовком и ссылкой
                    for user_id, subs in user_subscriptions.items():
                        if code in subs:
                            try:
                                bot.send_message(user_id, message, parse_mode="HTML")
                            except Exception as e:
                                print(f"Ошибка отправки {user_id}: {e}")
            except Exception as e:
                print(f"[{code}] Ошибка парсера: {e}")
        time.sleep(10)  # каждые 30 минут
        print('ok')


# Запуск фоновой задачи
threading.Thread(target=check_news_loop, daemon=True).start()

# Запуск бота
print("Бот запущен.")
bot.infinity_polling()
