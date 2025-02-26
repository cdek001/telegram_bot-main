from token_generator import get_token
import requests
import json

url = "https://api.cdek.ru/v2/orders"
# Create the payload for the PATCH request
payload = {
    "requests": [
        {
            "request_uuid": "NEW_REQUEST_UUID",
            "type": "UPDATE",
            "state": "ACCEPTED",
            "date_time": new_delivery_date + "T12:00:00Z",
            "errors": [],
            "warnings": []
        }
    ]
}

# Set the headers for the request
headers = {
    'Authorization': f'Bearer {get_token()}',
    'Content-Type': 'application/json'
}

# Convert the payload to JSON
json_payload = json.dumps(payload)

# Send the PATCH request
response = requests.patch(url, headers=headers, data=json_payload)

# Check the response status code
if response.status_code == 200:
    print("Order updated successfully!")
else:
    print("Error updating order:", response.text)