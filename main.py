"""Script to scrape X county homes from zillow website
"""
import argparse
import datetime
import logging
import os
import pickle
import random

import pandas as pd

import db_helpers.zillow_db as zdb
import scrapers.zillow as zs

# setup argparse
parser = argparse.ArgumentParser(description="Scrape data from zillow.com")
parser.add_argument(
    "-c",
    "--county",
    type=str,
    nargs=1,
    required=False,
    action="store",
    dest="county",
    help="County to collect home data in",
    default="hamilton-county-oh",
)

parser.add_argument(
    "-np",
    "--num_pages",
    type=int,
    nargs=1,
    required=False,
    action="store",
    dest="num_pages",
    help="Number of zillow landing pages to scrape home URLs",
    default=5,
)

args = parser.parse_args()


def main(county: str, num_pages: int):
    """
    Main program to scrape data

    Parameters
    ----------
    county : str
        Which county to collect data in. Defaults to hamilton-county-oh
    num_pages : int
        Number of landing pages to scrape. Defaults to 5.
    """
    # create a logs folder for this run
    cwd = os.getcwd()
    time = datetime.datetime.now()
    log_file = (
        args.county.replace("-", "_")
        + "_"
        + str(time).replace(" ", "_").replace(":", "_").replace(".", "_")
    )
    logging.basicConfig(
        filename=f"logs/{log_file}.log",
        filemode="a",
        format="%(name)s - %(levelname)s - %(message)s",
    )

    # create a directory to store raw data
    os.mkdir(f"{cwd}/raw_data/{log_file}")

    # connect to the SQLite DB
    conn = zdb.connect_to_zillow_db()

    # 1. collect the card urls from zillow landing pages
    # loop for five pages for zillow.com

    # this list will save the url data scraped from the zillow landing pages
    # this list will be saved as a pickled file
    prop_urls_list = []

    for i in list(range(args.num_pages[0])):
        # get the urls from the page
        url = f"https://www.zillow.com/{args.county}/{i}_p/"
        card_info = zs.get_card_info(url=url)
        # extract the property urls from the cards
        prop_urls = zs.clean_home_url(card_info)
        prop_urls_list.append(prop_urls)

    # pickle the prop_urls_list in case of errors
    outfile_prop_urls_list = open(f"raw_data/{log_file}/prop_urls_list.pkl", "wb")
    pickle.dump(prop_urls_list, outfile_prop_urls_list)
    outfile_prop_urls_list.close()

    # this dictionary is going to hold the raw property attrs dicts
    # this dict will be saved as a pickled file
    home_attr_dict = {}

    # 2. loop over each url scrapped from the landing pages and extract the house attributes
    # loop over each url scraped from the page to extract the info
    num_errors = 0
    for l in prop_urls_list:
        for url in l:
            # collect the prop attributes
            prop_address, prop_dict = zs.get_prop_soup(url=url)
            prop_attrs = zs.extract_prop_atts(prop_dict)

            # check the database to see if I hit this home already
            # if no results are returned from the database,
            # scrape the webpage and get the home attributes
            url_in_db = zdb.get_listing_by_url(conn, url={"url": url})

            if len(url_in_db) == 0:
                # save prop_attrs dictionary
                home_attr_dict[prop_dict[prop_address][0]] = prop_attrs
                # create a new record in the database
                try:
                    zdb.insert_listing_record(conn, prop_attrs)
                except ProgrammingError as e:
                    num_errors += 1
                    logging.error(f"Insert of record from {url} failed. Error: {e}")
            # if results are returned from the database,
            # compare the attributes of existing record(s) and new data
            else:
                pd_query = f"""SELECT *
                            FROM zillow_listings
                            WHERE url='{url}'"""
                records = pd.read_sql_query(pd_query, conn)
                # Check all returned records against prop_attrs to see if it already exists
                if records.isin(prop_attrs).all().all():
                    continue
                else:
                    try:
                        # save prop_attrs dictionary
                        home_attr_dict[prop_dict[prop_address][0]] = prop_attrs
                        zdb.insert_listing_record(conn, prop_attrs)
                    except ProgrammingError as e:
                        num_errors += 1
                        logging.error(f"Insert of record from {url} failed. Error: {e}")
            # sleep if off big guy
            time.sleep(random.lognormvariate(1.5, 0.5))

    # pickle the home_attr_dict in case of errors
    outfile_home_attr_dict = open(f"raw_data/{log_file}/home_attr_dict.pkl", "wb")
    pickle.dump(prop_urls_list, outfile_home_attr_dict)
    outfile_home_attr_dict.close()

    # ! TO DO
    # 3. Send email if any errors


if __name__ == "__main__":
    main(county=args.county, num_pages=args.num_pages)
