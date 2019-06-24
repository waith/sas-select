# excel to sql database

import pandas as pd
import sqlite3

df = pd.read_excel("sas-schedule-1-april-2019-full.xlsx", skiprows=0)

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
