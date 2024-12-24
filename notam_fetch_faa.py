import requests
import re
import csv
import sys
import os
from bs4 import BeautifulSoup
import logging
import logging

# Configure logging to output to both a file and the terminal
log_file = 'notam_fetch_faa.log'  # Common log file for both scripts

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),  # Write to log file
        logging.StreamHandler()  # Display logs in the terminal
    ]
)

def extract_notam_fields(notam_text):
    """Extract structured NOTAM fields from raw NOTAM text."""
    notam_data = {
        'NOTAM No': '',
        'Q Code': '',
        'From': '',
        'To': '',
        'Schedule': '',
        'Text': '',
        'Lower Limit': '',
        'Upper Limit': '',
        'Created Time': '',
        'Farsi': ''
    }

    notam_text = re.sub(r'\s+', ' ', notam_text)

    patterns = {
        'NOTAM No': re.compile(r'([A-Z]\d{4}/\d{2})'),
        'Q Code': re.compile(r'Q\) (.+?)(?=[A-Z]\)|\Z)'),
        'From': re.compile(r'B\) (\d{10})'),
        'To': re.compile(r'C\) (\d{10}(?:\sEST)?|PERM)'),
        'Schedule': re.compile(r'D\) (.+?)(?=[A-Z]\)|\Z)'),
        'Text': re.compile(r'E\) (.+?)(?=[A-Z]\)|\Z)'),
        'Lower Limit': re.compile(r'F\) (\S+)'),
        'Upper Limit': re.compile(r'G\) (\S+)')
    }

    for key, pattern in patterns.items():
        match = pattern.search(notam_text)
        if match:
            notam_data[key] = match.group(1).strip()

    created_match = re.search(r'CREATED:\s*(\d{2}\s\w{3}\s\d{4}\s\d{2}:\d{2}:\d{2})', notam_text)
    if created_match:
        notam_data['Created Time'] = created_match.group(1)

    return notam_data

def fetch_faa_notams(icao):
    """Fetch NOTAMs from FAA for a given ICAO code."""
    url = f"https://www.notams.faa.gov/dinsQueryWeb/queryRetrievalMapAction.do?reportType=Raw&retrieveLocId={icao}&actionType=notamRetrievalbyICAOs"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return icao, response.text
    except requests.exceptions.RequestException as e:
        logging.warning(f"Failed to fetch FAA NOTAMs for {icao}: {e}")
        return icao, None

def parse_faa_notams(html_content, icao):
    """Parse NOTAMs from the FAA HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    notam_table = soup.select_one('#form1 div table tr td table:nth-of-type(3)')
    if not notam_table:
        logging.warning(f"No NOTAM table found for {icao} on FAA")
        return []

    notams_data = []
    notam_rows = notam_table.find_all('tr')[1:]

    for row in notam_rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue
        notam_text = cells[1].get_text(strip=True)
        if not notam_text:
            continue
        notam_dict = extract_notam_fields(notam_text)
        if not notam_dict:
            continue
        notams_data.append(notam_dict)

    return notams_data

def fetch_and_save_faa_notams(icao_list, output_file):
    # Include 'ICAO' as the first column
    fieldnames = ['ICAO', 'NOTAM No', 'Q Code', 'From', 'To', 'Schedule', 'Text', 'Lower Limit', 'Upper Limit', 'Created Time', 'Farsi']

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        total_icao = len(icao_list)
        logging.info(f"Processing {total_icao} ICAO codes...")

        for index, icao in enumerate(icao_list, start=1):
            logging.info(f"[{index}/{total_icao}] Fetching NOTAMs for {icao}...")
            response = fetch_faa_notams(icao)
            if response:
                _, html_content = response
                if html_content:
                    notams = parse_faa_notams(html_content, icao)
                    for notam in notams:
                        if isinstance(notam, dict):  # Ensure valid data is written
                            # Add the ICAO column to the NOTAM data
                            notam['ICAO'] = icao
                            writer.writerow(notam)
                        else:
                            logging.warning(f"Unexpected NOTAM format for {icao}: {notam}")
                else:
                    logging.warning(f"No HTML content found for {icao}.")
            else:
                logging.warning(f"No NOTAMs found for {icao}.")
        logging.info(f"All NOTAMs saved to {output_file}.")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: notam_fetch_faa.py {ICAO | filename.csv}")
        sys.exit(1)

    input_arg = sys.argv[1]
    icao_list = []

    if os.path.isfile(input_arg):
        # Load ICAO codes from CSV file
        with open(input_arg, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            icao_list = [row['ICAO'] for row in reader if 'ICAO' in row]
    else:
        icao_list = [input_arg]

    fetch_and_save_faa_notams(icao_list, "notam_fetch_faa.csv")
