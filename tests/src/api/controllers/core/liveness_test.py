def test_liveness(test_client):
    """
    Test if the application is up and runnig
    """

    response = test_client.get("/-/healthz")

    assert response.status_code == 200
    assert response.json() == {"statusOk": True}
