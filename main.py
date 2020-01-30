from utils import scrape_afisha_report

city_name = 'msk'

print('Загрузка афиши...')
report_list = scrape_afisha_report(city_name)

report_text = '\n'.join([
    f'"{movie["title"]}" {movie["min_age"]}, {movie["genre"]}, {movie["year"]}, {movie["country"]}, длительность {movie["duration"]}, веб-страница: {movie["href"]}'
    for movie in report_list
])
print(report_text)

input('Нажмите Enter для завершения ')