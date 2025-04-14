import requests 
import json 

number = "P04637"
url = f"https://rest.uniprot.org/uniprotkb/{number}.json"

response = requests.get(url)
data = response.json()

with open("P04637.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"JSON file saved as P04637.json")

