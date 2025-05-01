
import requests
import csv

with open('ru_imdb_top_25.csv', 'w', newline='') as csvfile:
    fieldnames = ['film', 'year', 'time', 'rating']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    f = open('imdb_top_1000.csv')
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
        writer.writerow({'film': movies1['name'], 'year': film_inf[1], 'time': list(film_inf[2].split(' '))[0] + ' минут', 'rating': film_inf[3]})
        print({'film': movies1['name'], 'year': film_inf[1], 'time': list(film_inf[2].split(' '))[0] + ' минут', 'rating': film_inf[3]})