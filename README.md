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
```

# Полезные ресурсы для Python-разработчиков

## 1. Официальная документация Python
Ссылка: [https://docs.python.org/3/](https://docs.python.org/3/)

Описание:
Официальная документация Python – основной источник информации о языке. Здесь можно найти описание стандартной библиотеки, справочники по синтаксису и руководства по использованию различных возможностей языка.

Пример использования:
При возникновении вопросов о функциях стандартной библиотеки или новых возможностях Python можно обратиться к этому ресурсу.

---

## 2. Real Python
Ссылка: [https://realpython.com/](https://realpython.com/)

Описание:
Real Python предлагает качественные статьи, учебные пособия и курсы по Python. Ресурс особенно полезен для разработчиков любого уровня – от новичков до продвинутых пользователей.

Пример использования:
Изучение продвинутых техник Python, таких как асинхронное программирование, работа с API и лучшие практики написания кода.

---

## 3. Stack Overflow (раздел Python)
Ссылка: [https://stackoverflow.com/questions/tagged/python](https://stackoverflow.com/questions/tagged/python)

Описание:
Крупнейшее сообщество разработчиков, где можно найти решения различных проблем, связанных с Python. Вопросы и ответы ранжируются по популярности, а участники голосуют за лучшие решения.

Пример использования:
Если возникла ошибка в коде или требуется оптимизировать алгоритм, можно найти готовое решение или задать свой вопрос сообществу.

---

## 4. Python Package Index (PyPI)
Ссылка: [https://pypi.org/](https://pypi.org/)

Описание:
Официальный репозиторий пакетов Python, где можно найти и установить тысячи библиотек для различных задач – от обработки данных до веб-разработки.

Пример использования:
При необходимости использовать стороннюю библиотеку (например, requests для работы с HTTP-запросами) можно найти и установить её через PyPI.

---

## 5. Google Colab
Ссылка: [https://colab.research.google.com/](https://colab.research.google.com/)

Описание:
Google Colab – это онлайн-среда выполнения Jupyter Notebook, которая позволяет запускать Python-код в облаке без необходимости настройки локального окружения.

Пример использования:
Отлично подходит для работы с машинным обучением, анализа данных и быстрой проверки кода без установки Python на компьютер.

```python
# Обзор ключевых возможностей Python

# 1. List Comprehensions
# List comprehensions позволяют создавать списки в одной строке, упрощая код.
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
print(squares)  # [1, 4, 9, 16, 25]

# 2. F-Strings
# F-строки упрощают форматирование строк, делая код более читаемым.
name = "Alice"
age = 25
print(f"Меня зовут {name}, мне {age} лет.")

# 3. Dataclasses
# Dataclasses упрощают работу с объектами данных, автоматически генерируя методы.
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

p = Person("Bob", 30)
print(p)  # Person(name='Bob', age=30)
```


```python
# Мини-проект: Генерация списка квадратов чисел с помощью list comprehensions

def generate_squares(n):
    """Генерирует список квадратов чисел от 1 до n."""
    return [x**2 for x in range(1, n+1)]

if name == "main":
    num = int(input("Введите число: "))
    squares_list = generate_squares(num)
    print("Квадраты чисел:", squares_list)
```




















