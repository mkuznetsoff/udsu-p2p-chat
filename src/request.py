import requests

url = "https://jsonplaceholder.typicode.com/users/1"

response = requests.get(url)
print(response.json()) 
print()
updated_user = {    
    "name": "Updated User",
    "username": "updateduser123",
}

response = requests.put(url, json=updated_user)
print(response.json()) 


