# tests/test_server.py

from flask import Flask


def test_app_exists(app) -> None:
    """Test that the Flask app instance is created successfully."""
    assert app is not None, "App instance should not be None."
    assert isinstance(app, Flask), "App should be an instance of Flask."


def test_app_config(app) -> None:
    """Test basic configuration settings of the Flask app.
    Adjust the assertions based on your actual configuration.
    """
    # Example: Check if testing mode is on
    assert app.config["TESTING"] is True, "TESTING config should be True."

    # Example: Check if a specific configuration key exists
    assert (
        "SQLALCHEMY_DATABASE_URI" in app.config
    ), "SQLALCHEMY_DATABASE_URI should be set."


def test_app_routes(client) -> None:
    """Test that the health check endpoint is working.
    Assumes that you have a '/service/auth/health' endpoint as defined earlier.
    """
    response = client.get("/service/auth/health")
    assert response.status_code == 200, "Health endpoint should return status code 200."
    assert response.get_json() == {
        "status": "OK"
    }, "Health endpoint should return {'status': 'OK'}."
