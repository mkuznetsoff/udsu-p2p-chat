import asyncio
from p2pd import P2PNode

async def main():
    # Инициализация узла
    node = await P2PNode()
    
    # Регистрация псевдонима
    nickname = await node.nickname("user2")
    print(f"Зарегистрирован как: {nickname}")
    
    # Получение списка доступных псевдонимов
    peers = await node.lookup_nicknames()
    print("Доступные пользователи:")
    for peer in peers:
        print(f"- {peer}")
    
    # Подключение к выбранному пользователю
    target_nick = input("Введите псевдоним для подключения: ")
    pipe = await node.connect(target_nick)
    print(f"Подключено к {target_nick}")
    
    # Отправка сообщений
    while True:
        msg = input("Введите сообщение: ")
        await pipe.send(msg.encode())

# Запуск клиента
asyncio.run(main())
