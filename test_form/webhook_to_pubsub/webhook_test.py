import webhook

import mock
import pytest
import os


# Set secret to dummy value for testing
os.environ['SECRET'] = 'foo'


# Set up client
@pytest.fixture
def client():
    webhook.app.testing = True
    return webhook.app.test_client()

# Test whether sending an empty payload leads to an error
def test_empty_payload(client):
    with pytest.raises(Exception) as e:
        client.post("/")


# Test whether posting with an invalid token leads to an error
def test_unverified_signature(client):
    client.post(
        "/",
        headers={
            "Content-Type": "application/json",
            "Secret": "foobar",
        },
    )

    assert 'Unauthorized'


# Tests whether posting with a valid token is successful
@mock.patch("webhook.publish_to_pubsub", mock.MagicMock(return_value=True))
def test_verified_signature(client):
    r = client.post("/", headers={"Content-Type": "application/json", "Secret": "foo"} )
    assert r.status_code == 204


# Test post to Pub/Sub
def test_data_sent_to_pubsub(client):
    webhook.publish_to_pubsub = mock.MagicMock(return_value=True)
    r = client.post("/", data='Hello', headers={"Content-Type": "application/json", "Secret": "foo"})
    webhook.publish_to_pubsub.assert_called_with(b"Hello")
    assert r.status_code == 204
