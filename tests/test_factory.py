from sas_select import create_app
import pytest
from bs4 import BeautifulSoup


def test_config():
    """Test create_app without passing test config"""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_empty_search(client):
    response = client.post("/", data={'CompanyCode': '', 'BrandName': ''})
    assert b'<table>' not in response.data


def test_exact_match(client):
    response = client.post("/", data={'CompanyCode': '1001', 'BrandName': ''})
    assert response.data.count(b'<tr>') == 2


def test_like_match(client):
    response = client.post("/", data={'CompanyCode': '28300', 'BrandName': ''})
    assert response.data.count(b'<tr>') == 3
    response = client.post("/", data={'CompanyCode': '100', 'BrandName': ''})
    assert response.data.count(b'<tr>') == 7


def test_brand_match(client):
    response = client.post("/", data={'CompanyCode': '28300', 'BrandName': 'Omnigon Bbraun Urimed Bag 2L'})
    assert response.data.count(b'<tr>') == 2
    response = client.post("/", data={'CompanyCode': '', 'BrandName': 'Omnigon Bbraun Urimed Bag 2L'})
    assert response.data.count(b'<tr>') == 2


@pytest.mark.parametrize(
    ("url", "tpl_message"),
    (
            ("/product/798",  ("2 pack(s) per month", "2 packs per month")),      # '3133','Hollister Karaya 5','30','60m'
            ("/product/844",  ("1 pack(s) per month", "1 pack per month")),       # '926-10','Dansac NovaLife 1 Piece Open Flat','30','30m'
            ("/product/1001", ("3 pack(s) per month", "3 packs per month")),      # 'BD13W','Ainscorp Salts Confidence Be','10','30m'
            ("/product/3068", ("12 pack(s) per year", "12 packs per year")),      # 'CS10-15','Halyard Australia Pty Ltd Corstop Ace Stoma Stopper','1','12a'
            ("/product/3094", ("1 pack(s) per month", "1 pack per month")),       # '12834','Coloplast Alterna Sleeve','30','50m'
            ("/product/3097", ("1 pack(s) per year",  "1 pack per year")),        # '12820','Coloplast Alterna Pressure Plate','5','5a'
            ("/product/3102", ("2 pack(s) per month", "2 packs per month")),      # '950-20','Dansac Irrigation Sleeves','20','50m'
            ("/product/3180", ("4 pack(s) per month", "4 packs per month")),      # '4031000','Wellspect LoFric Intermittent Catheters - Nelaton','30','120m'
            ("/product/3248", ("1 pack per 2 years", )),                          # '8770','Hollister Clamps','20','10a'
            ("/product/3253", ("1 pack per 2 months", )),                         # '37443','ConvaTec ConvaCare','100','60m'
            ("/product/3254", ("1 pack(s) per month", "1 pack per month")),       # '403100','Smith & Nephew Remove','50','60m'
            ("/product/3546", ("1 pack per 6 months", )),                         # '9431-30','Hollister T-Tap Night Drainage Collector','30','5m'
            ("/product/3547", ("0.5 pack(s) per month", "0.5 packs per month")),  # '28300','Omnigon Bbraun Urimed Bag 2L','10','5m'
    )
)
def test_pack_entitlement(client, url, tpl_message):
    response = client.get(url)
    soup = BeautifulSoup(response.data, features="html.parser")
    pe = soup.find(id='pack_entitlement')
    assert any((m in pe.string for m in tpl_message))
