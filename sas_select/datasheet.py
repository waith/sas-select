# excel to sql database

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import datetime
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


def init_db():
    base_url_str = "https://www.health.gov.au/internet/main/publishing.nsf/Content/"
    page_url_str = "health-stoma-schedule-index.htm"

    page = urlopen(base_url_str + page_url_str)

    soup = BeautifulSoup(page, features="html.parser")

    div_read = soup.find(id='read')

    lst_a = div_read.find_all("a")
    if len(lst_a) == 0:
        raise IOError("Could not find any hyperlinks on SAS Utilisition web page " + base_url_str + page_url_str)
    xl_url_str = None
    for a in lst_a:
        href = a.get('href')
        if 'xls' in href:
            xl_url_str = base_url_str + href
            break

    if xl_url_str is None:
        raise IOError("Could not find url for xls for any year between 2012 and " + str(datetime.date.today().year))

    df = pd.read_excel(xl_url_str)

    not_founds = []
    for expected in COLUMN_NAMES:
        if expected not in df.columns:
            not_founds.append(expected)

    if not_founds:
        raise ValueError("Missing column", not_founds)

    sas_db = db.get_db()

    cursor = sas_db.cursor()

    cursor.execute("drop table if exists tbl_products")

    cursor.execute("""create table tbl_products (
        ID integer primary key,
        GroupID varchar,
        SASCode varchar,
        CompanyCode varchar,
        BrandName varchar,
        ProductDescription varchar,
        PackSize numeric,
        MaximumQty varchar,
        PackPrice numeric,
        PackPremium numeric
    )""")
    sas_db.commit()

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

    sql = "select * from tbl_products limit 20"
    records = cursor.execute(sql).fetchall()

    for record in records:
        print(dict(record))
