import os
from google.cloud import pubsub_v1

credentials_path = './marketing-bd-379302-853ba6fb673e.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

timeout = 5.0

subscriber = pubsub_v1.SubscriberClient()
subscription_path = 'projects/marketing-bd-379302/subscriptions/CDBContactFormEN-sub'

def callback(message):
    print(f'Received message: {message}')
    print(f'data: {message.data}')
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f'Listening for messages on {subscription_path}')

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
        streaming_pull_future.result()
