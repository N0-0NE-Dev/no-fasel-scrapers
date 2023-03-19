from subprocess import Popen
from time import perf_counter
from datetime import date

start_time = perf_counter()

movies_process = Popen(["python", "FaselMoviesScraper.py"])
series_process = Popen(["python", "FaselSeriesScraper.py"])
anime_process = Popen(["python", "FaselAnimeScraper.py"])
arabic_series_process = Popen(["python", "AkwamSeriesScraper.py"])
arabic_movies_process = Popen(["python", "AkwamMoviesScaper.py"])
we_cima_process = Popen(["python", "WeCimaScraper.py"])


movies_process.wait()
series_process.wait()
anime_process.wait()
arabic_series_process.wait()
arabic_movies_process.wait()
we_cima_process.wait()

trending_process = Popen(["python", "TrendingScraper.py"])
post_processing_process = Popen(["python", "Postprocessing.py"])

trending_process.wait()
post_processing_process.wait()

all_conent_indexing_process = Popen(["python", "AllContentIndexer.py"])

all_conent_indexing_process.wait()

end_time = perf_counter()

with open("./output/last-scraped.txt", "w") as fp:
    fp.write(date.today().strftime("%Y-%m-%d"))

print(
    f"Finished scraping all the content in about {round((end_time - start_time) / 60)} minute(s)"
)
