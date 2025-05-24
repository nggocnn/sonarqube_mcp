import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
import requests
import logging
from unittest.mock import patch, Mock
from dotenv import load_dotenv
from src.client.client import SonarQubeClient

logging.basicConfig(level=logging.DEBUG)

load_dotenv()


@pytest.fixture(scope="module")
def good_client():
    good_client = SonarQubeClient(
        base_url=os.getenv("SONARQUBE_URL"),
        token=os.getenv("SONARQUBE_TOKEN"),
        organization=os.getenv("SONARQUBE_ORG", None),
    )

    good_client.validate_connection()
    return good_client


def test_validate_connection(good_client):
    result = good_client.validate_connection()
    assert isinstance(result, bool)
    assert good_client.connected == result
    assert good_client.connection_message


def test_get_system_health(good_client):
    result = good_client.get_system_health()
    assert isinstance(result, dict)
    assert "health" in result or "error" in result


def test_get_system_status(good_client):
    result = good_client.get_system_status()
    assert isinstance(result, dict)
    assert "status" in result or "error" in result


def test_system_ping(good_client):
    result = good_client.system_ping()
    assert isinstance(result, bool)
    assert result is True


def test_list_projects(good_client):
    result = good_client.list_projects()
    assert isinstance(result, dict)
    assert "components" in result or "error" in result


def test_list_user_projects(good_client):
    result = good_client.list_user_projects()
    assert isinstance(result, dict)
    assert "projects" in result or "error" in result


def test_get_metrics_type(good_client):
    result = good_client.get_metrics_type()
    assert isinstance(result, dict)
    assert "types" in result or "error" in result


def test_get_quality_gates(good_client):
    result = good_client.get_quality_gates()
    assert isinstance(result, dict)
    assert "qualitygates" in result or "error" in result


@pytest.fixture
def bad_client():
    return SonarQubeClient(base_url="http://fake-url", token="fake-token")


def test_http_error(bad_client):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=Mock(status_code=401)
    )

    with patch("requests.request", return_value=mock_response):
        result = bad_client._SonarQubeClient__make_request("/bad", health_check=False)
        assert result["error"] == "HTTP 401"
        assert "details" in result


def test_json_decode_error(bad_client):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
        "Expecting value", "doc", 0
    )

    with patch("requests.request", return_value=mock_response):
        result = bad_client._SonarQubeClient__make_request(
            "/bad-json", health_check=False
        )
        assert result["error"] == "JSON serialization error"
        assert "details" in result


def test_request_exception(bad_client):
    with patch(
        "requests.request",
        side_effect=requests.exceptions.RequestException("Connection error"),
    ):
        result = bad_client._SonarQubeClient__make_request(
            "/request-ex", health_check=False
        )
        assert result["error"] == "Request failed"
        assert "Connection error" in result["details"]


def test_value_error(bad_client):
    with patch("requests.request", side_effect=ValueError("Bad input")):
        result = bad_client._SonarQubeClient__make_request(
            "/value-error", health_check=False
        )
        assert result["error"] == "Invalid request"
        assert "Bad input" in result["details"]
