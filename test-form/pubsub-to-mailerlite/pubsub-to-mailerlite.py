import base64
import json
import os
import sys
import time
import urllib
import mailerlite as MailerLite
from flask import Flask, request
from google.cloud import secretmanager


# Get secret name and store as an environment variable
#secret_name = 'mailerlite_api_token'
#os.environ['SECRET_NAME'] = secret_name


# Get secret from secret manager
#def get_secret(project_id, secret_id, version_id):
#    # Returns secret payload from Cloud Secret Manager
#    client = secretmanager.SecretManagerServiceClient()
#    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
#    secret = client.access_secret_version(name=name)
#    return secret.payload.data.decode('UTF-8')
#os.environ['API_KEY'] = get_secret(os.environ.get('PROJECT_NAME'), os.environ.get('SECRET_NAME', 'latest'), "latest")


# Instantiate MailerLite client
ml_client = MailerLite.Client({'api_key': os.environ.get('API_KEY')})


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
    add_contact_to_mailerlite(data)

    print(data)

    sys.stdout.flush()
    return ("", 204)


def add_contact_to_mailerlite(data):
    response = ml_client.subscribers.create(data['your-email'])


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8082

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
