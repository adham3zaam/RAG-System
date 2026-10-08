
import requests


url = "http://127.0.0.1:5000/ask"

data = {
    "question": "What is artificial intelligence?"
}

response = requests.post(
    url,
    json=data
)

print("Status Code:")
print(response.status_code)

print("\nResponse:")
print(response.json())

