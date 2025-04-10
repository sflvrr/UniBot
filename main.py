import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import time
import threading
from parse_uni_functions import *
import random


BOT_TOKEN = '7973736093:AAEaVvXexnejqMD-mcgDmakkAikghmbsQ8Q'
bot = telebot.TeleBot(BOT_TOKEN)

universities = {  # Список университетов
    "HSE": ("Высшая школа экономики", parse_hse),
    "MIPT": ("МФТИ", parse_mipt),
    "MIREA": ("МИРЭА", parse_mirea),
    "MEPHI": ("МИФИ", parse_mephi),
    "MISIS": ("МИСиС", parse_misis),
    "MAI": ("МАИ", parse_mai)}


error_messages = ["К такому меня жизнь не готовила...", 'Извини, но это уже слишком...',
                  'Ошибка! Мой процессор перегрелся! Спроси что-нибудь другое.', 'Я что-то не совсем тебя понял...']
user_subscriptions = {}  # user_id: set(университетов)
last_titles = {code: [] for code in universities}
proposal = False
admin = '1700868755'


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


def send_main_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Университеты"))
    markup.add(KeyboardButton("Образовательные центры"))
    markup.add(KeyboardButton("Олимпиады"))
    markup.add(KeyboardButton("Предложить функцию"))
    bot.send_message(chat_id, "Вот меню 👇", reply_markup=markup)


# Команда /start
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    send_main_menu(message.chat.id)


@bot.message_handler(content_types=['text'])
def func(message):
    global proposal
    if message.text == "Университеты":
        send_unis(message)

    elif message.text == "Образовательные центры":
        bot.send_message(message.chat.id, "Эта функция ещё находится в разработке, но кнопка уже есть! :) \n"
                                          "Мы трудимся изо всех сил, чтобы она быстрее стала доступна!")

    elif message.text == "Олимпиады":
        bot.send_message(message.chat.id, "Эта функция ещё находится в разработке, но кнопка уже есть! :) \n"
                                          "Мы трудимся изо всех сил, чтобы она быстрее стала доступна!")

    elif message.text == "Предложить функцию":
        propose_function(message)

    elif message.text == "Вернуться в главное меню":
        send_main_menu(message.chat.id)

    else:
        if proposal:
            send_admin(message)
            proposal = False
        else:
            bot.send_message(message.chat.id, text=random.choice(error_messages))


def send_unis(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    back = KeyboardButton("Вернуться в главное меню")
    markup.add(back)
    bot.send_message(message.chat.id, text="Из списка ниже выбери те университеты, от которых хочешь получать новости.", reply_markup=markup)
    user_id = message.from_user.id
    user_subscriptions.setdefault(user_id, set())
    bot.send_message(user_id, "Выбери ВУЗы для подписки:", reply_markup=get_keyboard(user_id))


def propose_function(message):
    global proposal
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    back = KeyboardButton("Вернуться в главное меню")
    markup.add(back)
    bot.send_message(message.chat.id, text="Я открыт к предложениям! Напиши своё сообщение ниже.", reply_markup=markup)
    proposal = True


def send_admin(message):
    print('forward_adm')
    print(message.chat.id)
    bot.send_message(admin, '{}'.format(message.text) + '\n\nuser id: ' + str(message.chat.id))
    bot.send_message(message.chat.id, "Спасибо! Твоё предложение отправлено разработчикам"
                                      " и они уже думают над реализацией...")
    send_main_menu(message.chat.id)


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
                if title not in last_titles[code]:  # Проверка, что новость новая
                    last_titles[code].append(title)
                    if len(last_titles[code]) > 10:  # Держим в памяти только последние 10 новостей ВУЗа
                        last_titles[code].pop(0)
                    message = f"🆕 Новость из {name}:\n<b>{title}</b>\n🗓🔗 {link}"  # Отправка сообщения пользователю с заголовком и ссылкой
                    for user_id, subs in user_subscriptions.items():
                        if code in subs:
                            try:
                                bot.send_message(user_id, message, parse_mode="HTML")
                            except Exception as e:
                                print(f"Ошибка отправки {user_id}: {e}")
            except Exception as e:
                print(f"[{code}] Ошибка парсера: {e}")
        time.sleep(900)  # каждые 15 минут
        print('ok')


# Запуск фоновой задачи
threading.Thread(target=check_news_loop, daemon=True).start()

# Запуск бота
print("Бот запущен.")
bot.infinity_polling()
