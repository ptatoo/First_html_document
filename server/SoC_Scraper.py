
import csv
import time
import re
from time import sleep

import queue

#Processes
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

#UCLAScraper
from UCLAScraper import UCLAScraper

BASE_URL = "https://sa.ucla.edu/ro/public/soc"

def worker_scrape_batch(subjectID_list: list, term: str, headless: bool = True):
    with UCLAScraper(term,headless) as scraper:
        for subjectID in subjectID_list:
            scraper.scrape_subject(subjectID)
        


if __name__ == '__main__':

    multiprocessing.set_start_method('spawn')
    
    #opens csv file
    subject_csv = open("server/Subjects.txt", "r")

    #stores subjectID string
    subjectID_list = []

    jobs = []

    start_time = time.perf_counter()

    for i, line in enumerate(subject_csv):
        if(i<12):
            line = line.strip()
            lines = line.split("(")
            if (len(lines) > 1):
                line = line.split("(")[len(lines) - 1][:-1]   
            subjectID_list.append(line)
    
    num_workers = 4

    # splits the subject list into even sized batches
    print(subjectID_list)
    batches = []
    # prep args
    # Create a list of tuples. Each tuple is the set of arguments for one worker.
    job_args = [(batch, "25F", False) for batch in batches]

    print(f"Starting {len(job_args)} workers to scrape {len(subjectID_list)} subjects.")
    print("-" * 50)

    # PROCESS POOL EXECUTOR
    with UCLAScraper("25f", True) as scraper:
        scraper.scrape_subject("MATH")


    print("-" * 50)
    print(f"All workers finished. Total execution time: {time.perf_counter() - start_time:.2f} seconds")
    

    