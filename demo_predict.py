import time
import requests

url = 'http://127.0.0.1:5000/predict'
payload = {'text': 'I loved this movie, it was fantastic!'}

# Wait for server to be ready
for i in range(10):
    try:
        r = requests.post(url, json=payload, timeout=3)
        print('status', r.status_code)
        print(r.json())
        break
    except Exception as e:
        print('Waiting for server...', e)
        time.sleep(1)
else:
    print('Failed to contact server after retries')
