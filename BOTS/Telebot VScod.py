import telebot
import random
import time, threading, schedule
import requests
import nltk           
from nltk.corpus import stopwords                       
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist
from wordcloud import WordCloud
import pymorphy2
from bs4 import BeautifulSoup
import pandas as pd
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from model import get_class
#import matplotlib.pyplot as plt
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')



bot = telebot.TeleBot("___")
last_flip = None


import os
print(os.listdir('images'))



# Папка для сохранения изображений
IMAGE_FOLDER = 'saved_images'

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)  # Получаем информацию о последней фотографии
        downloaded_file = bot.download_file(file_info.file_path)  # Загружаем файл

        # Определяем уникальное имя для нового файла
        existing_files = os.listdir(IMAGE_FOLDER)
        max_num = 0
        for filename in existing_files:
            if filename.isdigit():
                num = int(filename)
                max_num = max(max_num, num)

        next_num = max_num + 1
        file_name = os.path.join(IMAGE_FOLDER, str(next_num) + '.jpg')  # Сохраняем как JPG

        # Записываем файл в папку
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, f'Изображение сохранено как {file_name}')
        result = get_class(model_path="C:\BOTS\keras_model.h5", labels_path="C:\BOTS\labels.txt", image_path=file_name)
        bot. send_message(message.chat.id, result)
    except Exception as e:
        bot.reply_to(message, 'Произошла ошибка при сохранении изображения.')

#@bot.message_handler(func=lambda message: True)
#def handle_text_message(message):
    #bot.reply_to(message, 'Пожалуйста, отправьте изображение.')



@bot.message_handler(commands=['конспект'])
def handle_generate_summary(message):
    if len(message.text.split(' ')) < 2:
        bot.reply_to(message, "Пожалуйста, введите текст для конспекта после команды /конспект.")
        return
    
    text = message.text.split
    def summarization(text, sent_number=4):
        sentences = sent_tokenize(text, language='russian')
        stop_words = set(stopwords.words('russian'))
        words = word_tokenize(text)
        words = [word.lower() for word in words if word.isalpha() and word not in stop_words]
        
        morph = pymorphy2.MorphAnalyzer(language='russian')
        words = [morph.parse(word)[0].normal_form for word in words]
        
        freq_dist = FreqDist(words)
        sentence_scores = {}

        for i, sentence in enumerate(sentences):
            sentence_words = word_tokenize(sentence.lower())
            sentence_words = [morph.parse(word)[0].normal_form for word in sentence_words]
            sentence_score = sum([freq_dist[word] for word in sentence_words if word in freq_dist])

            sentence_scores[i] = sentence_score

        sorted_scores = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        selected_sentences = sorted(sorted_scores[:sent_number])
        summary = ' '.join([sentences[i] for i, _ in selected_sentences])
        return summary
    #bot.reply_to(message)



url = 'https://new-science.ru/category/news/page/'

def fetch_news():
    dict_news = {"news": [], "links": [], "views": [], "date": []}
    
    for i in range(1, 31):
        response = requests.get(url + str(i) + "/")
        bs = BeautifulSoup(response.text, "lxml")
        temp = bs.find_all('div', 'post-details')
        
        for post in temp:
            dict_news["news"].append(post.find('h2', 'post-title').text)  
            dict_news["links"].append(post.find('h2', 'post-title').find('a').get('href'))  
            dict_news["views"].append(post.find('span', 'meta-views meta-item').text)
            dict_news["date"].append(post.find('span', 'date meta-item tie-icon').text)

    return pd.DataFrame(dict_news, columns=["news", "links", "views", "date"])

@bot.message_handler(commands=['news'])
def get_news(message):
    df_news = fetch_news()
    
    for _, row in df_news.tail(3).iterrows():
        message_text = f"*{row['news']}*\n*Просмотры:* {row['views']}\n*Дата:* {row['date']}\n"
        bot.reply_to(message, message_text, parse_mode='Markdown')



def get_duck_image_url():
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']

@bot.message_handler(commands=['duck'])
def duck(message):
    '''По команде duck вызывает функцию get_duck_image_url и отправляет URL изображения утки'''
    image_url = get_duck_image_url()
    bot.reply_to(message, image_url)


def get_dog_image_url():
    url = 'https://random.dog/woof.json'
    res = requests.get(url)
    data = res.json()
    return data['url']

@bot.message_handler(commands=['dog'])
def dog(message):
    '''По команде dog вызывает функцию get_dog_image_url и отправляет URL изображения собаки'''
    image_url = get_dog_image_url()
    bot.reply_to(message, image_url)


def get_fox_image_url():
    url = 'https://randomfox.ca/floof/'
    res = requests.get(url)
    data = res.json()
    return data['image']

@bot.message_handler(commands=['fox'])
def fox(message):
    '''По команде fox вызывает функцию get_fox_image_url и отправляет URL изображения лисы'''
    image_url = get_fox_image_url()
    bot.reply_to(message, image_url)


def get_pokemon_information(name):
    url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    res = requests.get(url)
    data = res.json()
    return data['sprites']['front_default']

@bot.message_handler(commands=['pokemon'])
def pokemon(message):
    '''По команде pokemon вызовите функцию get_pokemon_information с именем покемона'''
    pokemon_name = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else 'pikachu'
    image_url = get_pokemon_information(pokemon_name)
    bot.reply_to(message, image_url)


@bot.message_handler(commands=['mems'])
def send_mems(message):
    img_name = random.choice(os.listdir('images'))
    with open(f'images/{img_name}', 'rb') as f:
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой Telegram бот. Напиши что-нибудь! Используй команду /help, чтобы узнать все доступные команды.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "/start - Приветствие и инструкция по использованию бота.\n"
        "/help - Список всех доступных команд и их назначение.\n"
        "/flip - Подбросить монету и узнать результат (Орёл или Решка).\n"
        "/last - Узнать последний результат подбрасывания монеты.\n"
        "/привет - Ответ от бота на приветствие.\n"
        "/пока - Ответ от бота на прощание.\n"
        "/heh число - Пишет he число раз.\n"
        "/set <seconds> — Установить таймер на указанное количество секунд; по истечении времени бот отправит сообщение.\n"
        "/unset — Остановить таймер (очистить все запланированные задачи для текущего чата).\n"
        "/duck - Рандомная картинка утки.\n"
        "/dog - Рандомная картинка собаки.\n"
        "/fox - Рандомная картинка лисы.\n"
        "/pokemon - Рандомная картинка пакемона.\n"
        "/fabrics - Узнать об экологически чистых тканях.\n"
        "/stores - Получить рекомендации по магазинам экологичной одежды.\n"
        "/конспект - Создать краткое содержание текста.\n"
        "/news - Узнать свежие новости."
    )
    bot.reply_to(message, help_text)

def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Время прошло!')

@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')

@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)

@bot.message_handler(commands=['heh'])
def send_heh(message):
    count_heh = int(message.text.split()[1]) if len(message.text.split()) > 1 else 5
    bot.reply_to(message, "he" * count_heh)

@bot.message_handler(commands=['flip'])
def flip_coin(message):
    global last_flip
    result = random.choice(['Орёл', 'Решка'])
    last_flip = result
    bot.reply_to(message, f'Монета подброшена: {result}')

@bot.message_handler(commands=['last'])
def last_flip_command(message):
    global last_flip
    if last_flip is None:
        bot.reply_to(message, 'Монета ещё не была подброшена.')
    else:
        bot.reply_to(message, f'Последний результат подбрасывания монеты: {last_flip}')



# Новые функции для экологии
@bot.message_handler(commands=['fabrics'])
def fabrics(message):
    '''Предоставляет информацию об экологически чистых тканях'''
    reply_text = (
        "Вот несколько экологически чистых тканей:\n"
        "1. Хлопок - Натуральная, дышащая ткань, но требует много воды для производства.\n"
        "2. Лен - Экологичная, устойчивая к вредителям ткань, требующая минимального ухода.\n"
        "3. Шерсть - Натуральная изоляция, но от использования шерсти зависят условия её производства.\n"
        "4. Бамбук - Быстрорастущий, легкообрабатываемый материал, но следует проверять методы обработки.\n"
        "5. Органический хлопок - Выращенный без химических удобрений, лучше для здоровья земли."
    )
    bot.reply_to(message, reply_text)

@bot.message_handler(commands=['stores'])
def stores(message):
    '''Предоставляет рекомендации по магазинам экологичной одежды'''
    reply_text = (
        "Вот несколько онлайн-магазинов, где вы можете купить экологичную одежду:\n"
        "1. Patagonia - известен своим экологичным подходом.\n"
        "2. People Tree - сертифицированная этичная мода.\n"
        "3. Everlane - открытая информация о производстве и устойчивых практиках.\n"
        "4. Ecolast - одежда из экологически чистых материалов.\n"
        "5. Reformation - мода с учетом устойчивости.\n"
    )
    bot.reply_to(message, reply_text)


@bot.message_handler(commands=['привет'])
def send_hello(message):
    bot.reply_to(message, "Привет! Как дела?")

@bot.message_handler(commands=['пока'])
def send_bye(message):
    bot.reply_to(message, "Пока! Удачи!")


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)

bot.infinity_polling()
