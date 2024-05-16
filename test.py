import requests

# URL of the FastAPI server
base_url = "https://royribaud.onrender.com"
base_url = "https://0.0.0.0"
# Data to be sent in the PUT request
item_data = {
    "name": "Test Item",
    "price": 15.99,
    "is_offer": True
}

# The item ID to be used
item_id = 1

# PUT request to update/create the item
put_url = f"{base_url}:5555/{item_id}"

print(put_url)
response_put = requests.put(put_url, json=item_data)

if response_put.status_code == 200:
    print("PUT request successful")
    print("Response:", response_put.json())
else:
    print("PUT request failed")
    print("Status code:", response_put.status_code)
    print("Response:", response_put.text)

# GET request to retrieve the item
get_url = f"{base_url}:5555/{item_id}"
response_get = requests.get(get_url)

if response_get.status_code == 200:
    print("GET request successful")
    print("Response:", response_get.json())
else:
    print("GET request failed")
    print("Status code:", response_get.status_code)
    print("Response:", response_get.text)
