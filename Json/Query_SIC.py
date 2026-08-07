import requests

url = "https://data.sec.gov/submissions/CIK0001045810.json"

headers = {"User-Agent": "your_name your_email@example.com"}

data = requests.get(url, headers=headers).json()

print(data["name"])
print(data["sic"])
print(data["sicDescription"])