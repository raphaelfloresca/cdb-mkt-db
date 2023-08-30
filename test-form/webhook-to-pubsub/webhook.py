import os
import sys
from flask import Flask, request
from google.cloud import pubsub_v1, secretmanager


# Get project name and store as an environment variable
project_name = 'marketing-bd-379302'
os.environ['PROJECT_NAME'] = project_name


# Get topic name and store as an environment variable
project_name = 'marketing-bd-379302'
topic_name = 'CDBContactFormEN'
os.environ['TOPIC_NAME'] = topic_name


# Get secret name and store as an environment variable
#secret_name = 'cdb_test_form_token'
#os.environ['SECRET_NAME'] = secret_name


# Get secret from secret manager
#def get_secret(project_id, secret_id, version_id):
#    # Returns secret payload from Cloud Secret Manager
#    client = secretmanager.SecretManagerServiceClient()
#    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
#    secret = client.access_secret_version(name=name)
#    return secret.payload.data.decode('UTF-8')
#os.environ['SECRET'] = get_secret(os.environ.get('PROJECT_NAME'), os.environ.get('SECRET_NAME', 'latest'), "latest")


# Flask app for webhook
app = Flask(__name__)


# Post requests to this endpoint publishes to Pub/Sub
@app.route('/', methods=['POST'])
def index():
    body = request.data

    # Check if request has valid auth token
    request_secret = request.headers['Secret']
    if request_secret != os.environ['SECRET']:
        return ('Unauthorized', 401)

    publish_to_pubsub(body)

    sys.stdout.flush()
    return ('', 204)


# Publishes the message to Cloud Pub/Sub
def publish_to_pubsub(msg):
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(
            os.environ.get('PROJECT_NAME'), os.environ.get('TOPIC_NAME')
        )

        # Pub/Sub data must be bytestring, attributes must be strings
        future = publisher.publish(topic_path, data=msg)

        exception = future.exception()
        if exception:
            raise Exception(exception)

        print(f'Published message: {future.result()}')

    except Exception as e:
        # Log any exceptions to stackdriver
        entry = dict(severity='WARNING', message=e)
        print(entry)



if __name__ == '__main__':
    PORT = int(os.getenv('PORT')) if os.getenv('PORT') else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host='127.0.0.1', port=PORT, debug=True)
