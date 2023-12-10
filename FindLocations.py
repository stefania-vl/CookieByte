import requests

# The API endpoint
base_url = "https://public.opendatasoft.com"
url_header = "/api/explore/v2.1/catalog/datasets/geonames-all-cities-with-a-population-500/records?limit=20&refine=timezone%3A%22Europe%2FBucharest%22&refine=country%3A%22Romania%22&refine=city%3A%22Bucharest%22"
url = base_url + url_header
# A GET request to the API
response = requests.get(url)

# Print the response
response_json = response.json()
print(response_json)