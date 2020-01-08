import requests, time, datetime
from bs4 import BeautifulSoup

date_today = datetime.date.today().strftime("%Y%m%d") # формат даты - 20200108
city_name = 'ufa'

response = requests.get(f'https://{city_name}.kinoafisha.info/movies/?order=popular&date%5B%5D={date_today}&time=all&movies=0&cinemas=0&tickets=0&price=')
soup_afisha = BeautifulSoup(response.text, 'html.parser')

movies = soup_afisha.select('article.films_item')
afisha_report = []
for movie in movies:
    movie_title = movie.select_one('.films_content .films_right a span span').text
    movie_genre = movie.select('.films_content .films_right span.films_info')[0].text
    movie_year_country = movie.select('.films_content .films_right span.films_info')[1].text
    movie_href = movie.select_one('.films_content .films_right a')['href']
    regional_movie_href = movie_href.replace('www', city_name)

    soup_movie_page = BeautifulSoup(requests.get(regional_movie_href).text, 'html.parser')
    movie_info = soup_movie_page.select('.movieInfoV2_info .movieInfoV2_infoItem')
    movie_duration = movie_info[0].select_one('span.movieInfoV2_infoData').text
    movie_year = movie_info[1].select_one('span.movieInfoV2_infoData').text
    movie_premier_date = movie_info[2].select_one('span.movieInfoV2_infoData').text
    movie_min_age = movie_info[3].select_one('span.movieInfoV2_infoData').text
    movie_distributor = movie_info[4].select_one('.movieInfoV2_infoData').text

    print(f'"{movie_title}" {movie_min_age}, {movie_genre}, {movie_year_country}, длительность {movie_duration}, веб-страница: {movie_href}')
    time.sleep(1)

input('Нажмите Enter для завершения ')