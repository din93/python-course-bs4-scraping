import requests, time, datetime, os
from bs4 import BeautifulSoup

def scrape_afisha_report(city_name):
    date_today = datetime.date.today().strftime("%Y%m%d") # формат даты - 20200108
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
        movie_info = soup_movie_page.select('.movieInfoV2_info .movieInfoV2_infoItem span.movieInfoV2_infoData')
        movie_info = dict(enumerate(movie_info))
        movie_duration = movie_info.get(0).text if movie_info.get(0) else '~'
        movie_year = movie_info.get(1).text if movie_info.get(1) else '~'
        movie_premier_date = movie_info.get(2).text if movie_info.get(2) else '~'
        movie_min_age = movie_info.get(3).text if movie_info.get(3) else '~'
        movie_distributor = movie_info.get(4).text if movie_info.get(4) else '~'
        
        movie_avalable_dates = soup_movie_page.select('.scheduleShort_filter .showtimesFilter_week a span.week_num')
        movie_avalable_dates = [date_span.text.replace('\xa0', ' ') for date_span in movie_avalable_dates]
        movie_theater_names = soup_movie_page.select('.showtimes_item .showtimes_cell .theater .theater_name')
        movie_theater_names = [theater_name.text for theater_name in movie_theater_names]
        movie_theater_addresses = soup_movie_page.select('.showtimes_item .showtimes_cell .theater .theater_info')
        movie_theater_addresses = [theater_address.text.replace('\xa0', ' ') for theater_address in movie_theater_addresses]
        movie_theatres = list(zip(movie_theater_names, movie_theater_addresses))

        afisha_report.append(dict(
            title=movie_title,
            genre=movie_genre,
            min_age=movie_min_age,
            year=movie_year,
            country=movie_year_country.split(', ')[1],
            duration=movie_duration,
            href=movie_href,
            avalable_dates=movie_avalable_dates,
            theatres=movie_theatres,
            distributor=movie_distributor,
            premier_date=movie_premier_date
        ))
    
    return afisha_report