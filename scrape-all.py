from subprocess import Popen
from time import perf_counter

start_time = perf_counter()

movies_process = Popen(["python", "movies-scraper.py"])
series_process = Popen(["python", "series-scraper.py"])
anime_process = Popen(["python", "anime-scraper.py"])

movies_process.wait()
series_process.wait()
anime_process.wait()

trending_process = Popen(["python", "trending-scraper.py"])
post_processing_process = Popen(["python", "post-processing.py"])
all_conent_indexing_process = Popen(["python", "all-content-indexer.py"])

trending_process.wait()
post_processing_process.wait()
all_conent_indexing_process.wait()

end_time = perf_counter()

print(
    f"Finished scraping all of fasel in about {round((end_time - start_time) / 60)} minute(s)"
)
