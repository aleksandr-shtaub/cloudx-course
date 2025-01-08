import pytest
import respx
from fastapi.testclient import TestClient
from main import app, IMDS_URL


@pytest.fixture
def imds_api_mock():
    mock_router = respx.mock(base_url=IMDS_URL, assert_all_called=False)
    with mock_router:
        mock_router.put("/api/token", name="token").respond(text="mock-token")
        mock_router.get("/meta-data/placement/region", name="region").respond(text="us-east-1")
        mock_router.get("/meta-data/placement/availability-zone", name="az").respond(text="us-east-1a")

        yield mock_router


@pytest.fixture
def client(imds_api_mock):
    with TestClient(app) as test_client:
        yield test_client


def test_read_root(client, imds_api_mock):
    response = client.get("/")
    assert response.status_code == 200

    expected_data = {
        "region": "us-east-1",
        "availability-zone": "us-east-1a",
    }
    assert response.json() == expected_data


def test_imds_metadata_calls(client, imds_api_mock):
    client.get("/")

    token_call = imds_api_mock["token"]
    assert token_call.called

    key = "X-aws-ec2-metadata-token"

    region_call = imds_api_mock["region"]
    assert region_call.called
    assert region_call.calls[0].request.headers[key] == "mock-token"

    az_call = imds_api_mock["az"]
    assert az_call.called
    assert az_call.calls[0].request.headers[key] == "mock-token"
