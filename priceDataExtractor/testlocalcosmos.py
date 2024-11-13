import requests

response = requests.get("https://localhost:8081/_explorer/index.html", verify=False)
print("Status Code:", response.status_code)