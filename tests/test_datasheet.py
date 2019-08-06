from sas_select.datasheet import (find_xl_url, BASE_URL_STR, COLUMN_NAMES,
                                  GROUP_ID, SAS_CODE, COMPANY_CODE, BRAND_NAME, PRODUCT_DESCRIPTION, PACK_SIZE,
                                  MAXIMUM_QTY, PACK_PRICE, PACK_PREMIUM)
from sas_select import db
import os
import xlrd


def test_find_xl_url():
    url = find_xl_url()
    assert "full.xls" in url
    assert BASE_URL_STR in url


def cell_value(sheet, rx, cx):
    cell = sheet.cell(rx, cx)
    if cell is xlrd.empty_cell or cell.value == '':
        return None
    else:
        return cell.value


def populate_db_from_sheet(sheet):
    """Given excel sheet, check required columns exist, and if so, empty and repopulate database"""

    dct_index_of_heading = {}
    for cx in range(sheet.ncols):
        dct_index_of_heading[sheet.cell_value(0, cx)] = cx
    not_founds = []
    for expected in COLUMN_NAMES:
        if expected not in dct_index_of_heading:
            not_founds.append(expected)
    if not_founds:
        raise ValueError("Missing column", not_founds)
    db.empty_tbl_products()
    sas_db = db.get_db()
    cursor = sas_db.cursor()
    sql = """insert into tbl_products (ID, GroupID, SASCode, CompanyCode, BrandName, ProductDescription, PackSize, MaximumQty, PackPrice, PackPremium) 
    values (?,?,?,?,?,?,?,?,?,?)"""
    for rx in range(1, sheet.nrows):
        cursor.execute(sql,
                       (rx,
                        cell_value(sheet, rx, dct_index_of_heading[GROUP_ID]),
                        cell_value(sheet, rx, dct_index_of_heading[SAS_CODE]),
                        cell_value(sheet, rx, dct_index_of_heading[COMPANY_CODE]),
                        cell_value(sheet, rx, dct_index_of_heading[BRAND_NAME]),
                        cell_value(sheet, rx, dct_index_of_heading[PRODUCT_DESCRIPTION]),
                        cell_value(sheet, rx, dct_index_of_heading[PACK_SIZE]),
                        cell_value(sheet, rx, dct_index_of_heading[MAXIMUM_QTY]),
                        cell_value(sheet, rx, dct_index_of_heading[PACK_PRICE]),
                        cell_value(sheet, rx, dct_index_of_heading[PACK_PREMIUM]),
                        )
                       )
    sas_db.commit()


def test_populate_db_from_excel(app, client):
    with app.app_context():
        book = xlrd.open_workbook(os.path.join(os.path.dirname(__file__), "sas-schedule-test-full.xlsx"))
        populate_db_from_sheet(book.sheet_by_index(0))
        sas_db = db.get_db()
        count_products = sas_db.execute('select count(*) from tbl_products').fetchone()
        assert count_products['count(*)'] == 33  # there should be 33 records imported from spreadsheet
        entitlements = sas_db.execute('select MaximumQty from tbl_products').fetchall()
        for e in entitlements:
            assert "a" in e['MaximumQty'] or "m" in e['MaximumQty']
    response = client.post("/", data={'CompanyCode': '1', 'BrandName': ''})
    assert response.data.count(b'<tr>') <= 21  # search function should limit results to 20 (+ 1 header row)
