import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import re

BASE_URL = "https://store-locations.underarmour.com/"

def is_phone_number(text):
    # Define the regular expression pattern for the phone number format XXX-XXX-XXXX
    pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
    # Match the pattern with the input text
    if pattern.match(text):
        return True
    return False


def get_all_links(url, query_selector = 'ul.contentlists li a'):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        links = [a['href'] for a in soup.select(query_selector) if 'href' in a.attrs]
        return links
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")
        return []

def get_store_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        store_details = []
        content_items = soup.select('div#content .itemlist')
        for item in content_items:
            divs = item.find_all('div')
            if len(divs) > 1:
                spans = divs[1].find_all("span")
                address = []
                for span in spans:
                    address_part = span.get_text(strip=False)
                    if is_phone_number(address_part):
                        break
                    address.append(address_part.strip())
                    
                # second_div_text = divs[1].get_text(strip=False).replace("Store Details", "")
                #second_div_text = ','.join(second_div_text.split())
                store_details.append(','.join(address))
        return store_details
    else:
        print(f"Failed to retrieve store details, status code: {response.status_code}")
        return []

def extract_last_segment(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    if path_segments:
        return path_segments[-1]  # Assuming the state segment is the last segment in the path
    return None

def parse_state_store_links(state_link, interval=1):
    store_links = get_all_links(state_link, 'ul.contentlist li a')
    stores_by_county = {}
    for link in store_links:
        store_url = link
        county = extract_last_segment(store_url)
        store_details = get_store_details(store_url)
        if county not in stores_by_county:
            stores_by_county[county] = []
        stores_by_county[county].extend(store_details)
    return stores_by_county

def main():
    state_links = get_all_links(BASE_URL)
    all_stores = {}
    for state_link in state_links:
        state = extract_last_segment(state_link)
        all_stores[state] = parse_state_store_links(state_link)

    # Print the final JSON output
    print(json.dumps(all_stores, indent=4))

if __name__ == "__main__":
    main()
