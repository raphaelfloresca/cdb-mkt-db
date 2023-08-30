import base64
import json
import os
import sys
import time
import urllib
import mailerlite as MailerLite
import requests
from flask import Flask, request
from google.cloud import secretmanager


# Get secret from secret manager
#def get_secret(project_id, secret_id, version_id):
#    # Returns secret payload from Cloud Secret Manager
#    client = secretmanager.SecretManagerServiceClient()
#    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
#    secret = client.access_secret_version(name=name)
#    return secret.payload.data.decode('UTF-8')
#os.environ['API_KEY'] = get_secret(os.environ.get('PROJECT_NAME'), os.environ.get('SECRET_NAME', 'latest'), "latest")


app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()

    # Check if valid JSON
    if not envelope:
        raise Exception("Expecting JSON payload")
    # Check if valid pub/sub message
    if "message" not in envelope:
        raise Exception("Not a valid Pub/Sub Message")

    msg = envelope["message"]
    data = json.loads(base64.b64decode(msg["data"]).decode("utf-8").strip())

    # Insert row into MailerLite
    add_contact_to_box(data, add_box_to_streak(data))

    print(data)

    sys.stdout.flush()
    return ("", 204)


# Add data to Streak
streak_headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "authorization": "Basic {}".format(str(os.environ.get('API_KEY')))
}


def add_box_to_streak(data, headers=streak_headers):
    url = "https://api.streak.com/api/v2/pipelines/agxzfm1haWxmb29nYWVyNAsSDE9yZ2FuaXphdGlvbiINY3JlYXRvcmRiLmFwcAwLEghXb3JrZmxvdxiAgOb55Z6xCAw/boxes"
    payload = { "name": data['your-name'] }
    response = requests.post(url, json=payload, headers=headers)
    response_dict = response.json()

    return response.json()['boxKey']


def add_contact_to_box(data, box_key, headers=streak_headers):
    # Create or get contact
    contact_url = "https://api.streak.com/api/v2/teams/agxzfm1haWxmb29nYWVyEQsSBFRlYW0YgIDGzpj8xwoM/contacts/?getIfExisting=true"
    contact_payload = { "emailAddresses": [data['your-email']] }
    contact_response = requests.post(contact_url, json=contact_payload, headers=headers)
    contact_response_dict = contact_response.json()

    # Update box with contact
    box_url = "https://api.streak.com/api/v1/boxes/{}".format(str(box_key))
    box_payload = { "contacts": [
        {
            "isStarred": True,
            "key": contact_response_dict['key']
        }
    ] }
    box_response = requests.post(box_url, json=box_payload, headers=headers)

    return 'Added contact to box'


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8083

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
