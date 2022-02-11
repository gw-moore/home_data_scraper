"""Module for scraping hamilton county auditor website
"""

from typing import Dict, List, Tuple, Union

import requests
from bs4 import BeautifulSoup

req_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.8",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
}


def get_webpage_text(parcel_num, page_postfix):
    # prep request
    with requests.Session() as s:
        url = f"https://wedge1.hcauditor.org/view/re/{parcel_num}/2019/{page_postfix}"
        r = s.get(url, headers=req_headers)

    # get page text
    soup = BeautifulSoup(r.content, "lxml")


def scrape_summary_page(soup):
    data_dict = {}
    data_dict["last_sale_amt"] = (
        soup.find("td", text="Last Sale Amount").find_next_sibling().text
    )
    data_dict["last_sale_date"] = (
        soup.find("td", text="Last Sale Date").find_next_sibling().text
    )
    data_dict["year_built"] = (
        soup.find("td", text="Year Built").find_next_sibling().text
    )
    data_dict["acreage"] = soup.find("td", text="Acreage").find_next_sibling().text
    return data_dict
