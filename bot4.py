import telebot
import os
import json

API_TOKEN = "8508595699:AAEe0VuwNFksVdAQqdaI23d0it0O_yvQMtI"
bot = telebot.TeleBot(API_TOKEN)

data = {"users": {}}
db_path = "db.json"

if os.path.exists(db_path) and os.path.getsize(db_path) != 0:
    with open(db_path, "r", encoding='utf-8') as file:
        data = json.load(file)
else:
    with open("db.json", "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if user_id not in data["users"] or data["users"].get(user_id).get("awaiting") == "name":
        data["users"][user_id] = {}
        data["users"][user_id]["awaiting"] = "name"

        bot.send_message(message.chat.id, "Введи свое имя")

        return

    data["users"][user_id]["money"] = 10000

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    slot_button = telebot.types.KeyboardButton("Игровой автомат")
    dice_button = telebot.types.KeyboardButton("Игральный кубик")

    keyboard.add(slot_button, dice_button)

    bot.send_message(message.chat.id, f"Привет, {data["users"][user_id]["name"]}", reply_markup=keyboard)

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, "Информация о боте")

@bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.chat.id

    if data["users"].get(user_id).get("awaiting") == "name":
        data["users"][user_id]["name"] = message.text
        data["users"][user_id]["awaiting"] = None
        data["users"][user_id]["money"] = 10000
        start(message)
        return

    if message.text == "Привет":
        bot.send_message(message.chat.id, "Привет")
    elif message.text == "Как дела?":
        bot.send_message(message.chat.id, "Отлично")
    elif message.text == "Игровой автомат":
        slot_game(message)
    elif message.text == "Игральный кубик":
        dice_game(message)

def dice_game(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

    btn1 = telebot.types.KeyboardButton("1", callback_data="1")
    btn2 = telebot.types.KeyboardButton("2", callback_data="2")
    btn3 = telebot.types.KeyboardButton("3", callback_data="3")
    btn4 = telebot.types.KeyboardButton("4", callback_data="4")
    btn5 = telebot.types.KeyboardButton("5", callback_data="5")
    btn6 = telebot.types.KeyboardButton("6", callback_data="6")

    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)

    bot.send_message(message.chat.id, "Угадайте число на кубике", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('1', '2', '3', '4', '5', '6'))
def diceButtonClicked(call):
    value = bot.send_dice(call.message.chat.id, emoji="").dice.value
    if str(value) == call.data:
        bot.send_message(call.message.chat.id, "Ты выиграл")
    else:
        bot.send_message(call.message.chat.id, "Попробуй еще раз")

def slot_game(message):
    value = bot.send_dice(message.chat.id, emoji="🎰").dice.value

    if value in (1, 22, 43):                                # 3 одинаковых значения
        data["users"][message.chat.id]["money"] += 3000
        bot.send_message(message.chat.id, "Победа, сумма выигрыша составила 3000. "
                                          f"Текущий баланс: {data["users"][message.chat.id]["money"]}")
    elif value in (16, 32, 48):                             # Первые два значения - 7
        bot.send_message(message.chat.id, "Победа, сумма выигрыша составила 5000. "
                                          f"Текущий баланс: {data["users"][message.chat.id]["money"]}")
        data["users"][message.chat.id]["money"] += 5000
    elif value == 64:                                       # Три 7
        bot.send_message(message.chat.id, "Jackpot, сумма выигрыша составила 10000. "
                                          f"Текущий баланс: {data["users"][message.chat.id]["money"]}")
        data["users"][message.chat.id]["money"] += 10000
    else:
        bot.send_message(message.chat.id, "Ты проиграл")

bot.polling(none_stop=True)