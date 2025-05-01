if open('ru_imdb_top_25.csv').readlines():
    pass
else:
    for s in open('ru_imdb_top_25.csv').readlines():
        print(s)