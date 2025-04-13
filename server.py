# Импортируем необходимые классы.
import logging

from pprint import pprint

import requests
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)
reply_keyboard = [['/search', '/top_films'],
                  ['/favorite', '/hz']]
inline_keyboard = [
        [
            InlineKeyboardButton("Добавить в избранное", callback_data="1"),
            InlineKeyboardButton("Новый поиск", callback_data="2"),
        ]]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)



async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я бот фильмов! 🍿🎥✮⋆˙ Можешь найти любой фильм, нажав команду /search -`♡´-",
        reply_markup=markup
    )




async def help_command(update, context):
    await update.message.reply_text("тут будет тутор по боту")
async def find_film(update, context):

    await update.message.reply_text(
        "Напишите название фильма, который Вы хотите найти")

    return 1

async def finding(update, context):
    film = update.message.text

    headers = {"X-API-KEY": "QG01J6A-MCEMR61-KPKT65M-FWVD582"}

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
    pprint(movies)
    await update.message.reply_text('Возможно, вы имели ввиду:')
    inf_film = [
        f'🎬 Название фильма - {movies1['names'][0]['name']}',
        f'🎬 Год выпуска фильма - {movies1['year']}',
        f'🎬 Страны выпуска: {', '.join([i['name'] for i in movies1['countries']])}',
        f'🎬 Жанры: {', '.join([i['name'] for i in movies1['genres']])}',
        f'🎬 Длительность фильма - {movies1['movieLength']} минут',
        f'🎬 Место в топе 250 - {movies1['top250']}',
        f'🎬 Оценка - {movies1['rating']['imdb']}',
        f'🎬 Возрастное ограничение - {movies1['ageRating']}+\n',
        f'🎥 Описание фильма: {movies1['description'].replace('\xa0', ' ')}'

    ]
    r = requests.get(movies1['poster']['url'])
    url = r.url
    await update.message.reply_text(url)




    for i in range(50):
        print('--------')
    ans = ''
    for s in inf_film:
        ans += s + '\n'


    reply_markup1 = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text(ans, reply_markup=reply_markup1)

async def button(update, context):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    if int(query.data) == 1:
        await query.edit_message_text(text=f"Фильм успешно добавлен в избранное. \nПосмотреть избранное можно по команде /favotite")
    else:
        await query.edit_message_text(text="Напишите название фильма, который Вы хотите найти")

        return 1


async def top_of_films(update, context):
    await update.message.reply_text(
        "тут будут топы фильмов")


async def yours_films(update, context):
    await update.message.reply_text("ваши избранные фильмы")





async def hz(update, context):
    await update.message.reply_text(
        "хз, че-то тут будет")

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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", find_film))
    application.add_handler(CommandHandler("top_films", top_of_films))
    application.add_handler(CommandHandler("favorite", top_of_films))
    application.add_handler(CommandHandler("hz", hz))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    main()
