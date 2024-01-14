import argparse
import requests
import re
import socket
import threading
import time
import datetime
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import urllib3
from threading import Lock
from urllib.parse import urlparse, urlunparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def banner():
    print("""
                ____            _       _       _____    ___  
               / ___|   _   _  | |__   | |__   |  ___|  ( _ ) 
               \___ \  | | | | | '_ \  | '_ \  | |_     / _ \ 
                ___) | | |_| | | |_) | | | | | |  _|   | (_) | 
               |____/   \__,_| |_.__/  |_| |_| |_|      \___/       

                              Coded By Ares
    """)

def setup_logging(folder_name):
    log_file_path = os.path.join(folder_name, 'history_log.log')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    class NoErrorFilter(logging.Filter):
        def filter(self, record):
            return record.levelno < logging.ERROR

    console_handler.addFilter(NoErrorFilter())

def find_links(session, url, regex):
    try:
        resp = session.get(url, timeout=3)
        try:
            return re.findall(regex, resp.text)
        except re.error as e:
            logging.error(f"Regex error: {e} in URL: {url}")
            return []
    except (requests.exceptions.ConnectionError, socket.gaierror, requests.exceptions.Timeout) as e:
        logging.error(f"Error finding links in {url}: {e}")
        return []

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", required=True, help="Specify the domain to scan")
    parser.add_argument("-n", "--name", default='subdomains_list.txt', dest="file_name", help="Specify the file name for saving results (optional)")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Specify the number of max workers for threading (optional)")
    parser.add_argument("-l", "--large", action='store_true', help="Use large subdomains base file (optional)")

    args = parser.parse_args()

    # Добавление префикса 'https://' если он отсутствует
    if not args.domain.startswith(('http://', 'https://')):
        args.domain = 'https://' + args.domain

    return args

def send_request(session, url, results_folder):
    try:
        return session.get(url, timeout=5, verify=False)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, socket.gaierror) as e:
        error_message = f"Error with URL: {url} - {e}"
        logging.error(error_message)
        with open(os.path.join(results_folder, 'now_not_available.txt'), 'a') as f:
            f.write(url + '\n')
        return None

def send_request_thread(session, url, folder_name, file_name, progress_report, lock):
    resp = send_request(session, url, folder_name)
    with lock:
        progress_report['checked'] += 1
        if resp and resp.ok:
            with open(os.path.join(folder_name, file_name), 'a') as f:
                f.write(url + '\n')
            progress_report['found'] += 1

def fuzzer(session, domain, folder_name, file_name, progress_report, lock, subdomains_base):
    total = 0
    with open(subdomains_base, "r") as wordlist_file, ThreadPoolExecutor(max_workers=4) as executor:
        for subd in wordlist_file:
            subd = subd.strip()
            if subd:
                parsed_url = urlparse(domain)
                new_netloc = subd + "." + parsed_url.netloc.replace('www.', '')
                new_url = urlunparse(parsed_url._replace(netloc=new_netloc))
                executor.submit(send_request_thread, session, new_url, folder_name, file_name, progress_report, lock)
                total += 1
    progress_report['total'] = total

def progress_monitor(progress_report, timeout=300):
    start_time = time.time()
    base_file = 'base_large.txt' if progress_report['large'] else 'base.txt'
    base_count = 4351335 if progress_report['large'] else 114665

    while True:
        with progress_report['lock']:
            checked = progress_report.get('checked', 0)
            found = progress_report.get('found', 0)
        if checked >= progress_report.get('total', 0) and progress_report.get('total', 0) != 0:
            logging.info(f"All subdomains have been checked. Found working subdomains: {found}")
            break
        if time.time() - start_time > timeout:
            logging.warning(f"Waiting time has been exceeded. Checked {checked} subdomains. Found working subdomains: {found}")
            break
        logging.info(f'Checked {checked} from {base_count} subdomains ...... FIND: {found}')
        time.sleep(5)

def create_directory_for_results(domain):
    formatted_domain = domain.replace("https://", "").replace("www.", "").split('/')[0]
    folder_name = f"{formatted_domain}_{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
    os.makedirs(folder_name, exist_ok=True)
    setup_logging(folder_name)
    return folder_name

def save_subdomains_to_file(subdomains, folder_name):
    file_path = os.path.join(folder_name, 'link_list.txt')
    with open(file_path, 'w') as file:
        for subdomain in subdomains:
            if subdomain.startswith('https:'):
                file.write(subdomain + '\n')
    total_links = len(subdomains)
    logging.info(f"Total links found on the site: {total_links}")

if __name__ == "__main__":
    banner()
    lock = Lock()
    options = parse_arguments()
    session = requests.Session()
    domain = options.domain

    results_folder = create_directory_for_results(domain)

    found_links = find_links(session, domain, '(?:href=")(.*?)"')

    save_subdomains_to_file(found_links, results_folder)

    subdomains_base = 'base_large.txt' if options.large else 'base.txt'

    progress_report = {'lock': lock, 'checked': 0, 'total': 0, 'found': 0, 'large': options.large}
    progress_thread = threading.Thread(target=progress_monitor, args=(progress_report,))
    progress_thread.start()

    fuzzer(session, domain, results_folder, options.file_name, progress_report, lock, subdomains_base)
    progress_thread.join()
