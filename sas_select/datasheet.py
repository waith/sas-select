# excel to sql database

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from . import db

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


def init_db():
    """Read excel file from gov website, check required columns exist, empty and repopulate database"""

    df = pd.read_excel(find_xl_url())
    populate_db_from_df(df)
