import os
from google.cloud import pubsub_v1

credentials_path = './marketing-bd-379302-853ba6fb673e.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/marketing-bd-379302/topics/CDBContactFormEN'

data = 'This is a test message'
data = data.encode('utf-8')

future = publisher.publish(topic_path, data)
print(f'published message id {future.result()}')
