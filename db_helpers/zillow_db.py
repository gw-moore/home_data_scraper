import sqlite3
from typing import Dict, List, Union

import pandas as pd


def connect_to_zillow_db():
    conn = sqlite3.connect("dbs/zillow.db")
    return conn


def insert_listing_record(conn, record: Dict[str, Union[str, int]]):
    """insert a record into the zillow_listings table

    Args:
        conn (sqlite connection): connection to zillow db
        record (Dict[str,Union[str,int]]): Dictionary representing the record to insert
    """
    with conn:
        c = conn.cursor()
        c.execute(
            """
                INSERT INTO zillow_listings VALUES
                (
                :url,
                :parcel_number,
                :address,
                :zip_code,
                :school_district,
                :list_price,
                :list_date,
                :bedrooms,
                :bathrooms_total,
                :bathrooms_full,
                :bathrooms_3_4,
                :bathrooms_1_2,
                :bathrooms_1_4,
                :basement,
                :new_construction,
                :year_built,
                :home_type,
                :stories,
                :total_interior_livable_area_sqft,
                :lot_size_acres,
                :region,
                :tax_assessed_value_dollars,
                :annual_tax_amount_dollars,
                :mls_id,
                :mlsstatus
                )
            """,
            record,
        )


def get_listing_by_url(conn: "SQLite connection", url: Dict[str, str]):
    """Collect records by URL

    Args:
        conn (sqlite connection): connection to zillow db
        url (Dict[str,str]): dictionary with key='url' and value=url string
    """
    c = conn.cursor()
    c.execute(
        """
            SELECT *
            FROM zillow_listings
            WHERE url=:url
        """,
        (url),
    )

    return c.fetchall()
