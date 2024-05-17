import base64
import json
import os
import sys
import time
import urllib

from flask import Flask, request
from google.cloud import bigquery


# Get dataset name and store as an environment variable
dataset_name = 'marketing_funnel'
os.environ['DATASET'] = dataset_name


# Get table name and store as an environment variable
table_name = 'cf7_test_form'
os.environ['TABLE'] = table_name


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

    # Insert row into bigquery
    insert_row_into_bigquery(data)

    print(data)

    sys.stdout.flush()
    return ("", 204)


def insert_row_into_bigquery(data):
    # Set up bigquery instance
    client = bigquery.Client()

    table_id = 'marketing-bd-379302.marketing_funnel.cf7_test_form'

    # Insert row
    row_to_insert = [
        {
            'email': data["your-email"],
            'message': data["your-message"],
            'name': data["your-name"],
            'subject': data["your-subject"],
            'time': time.time(),
        }
    ]
    bq_errors = client.insert_rows_json(table_id, row_to_insert)

    # If errors, log to Stackdriver
    if bq_errors:
        entry = {
            "severity": "WARNING",
            "msg": "Row not inserted.",
            "errors": bq_errors,
            "row": row_to_insert,
        }
        print(json.dumps(entry))


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8081

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
