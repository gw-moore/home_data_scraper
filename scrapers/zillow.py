"""Module for scraping zillow.com home listings
"""

import datetime as dt
import os
from random import randrange
from typing import Dict, List, Tuple, Union

import bs4
import requests
from bs4 import BeautifulSoup

from scrapers.nord_servers import nord_servers

nord_username = os.environ["NORD_USERNAME"]
nord_password = os.environ["NORD_PASSWORD"]

request_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.8",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
}


def setup_proxies(server_list):
    proxies = {
        "http": f"socks5://{nord_username}:{nord_password}@{nord_servers[randrange(len(server_list))]}:1080",
    }
    return proxies


def get_card_info(
    url: str, req_header: Dict[str, str] = request_headers
) -> List[bs4.element.Tag]:
    """Extract home card info from a zillow page

    Args:
        url (str): URL string of zillow page.
    """
    proxies = setup_proxies(nord_servers)
    # prep request
    with requests.Session() as s:
        r = s.get(url, headers=req_header, proxies=proxies)

    # get page text
    soup = BeautifulSoup(r.content, "lxml")

    # find all card info
    card_info = soup.find_all("div", {"class": "list-card-info"})
    return card_info


home_url_modifiers = {"'": "", '"': "", " ": ""}


def clean_home_url(card_info: list) -> List[str]:
    """From a set of zillow card info, extract urls to home details"""
    urls = []
    for i, c in enumerate(card_info):
        # first extract from url text
        text = str(card_info[i]).split("href=")[1].split("tabindex")[0]
        # then clean the url text
        for k, v in home_url_modifiers.items():
            text = text.replace(k, v)
        # append the finished text to urls
        urls.append(text)
    return urls


def get_prop_soup(
    url: str, req_header: Dict[str, str] = request_headers
) -> Union[str, Dict[str, Tuple[str, bs4.element.Tag]]]:
    """Get the website text of the home details page"""
    proxies = setup_proxies(nord_servers)
    prop_text = {}

    # extract the property address
    address = str(url).split("/")[4]
    # prep the request
    with requests.Session() as s:
        r = s.get(url, headers=request_headers, proxies=proxies)
    # get the webpage text
    soup = BeautifulSoup(r.content, "lxml")
    # store text in the dictionary
    prop_text[address] = (url, soup)

    return address, prop_text


def init_values_dict():
    values_dict = {
        "url": None,
        "address": None,
        "zip_code": None,
        "school_district": None,
        "list_price": None,
        "list_date": None,
        "bedrooms": None,
        "bathrooms_total": None,
        "bathrooms_full": None,
        "bathrooms_3_4": None,
        "bathrooms_1_2": None,
        "bathrooms_1_4": None,
        "features": None,
        "level": None,
        "basement": None,
        "flooring": None,
        "flooring_0": None,
        "flooring_1": None,
        "flooring_2": None,
        "heating_features": None,
        "heating_features_0": None,
        "heating_features_1": None,
        "heating_features_2": None,
        "total_number_of_fireplaces": None,
        "cooling_features": None,
        "appliances_included_0": None,
        "appliances_included_1": None,
        "appliances_included_2": None,
        "appliances_included_3": None,
        "appliances_included_4": None,
        "appliances_included_5": None,
        "appliances_included_6": None,
        "appliances_included_7": None,
        "total_interior_livable_area_sqft": None,
        "finished_area_below_ground_sqft": None,
        "parking_features": None,
        "parking_features_0": None,
        "parking_features_1": None,
        "attached_garage": None,
        "garage_spaces": None,
        "covered_spaces": None,
        "has_uncovered_spaces": None,
        "stories": None,
        "exterior_features": None,
        "patio_and_porch_details": None,
        "patio_and_porch_details_0": None,
        "patio_and_porch_details_1": None,
        "fencing": None,
        "fencing_0": None,
        "fencing_1": None,
        "view_description": None,
        "lot_size_acres": None,
        "parcel_number": None,
        "zoning_description": None,
        "home_type": None,
        "construction_materials": None,
        "additional_structures_included": None,
        "windows": None,
        "windows_0": None,
        "windows_1": None,
        "windows_2": None,
        "windows_3": None,
        "new_construction": None,
        "year_built": None,
        "electric_information": None,
        "gas_information": None,
        "internet_and_tv": None,
        "utilities_for_property": None,
        "sunscore": None,
        "security_features": None,
        "region": None,
        "tax_assessed_value_dollars": None,
        "annual_tax_amount_dollars": None,
        "mls_id": None,
        "roof": None,
        "roof_0": None,
        "roof_1": None,
        "interiorfeatures": None,
        "bedroomspossible": None,
        "farmlandareaunits": None,
        "roadfrontagetype": None,
        "currentuse": None,
        "mlsstatus": None,
    }
    return values_dict


def extract_prop_atts(
    prop_text: Dict[str, Tuple[str, bs4.element.Tag]]
) -> Dict[str, List[str]]:
    property_attrs = init_values_dict()

    # k - property address
    # v - webpage text
    for k, v in prop_text.items():
        # the values of the dict is a tuple of str and soup
        # assign each to a name for ease of use
        url = v[0]
        property_attrs["url"] = url
        soup = v[1]

        # get the element that are stored are different parts of the page
        # make the property address and zip attributes
        address_elements = k.lower().replace("-", "_").split("_")
        property_attrs["address"] = "_".join(address_elements[:-1])
        property_attrs["zip_code"] = address_elements[-1]
        # find the price
        prop_list_price = soup.find("span", {"class", "ds-value"}).text
        prop_list_price = prop_list_price.replace("$", "").replace(",", "")
        property_attrs["list_price"] = prop_list_price
        # get time on zillow
        top_text = soup.find_all("div", {"class": "Text-aiai24-0"})
        for tt in top_text:
            if "day" in tt.text:
                time_on_zillow = tt.text
                if time_on_zillow == "--":
                    time_on_zillow = 0
                    break
                break
        # calculate list date with the time on zillow var
        today = dt.date.today()
        list_date = today - dt.timedelta(int(time_on_zillow.split(" ")[0]))
        property_attrs["list_date"] = list_date
        # get school district
        school_district = soup.find(
            "span", {"class", "ds-school-value ds-body-small"}
        ).text
        property_attrs["school_district"] = school_district

        # extract property attributes
        for x in soup.find_all("span", {"class": "Text-aiai24-0 iUFtIX"}):
            # split the attribute string into key and value
            att = x.text.split(":")
            # key is the attribute name
            key = att[0].lower().replace(" ", "_")
            # clean the number of bathroom keys
            # this is done so the keys flow in the sql table
            if "bathroom" in key:
                if key == "bathrooms":
                    key = "bathrooms_total"
                elif "full" in key:
                    key = "bathrooms_full"
                elif "3/4" in key:
                    key = "bathrooms_3_4"
                elif "1/2" in key:
                    key = "bathrooms_1_2"
                elif "1/4" in key:
                    key = "bathrooms_1_4"
            # clean the value
            # based on the value the key may be modified
            if len(att) > 1:
                value = att[1].lstrip().rstrip().lower()
                if "$" in value:
                    value = value.replace("$", "").replace(",", "")
                    key = key + "_dollars"
                elif "sqft" in value:
                    value = value.replace(",", "").replace(" sqft", "")
                    key = key + "_sqft"
                elif "acres" in value:
                    value = value.replace(" acres", "")
                    key = key + "_acres"
                elif "," in value:
                    values = value.split(",")
                    fin_values = []
                    for v in values:
                        fin_values.append(
                            v.lstrip()
                            .rstrip()
                            .replace(" ", "_")
                            .replace("(", "")
                            .replace(")", "")
                            .replace("_/_", "_")
                        )
                    # since we split this is a list
                    # we need to extract each element of the list into its own key,value pair
                    for i, v in enumerate(fin_values):
                        property_attrs[f"{key}_{i}"] = v
                    # if we get here, move to the next element in the list
                    continue
                elif value == "":
                    value = None
                else:
                    value = (
                        value.replace(" ", "_")
                        .replace("(", "")
                        .replace(")", "")
                        .replace("sun_number™", "")
                    )
            else:
                value = None
            property_attrs[key] = value
    return property_attrs
