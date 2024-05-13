import telebot
from telebot import types

TOKEN = '6569446120:AAE85EgrKRanb3jvcfu_VFZ3k26_lHTAlPU'  # Замените 'YOUR_TOKEN' на ваш токен от BotFather

bot = telebot.TeleBot(TOKEN)

ads = []
moderators = []
password = "123"  # Задайте пароль для добавления модератора

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    add_moderator_button = types.KeyboardButton('/add_moderator')
    markup.add(add_moderator_button)
    bot.send_message(message.chat.id, "Привет! Этот бот позволяет добавлять объявления. Используйте /add для добавления, /delete для удаления и /search для поиска.", reply_markup=markup)

@bot.message_handler(commands=['add_moderator'])
def add_moderator_command(message):
    bot.send_message(message.chat.id, "Введите пароль для добавления в качестве модератора:")
    bot.register_next_step_handler(message, add_moderator)

def is_moderator(user_id):
    return user_id in moderators

def add_moderator(message):
    if message.text == password:
        user_id = message.from_user.id
        if user_id not in moderators:
            moderators.append(user_id)
            bot.send_message(message.chat.id, "Вы добавлены в список модераторов!")
        else:
            bot.send_message(message.chat.id, "Вы уже являетесь модератором.")
    else:
        bot.send_message(message.chat.id, "Неверный пароль.")

@bot.message_handler(commands=['add'])
def add_message(message):
    bot.send_message(message.chat.id, "Введите название компании:")
    bot.register_next_step_handler(message, add_company)

def add_company(message):
    company_name = message.text
    bot.send_message(message.chat.id, "Введите должность:")
    bot.register_next_step_handler(message, add_position, company_name)

def add_position(message, company_name):
    position = message.text
    bot.send_message(message.chat.id, "Введите зарплату:")
    bot.register_next_step_handler(message, save_ad, company_name, position)

def save_ad(message, company_name, position):
    salary = message.text
    ad_text = f"Компания: {company_name}\nДолжность: {position}\nЗарплата: {salary}"
    ads.append({'text': ad_text, 'user_id': message.from_user.id})
    bot.send_message(message.chat.id, "Объявление успешно добавлено!")

@bot.message_handler(commands=['delete'])
def delete_message(message):
    if is_moderator(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(row_width=1)
        for ad in ads:
            markup.add(types.KeyboardButton(ad['text']))
        bot.send_message(message.chat.id, "Выберите объявление для удаления:", reply_markup=markup)
        bot.register_next_step_handler(message, delete_ad)
    else:
        bot.send_message(message.chat.id, "У вас нет прав на удаление объявлений.")

@bot.message_handler(commands=['search'])
def search_message(message):
    bot.send_message(message.chat.id, "Введите тег для поиска:")
    bot.register_next_step_handler(message, search_ad)

def delete_ad(message):
    ad_text = message.text
    user_id = message.from_user.id
    for ad in ads:
        if ad['text'] == ad_text:
            if ad['user_id'] == user_id or is_moderator(user_id):
                ads.remove(ad)
                bot.send_message(message.chat.id, "Объявление успешно удалено!")
                return
            else:
                bot.send_message(message.chat.id, "У вас нет прав на удаление данного объявления.")
                return
    bot.send_message(message.chat.id, "Такого объявления не существует.")

def search_ad(message):
    tag = message.text
    found_ads = [ad['text'] for ad in ads if tag.lower() in ad['text'].lower()]
    if found_ads:
        bot.send_message(message.chat.id, "Найденные объявления по тегу '{}':\n{}".format(tag, '\n'.join(found_ads)))
    else:
        bot.send_message(message.chat.id, "По вашему запросу ничего не найдено.")

bot.polling()