# excel to sql database

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from . import db
from datetime import datetime
import re

GROUP_ID = 'Group ID'
SAS_CODE = 'SAS Code'
COMPANY_CODE = 'Company Code'
BRAND_NAME = 'Brand Name'
PRODUCT_DESCRIPTION = 'Product Description'
PACK_SIZE = 'Pack Size'
MAXIMUM_QTY = 'Maximum Qty\nMonthly (m)\nAnnual (a)'
PACK_PRICE = 'Pack Price'
PACK_PREMIUM = 'Pack Premium'

COLUMN_NAMES = (GROUP_ID,
                SAS_CODE,
                COMPANY_CODE,
                BRAND_NAME,
                PRODUCT_DESCRIPTION,
                PACK_SIZE,
                MAXIMUM_QTY,
                PACK_PRICE,
                PACK_PREMIUM,
                )

BASE_URL_STR = "https://www.health.gov.au/internet/main/publishing.nsf/Content/"
PAGE_URL_STR = "health-stoma-schedule-index.htm"


def find_xl_url():
    """scrape government web page for url containing full.xls"""

    page = urlopen(BASE_URL_STR + PAGE_URL_STR)
    soup = BeautifulSoup(page, features="html.parser")
    div_read = soup.find(id='read')
    lst_a = div_read.find_all("a")
    if len(lst_a) == 0:
        raise IOError("Could not find any hyperlinks on SAS schedule web page " + BASE_URL_STR + PAGE_URL_STR)
    for a in lst_a:
        href = a.get('href')
        if 'full.xls' in href:
            return BASE_URL_STR + href
    raise IOError("Could not find url for '*full.xls' on SAS schedule web page " + BASE_URL_STR + PAGE_URL_STR)


def populate_db_from_df(df):
    """Given dataframe df, check required columns exist, and if so, empty and repopulate database"""

    not_founds = []
    for expected in COLUMN_NAMES:
        if expected not in df.columns:
            not_founds.append(expected)
    if not_founds:
        raise ValueError("Missing column", not_founds)
    db.empty_tbl_products()
    sas_db = db.get_db()
    cursor = sas_db.cursor()
    sql = """insert into tbl_products (ID,GroupID, SASCode, CompanyCode, BrandName, ProductDescription, PackSize, MaximumQty, PackPrice, PackPremium) 
    values (?,?,?,?,?,?,?,?,?,?)"""
    for index, row in df.iterrows():
        cursor.execute(sql, (index,
                             row[GROUP_ID],
                             row[SAS_CODE],
                             row[COMPANY_CODE],
                             row[BRAND_NAME],
                             row[PRODUCT_DESCRIPTION],
                             row[PACK_SIZE],
                             row[MAXIMUM_QTY],
                             row[PACK_PRICE],
                             row[PACK_PREMIUM]))
    sas_db.commit()


def fetch_data():
    """Read excel file from gov website, check required columns exist, empty and repopulate database"""

    scrape_page, last_reading = need_scrape()

    if scrape_page:
        new_url = find_xl_url()
        regex = r'([^\/]+)(?=\.\w+$)'
        # This regex is to find excel file name from end of url excluding final .xls or .xlsx
        # ([^\/]+) : Find group of characters not including forward slash
        # (?=.\w+$) : look ahead to find a dot, followed by a word, followed by end of line and exclude this whole part.
        file_name = re.search(regex, new_url).group(0)
        sas_db = db.get_db()

        if last_reading and new_url == last_reading['FileURL']:
            # Update scrape date
            sas_db.execute('UPDATE tbl_data_reading SET LastScrapeDate = ? WHERE ID = ?;', (datetime.now(), last_reading['ID']))
            print('Scrape date updated')
            message = "No new data to update"

        else:
            print('New URL found:', new_url)
            # Read new file
            df = pd.read_excel(new_url)
            populate_db_from_df(df)
            # Insert new data reading info
            sas_db.execute('INSERT INTO tbl_data_reading (FileURL, FileName, ReadDate, LastScrapeDate) values (?, ?, ?, ?);', (new_url, file_name, datetime.now(), datetime.now()))
            print('Updated with', new_url)
            message = "Product data was updated with " + file_name

        sas_db.commit()

    else:
        # Don't scrape
        message = "Last scrape was today"

    return message


def need_scrape():

    last_reading = find_last_reading()

    if last_reading:
        if last_reading['LastScrapeDate']:
            # Found last scrape date
            today_date = datetime.now().date()
            last_scrape_date = last_reading['LastScrapeDate'].date()
            diff = today_date - last_scrape_date
            days_ago = diff.days
            print('Last scrape was', days_ago, 'days ago')
            if days_ago > 0:
                # Last scrape was at least yesterday
                scrape_page = True
            else:
                # Last scrape was today
                scrape_page = False
        else:
            # Force new scrape because LastScrapeDate is not available
            print('No scrape date found')
            scrape_page = True
    else:
        # Empty table
        print('No previous readings found')
        scrape_page = True

    return scrape_page, last_reading


def find_last_reading():
    sas_db = db.get_db()
    last_reading = sas_db.execute('SELECT * FROM tbl_data_reading ORDER BY ReadDate DESC LIMIT 1;').fetchone()
    return last_reading


def find_last_file_name():
    last_reading = find_last_reading()
    if last_reading:
        return last_reading['FileName']
    else:
        return None
