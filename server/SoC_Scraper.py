import time
import random
import sys

#Flask
from flask import Flask,jsonify

#Processes
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from multiprocessing.pool import Pool

#UCLAScraper
from UCLAScraper import UCLAScraper

BASE_URL = "https://sa.ucla.edu/ro/public/soc"

def worker_scrape_batch(subjectID_list: list, term: str, headless: bool):
    with UCLAScraper(term,headless) as scraper:
        for subjectID in subjectID_list:
            scraper.scrape_subject(subjectID)
        
def wrapper_worker(args):
    return worker_scrape_batch(*args)

def SoC_Scraper(subjects_path, section_directory):
    try:
        #opens csv file
        subject_csv = open(subjects_path, "r")

        #stores subjectID string
        subjectID_list = []

        jobs = []

        start_time = time.perf_counter()

        for i, line in enumerate(subject_csv):
            line = line.strip()
            lines = line.split("(")
            if (len(lines) > 1):
                line = line.split("(")[len(lines) - 1][:-1]   
            subjectID_list.append(line)
        
        num_workers = 4
        
        random.shuffle(subjectID_list)

        # splits the subject list into even sized batches
        batches = [subjectID_list[i::num_workers] for i in range(num_workers)]
        
        #creates job args from the batches
        job_args = [(batch, "25W", True) for batch in batches]
        job_args = [(["MATH"], "25W", False)]

        print(f"Starting {len(job_args)} workers to scrape {len(subjectID_list)} subjects.")
        print("-" * 50)
        print(job_args)
        # PROCESS POOL EXECUTOR
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            executor.map(wrapper_worker, job_args)

        print("-" * 50)
        print(f"All workers finished. Total execution time: {time.perf_counter() - start_time:.2f} seconds")
        return "no issue"
    except Exception as e:
        return str(e)
    sys.stdout.flush()