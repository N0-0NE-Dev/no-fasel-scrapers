from subprocess import Popen
from time import perf_counter

start_time = perf_counter()

movies_process = Popen(["python", "MovieScraper.py"])
series_process = Popen(["python", "SeriesScraper.py"])
anime_process = Popen(["python", "AnimeScraper.py"])

movies_process.wait()
series_process.wait()
anime_process.wait()

trending_process = Popen(["python", "TrendingScraper.py"])
postprocessing_process = Popen(["python", "PostProcessing.py"])

trending_process.wait()
postprocessing_process.wait()

end_time = perf_counter()

print(
    f"Finished scraping all of fasel in about {round((end_time - start_time) / 60)} minute(s)"
)
