# udsu-p2p-chat
A secure and anonymous P2P messaging app with encryption and cross-platform support 🐍🐍🐍
![Демо](src/P2P-чат-P2P-чат.png)
![Демо](src/document.jpg)
```python
#src/request.py
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
 
#WITH THIS CODE WE GOT
{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz",
  "address": {
    "street": "Kulas Light",
    "suite": "Apt. 556",
    "city": "Gwenborough",
    "zipcode": "92998-3874",
    "geo": {
      "lat": "-37.3159",
      "lng": "81.1496"
    }
  },
  "phone": "1-770-736-8031 x56442",
  "website": "hildegard.org",
  "company": {
    "name": "Romaguera-Crona",
    "catchPhrase": "Multi-layered client-server neural-net",
    "bs": "harness real-time e-markets"
  }
}
