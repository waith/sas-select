# excel to sql database

import sqlite3

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import datetime

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

df = pd.read_excel(xl_url_str, skiprows=0)

db = sqlite3.connect(
    database='db_products.sqlite',
    detect_types=sqlite3.PARSE_DECLTYPES
)

db.row_factory = sqlite3.Row

cursor = db.cursor()

cursor.execute("drop table if exists tbl_products")

cursor.execute("""create table tbl_products (
    ID integer primary key,
    GroupID varchar,
    SASCode varchar,
    CompanyCode varchar,
    BrandName varchar,
    ProductDescription varchar,
    MaximumQty varchar,
    PackSize numeric,
    PackPrice numeric,
    PackPremium numeric
)""")
db.commit()

sql = """insert into tbl_products (ID,GroupID, SASCode, CompanyCode, BrandName, ProductDescription, MaximumQty, PackSize, PackPrice, PackPremium) 
values (?,?,?,?,?,?,?,?,?,?)"""

for index, row in df.iterrows():
    cursor.execute(sql,(index, row['Group ID'], row['SAS Code'], row['Company Code'], row['Brand Name'], row['Product Description'], row['Pack Size'], row['Maximum Qty\nMonthly (m)\nAnnual (a)'], row['Pack Price'], row['Pack Premium']))

db.commit()

sql = "select * from tbl_products limit 20"
records = cursor.execute(sql).fetchall()

for record in records:
    print(dict(record))
