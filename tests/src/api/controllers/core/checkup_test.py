def test_checkup(test_client):
    """
    Test the availability of all the service's dependencies
    """

    response = test_client.get("/-/check-up")

    assert response.status_code == 200
    assert response.json() == {"statusOk": True}
