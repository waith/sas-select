from sas_select import create_app


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


