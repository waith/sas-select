from sas_select import create_app
import pytest


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


@pytest.mark.parametrize(
    ("url", "tpl_message"),
    (
            ("/product/798",  (b"2 pack(s) per month", b"2 packs per month")),      # '3133','Hollister Karaya 5','30','60m'
            ("/product/844",  (b"1 pack(s) per month", b"1 pack per month")),       # '926-10','Dansac NovaLife 1 Piece Open Flat','30','30m'
            ("/product/1001", (b"3 pack(s) per month", b"3 packs per month")),      # 'BD13W','Ainscorp Salts Confidence Be','10','30m'
            ("/product/3068", (b"12 pack(s) per year", b"12 packs per year")),      # 'CS10-15','Halyard Australia Pty Ltd Corstop Ace Stoma Stopper','1','12a'
            ("/product/3094", (b"1 pack(s) per month", b"1 pack per month")),       # '12834','Coloplast Alterna Sleeve','30','50m'
            ("/product/3097", (b"1 pack(s) per year",  b"1 pack per year")),        # '12820','Coloplast Alterna Pressure Plate','5','5a'
            ("/product/3102", (b"2 pack(s) per month", b"2 packs per month")),      # '950-20','Dansac Irrigation Sleeves','20','50m'
            ("/product/3180", (b"4 pack(s) per month", b"4 packs per month")),      # '4031000','Wellspect LoFric Intermittent Catheters - Nelaton','30','120m'
            ("/product/3248", (b"1 pack per 2 years", )),                           # '8770','Hollister Clamps','20','10a'
            ("/product/3253", (b"1 pack per 2 months", )),                          # '37443','ConvaTec ConvaCare','100','60m'
            ("/product/3254", (b"1 pack(s) per month", b"1 pack per month")),       # '403100','Smith & Nephew Remove','50','60m'
            ("/product/3546", (b"1 pack per 6 months", )),                          # '9431-30','Hollister T-Tap Night Drainage Collector','30','5m'
            ("/product/3547", (b"0.5 pack(s) per month", b"0.5 packs per month")),  # '28300','Omnigon Bbraun Urimed Bag 2L','10','5m'
    )
)
def test_pack_entitlement(client, url, tpl_message):
    response = client.get(url)
    assert any((m in response.data for m in tpl_message))


