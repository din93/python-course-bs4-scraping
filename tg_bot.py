import telebot
from telebot import apihelper, types
import requests, time, os, datetime, json, random
from bs4 import BeautifulSoup
from utils import scrape_afisha_report

admin_name = ''
bot_token = ""
cache_path = 'cache_reports.json'

http_address = 'http://81.210.32.100:8080'
apihelper.proxy = {
    'http': http_address,
    'https': http_address
}

bot = telebot.TeleBot(bot_token)

stickers_hello = dict(
    hereisjohny_hi = 'CAACAgIAAxkBAANiXixhCerxeJfw1yVEncQVZDfXB_kAAh0GAAJjK-IJOM2IMvQWyocYBA',
    monkey_hi = 'CAACAgIAAxkBAANmXixiUb_NCEXhAw5nfM6GJLhODtcAAqUAAzDUnRE4G8Njl3YdLRgE',
    dog_hi = 'CAACAgIAAxkBAANuXixjUJpYkjOjM7vuEaGNqKVccSkAAuQBAALKAwYLAAFdfBYpsR0xGAQ',
    theboss_hi = 'CAACAgIAAxkBAAONXixq3MaaqG3fJZ09fxEV7pexpN8AAqUJAAIItxkCO2IWwlRakOIYBA',
    seagull_hi = 'CAACAgIAAxkBAAOPXixrIYklKv3BQGs7EQUZm3ByIwEAAmcAA5afjA7JBmfMQdsNTxgE',
    mrbean_hi = 'CAACAgUAAxkBAAORXixrup3awxQKp1OM-McZO_xxr4MAAoIDAALpCsgDjFkDselbxLcYBA',
    toyduck_hi = 'CAACAgIAAxkBAAOTXixsDPdRnjW5HpLJYn6iQ_KTyj4AAgEBAAJWnb0KIr6fDrjC5jQYBA',
    eggbeacon_hi = 'CAACAgIAAxkBAAOVXixsOMronD98hJl1GBa8n_BiMp4AAhwAA_cCyA9wHHItbZMYeBgE',
    wolfie_hi = 'CAACAgIAAxkBAAOXXixsl40CvuMSWy6P-flwsUBFAuAAAiUAA-SgzgddsYEz6G-tdBgE',
    tiecat_hi = 'CAACAgIAAxkBAAObXixtCHy6dtpOHmJMoIHrFmvND2QAAg4AA5afjA4PgOejgpWn1xgE',
)
stickers_justforfun = dict(
    duck_computer = 'CAACAgIAAxkBAANfXixeTZOVghaTeLpBdT41ROGREIUAAkYAA1KJkSP4_uXkCtUKHRgE',
    duck_thumb_up = 'CAACAgIAAxkBAANgXixe3_aJbju4ehsi0mED-Gi31hQAAkEAA1KJkSPV1ldK02RxVhgE',
    yepekayee = 'CAACAgIAAxkBAANkXixhqxjbEtOCa-rOxj8xmaaOQF8AAsYCAAJjK-IJzec08mzFJQ4YBA',
    baboon_heart = 'CAACAgIAAxkBAANoXixid7nwjH0dLYxLV54zPN9cXTAAApsAAzDUnREDE1nXR8X0jhgE',
    monkey_crazy = 'CAACAgIAAxkBAANqXixisVRlSohB-qrMvQozBbPBImIAAqgAAzDUnRG1yvu41nOKaRgE',
    bewarethedog = 'CAACAgIAAxkBAANsXixjMNr5HyvzHcFNklLrTaerayoAAvMBAALKAwYLGs1jmaU905IYBA',
    toy_duck_vietnam = 'CAACAgIAAxkBAANwXixjx9uZ4ywhisSFcYCTNxs9ts0AAvQAA1advQoRWLD12f1VSRgE',
    freeman_heart = 'CAACAgQAAxkBAANyXixkAmZbDpqezKBvxu_aoQIUoPcAAk8AA4Nq0BCBCEYaEB0fERgE',
    freeman_popcorn = 'CAACAgQAAxkBAAN0XixkKLAYs3O5xF-C2I0JOIVF79EAAkYAA4Nq0BBn0J1SRIJsCxgE',
    banana_screamer = 'CAACAgIAAxkBAAOZXixs5mamFHzpS3xp-QiEHhCZia8AAvECAAK1cdoGcSIxNd9nDrAYBA',
    tiecat_ok = 'CAACAgIAAxkBAAOdXixtLP24XmVIcvoPRRp2m0R1_ukAAhwAA5afjA6Z1Gm-YvJ55RgE',
    duck_phonechat = 'CAACAgIAAxkBAAOfXixtV3Avra3WMw3H21MWUY148xkAAkIAA1KJkSODyFRjM7vkWRgE',
)

admin_markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
getcachebtn = types.KeyboardButton('/getcache')
terminatebtn = types.KeyboardButton('/terminate')
admin_markup.add(getcachebtn, terminatebtn)

def is_cache_actual():
    return datetime.datetime.fromtimestamp(os.path.getmtime(cache_path)).date() == datetime.date.today()

def get_cache_reports():
    if os.path.isfile(cache_path) and is_cache_actual():
        with open(cache_path, 'r', encoding='utf-8') as tfile:
            reports = json.loads(tfile.read())
    else:
        reports = dict()
    os.remove(cache_path) if not is_cache_actual() else None
    return reports

def save_cache_reports(reports):
    with open(cache_path, 'w', encoding='utf-8') as tfile:
        tfile.write(json.dumps(reports, ensure_ascii=False, indent=2))

def get_afisha_message_text(afisha_report):
    return '\n'.join([
        f'"{movie["title"]}" {movie["min_age"]}, {movie["genre"]}, {movie["year"]}, {movie["country"]}, {movie["duration"]} \nдни показа: {", ".join(movie["avalable_dates"])} \n{movie["href"]}\n'
        for movie in afisha_report
    ])

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Привет! Я даю краткую информацию о тех фильмах, которые сейчас показывают в кинотеатрах вашего города")

@bot.message_handler(commands=['help'])
def send_help(message):
	bot.reply_to(message, "Введите команду /afisha с названием города на латинице (по умолчанию это Москва)")

@bot.message_handler(commands=['afisha'])
def send_afisha(message):
    cache_reports = get_cache_reports()
    message_region = ' '.join(message.text.lower().split(' ')[1:])
    if message_region.strip()=='':
        message_region = 'msk'
    if message_region in cache_reports:
        afisha_list = cache_reports.get(message_region)
    else:
        try:
            afisha_list = scrape_afisha_report(message_region)
            cache_reports[message_region] = afisha_list
            save_cache_reports(cache_reports)
        except:
            bot.reply_to(message, f'Возникла ошибка с запросом для населенного пункта "{message_region}""')
            return
    
    reply_text = get_afisha_message_text(afisha_list)
    splitted_reply = telebot.util.split_string(reply_text, 2000)
    for reply_chunk in splitted_reply:
        bot.reply_to(message, reply_chunk)

@bot.message_handler(commands=['admin'], func=lambda message: message.from_user.username == admin_name)
def admin(message):
    bot.reply_to(message, "#>", reply_markup=admin_markup)

@bot.message_handler(commands=['getcache'], func=lambda message: message.from_user.username == admin_name)
def get_cache(message):
    with open(cache_path, 'rb') as tfile:
        bot.send_document(message.chat.id, tfile)

@bot.message_handler(commands=['terminate'], func=lambda message: message.from_user.username == admin_name)
def terminate(message):
    bot.reply_to(message, "Выключаюсь")
    bot.stop_polling()

@bot.message_handler(content_types=['text'])
def hi_sticker(message):
    matches_hello = False
    for hello_text in ['hello', 'hi', 'привет', 'здравствуй']:
        if hello_text in message.text.lower():
            matches_hello = True
    if matches_hello:
        bot.send_sticker(message.chat.id, random.choice(list(stickers_hello.values())))

@bot.message_handler(content_types=['sticker'])
def response_sticker(message):
    bot.send_sticker(message.chat.id, random.choice(list(stickers_justforfun.values())))

bot.polling()