import logging
import sqlite3
from collections import defaultdict
from pprint import pprint

import requests
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

if open('data/ru_imdb_top_25.csv'):
    pass
else:

    import requests
    import csv

    with open('data/ru_imdb_top_25.csv', 'w', newline='') as csvfile:
        fieldnames = ['film', 'year', 'time', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        f = open('data/imdb_top_1000.csv')
        title = f.readline()
        i = 1
        for s in f.readlines()[:10]:
            film_inf = list(s.split(','))
            film = film_inf[0]
            headers = {"X-API-KEY": "JS610HH-JHNMHK5-PFJ8M72-RA4VHDH"}

            query = film
            params = {
                'query': query
            }
            response = requests.get(
                'https://api.kinopoisk.dev/v1.4/movie/search',
                headers=headers,
                params=params
            )
            movies = response.json()

            movies1 = movies['docs'][0]
            writer.writerow(
                {'film': movies1['name'], 'year': film_inf[1], 'time': list(film_inf[2].split(' '))[0] + ' минут',
                 'rating': film_inf[3]})
            print({'film': movies1['name'], 'year': film_inf[1], 'time': list(film_inf[2].split(' '))[0] + ' минут',
                   'rating': film_inf[3]})

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
reply_keyboard = [['/search', '/top_films'],
                  ['/favorite', '/help']]
inline_keyboard = [
    [
        InlineKeyboardButton("Добавить в избранное", callback_data="1"),
        InlineKeyboardButton("Новый поиск", callback_data="2"),
    ]]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
users = defaultdict()
last_requests = []
bd = sqlite3.connect('data/Films.sqlite')


async def start(update, context):
    user = update.effective_user
    '''await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот фильмов! 🍿🎥✮⋆˙ Можешь найти любой фильм, нажав команду /search -`♡´-",
        reply_markup=markup
    )'''
    caption = rf"Привет {user.mention_html()}! Я бот фильмов FILMIX! 🍿🎥✮⋆˙ Можешь найти любой фильм, нажав команду /search"
    photo_path = 'data/img.png'
    await update.message.reply_photo(
        photo=open(photo_path, 'rb'),
        caption=caption,
        parse_mode='HTML', reply_markup=markup
    )



async def find_film(update, context):
    await update.message.reply_text(
        "Напишите название фильма, который Вы хотите найти")

    return 1


async def finding(update, context):
    film0 = update.message.text

    headers = {"X-API-KEY": "JS610HH-JHNMHK5-PFJ8M72-RA4VHDH"}

    query = film0
    params = {
        'query': query
    }
    response = requests.get(
        'https://api.kinopoisk.dev/v1.4/movie/search',
        headers=headers,
        params=params
    )
    movies = response.json()

    movies1 = movies['docs'][0]
    pprint(movies1)
    await update.message.reply_text('Возможно, вы имели ввиду:')
    inf_film = [
        f'🎬 Название фильма - {movies1['name']}',
        f'🎬 Год выпуска фильма - {movies1['year']}',
        f'🎬 Страны выпуска: {', '.join([i['name'] for i in movies1['countries']])}',
        f'🎬 Жанры: {', '.join([i['name'] for i in movies1['genres']])}',
        f'🎬 Длительность фильма - {movies1['movieLength']} минут',
        f'🎬 Место в топе 250 - {movies1['top250']}',
        f'🎬 Оценка - {movies1['rating']['imdb']}',
        f'🎬 Возрастное ограничение - {movies1['ageRating']}+\n',
        f'🎥 Описание фильма: {movies1['description'].replace('\xa0', ' ')}'

    ]

    last_requests.append(movies1['name'])
    r = requests.get(movies1['poster']['url'])
    url = r.url
    await update.message.reply_text(url)

    for i in range(50):
        print('--------')
    ans = ''
    for s in inf_film:
        ans += s + '\n'

    reply_markup1 = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text(ans)
    await update.message.reply_text('Добавить фильм в избранное?', reply_markup=reply_markup1)


async def button(update, context):
    query = update.callback_query
    await query.answer()
    if int(query.data) == 1:
        await query.edit_message_text(
            text=f"Фильм успешно добавлен в избранное. \nПосмотреть избранное можно по команде /favorite")
        sqlite_insert_query = """INSERT INTO Users
                                  (username, tgnik, films)
                                  VALUES
                                  (?, ?, ?);"""
        username = list(list(str(update.effective_user).split('id='))[1].split(','))[0]
        tgnik = list(list(str(update.effective_user).split("username='"))[1].split("'"))[0]

        print(tgnik)
        cursor = bd.cursor()
        data_tuple = (username, tgnik, last_requests[-1])
        cursor.execute(sqlite_insert_query, data_tuple)
        bd.commit()

        if username in users:
            users[username].append(last_requests[-1])
        else:
            users[username] = [last_requests[-1]]
        print(users)
    else:
        await query.edit_message_text(text="Напишите название фильма, который Вы хотите найти")

        return 1


async def top_of_films(update, context):
    await update.message.reply_text(
        "Топ 10 фильмов по версии IMDB:")
    f = open('data/ru_imdb_top_25.csv')
    top_films = []
    tit = f.readline()
    for film in f.readlines():
        film_i = list(film[:-1].split(','))
        r = f'{film_i[0]}: {film_i[1]} год, длительность - {film_i[2]}, рейтинг IMDB - {film_i[3]}'
        top_films.append(r)
    ans = ''
    i = 1
    for s in top_films:
        ans += str(i) + '. ' + s + '\n'
        i += 1
        if i == 11:
            break
    await update.message.reply_text(ans)


async def yours_films(update, context):
    await update.message.reply_text("Ваши избранные фильмы:")
    ans = ''
    cursor = bd.cursor()
    username = list(list(str(update.effective_user).split('id='))[1].split(','))[0]

    result = cursor.execute(f"""SELECT * FROM Users
                WHERE username = ?""", (username,)).fetchall()
    print(result)
    found = []
    if result:
        for fi in result:
            if fi[3] not in found:
                found.append(fi[3])

        i = 1
        for fi in found:
            ans += str(i) + '. ' + fi + '\n'
            i += 1


    else:
        ans = 'Избранные фильмы не найдены :('

    await update.message.reply_text(ans)
    print(ans)


async def hz(update, context):
    await update.message.reply_text(
        "хз, че-то тут будет")


async def help_command(update, context):
    text = ''
    await update.message.reply_text('''Инструкция по использованию бота "Фильмы" 🍿🎥 1. Запуск бота Начните общение 
    с ботом, нажав кнопку Start или отправив команду /start. Бот приветствует вас и предоставляет клавиатуру с 
    основными командами.

2. Основные команды /search — поиск фильма по названию. После ввода команды бот запросит название фильма. Отправьте 
название, и бот найдет информацию о фильме (год выпуска, жанр, рейтинг и т. д.), а также покажет постер.

/top_films — просмотр топ-10 фильмов по версии IMDB. Бот выведет список с названиями, годами выпуска, длительностью и 
рейтингом.

/favorite — просмотр вашего списка избранных фильмов. Фильмы можно добавить в избранное во время поиска.

/help — краткая инструкция по использованию бота (эта информация).

/hz — команда без функционала (на будущее).

3. Поиск фильма
Введите команду /search.

Бот попросит ввести название фильма. Отправьте название.

Бот найдет информацию о фильме и предложит:

Добавить фильм в избранное (кнопка "Добавить в избранное").

Начать новый поиск (кнопка "Новый поиск").

4. Добавление в избранное После поиска фильма нажмите кнопку "Добавить в избранное", чтобы сохранить фильм в вашем 
списке. Просмотреть избранное можно командой /favorite.

5. Просмотр избранного
Введите команду /favorite, чтобы увидеть список сохраненных фильмов. Если список пуст, бот сообщит об этом.

6. Завершение работы
Чтобы завершить диалог, используйте команду /stop. Бот попрощается с вами.


    ''')


async def stop(update, context):
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(

        entry_points=[CommandHandler('search', find_film)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, finding)],

        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", find_film))
    application.add_handler(CommandHandler("top_films", top_of_films))
    application.add_handler(CommandHandler("favorite", yours_films))
    application.add_handler(CommandHandler("hz", hz))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    main()
