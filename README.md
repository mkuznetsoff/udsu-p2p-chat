# udsu-p2p-chat
A secure and anonymous P2P messaging app with encryption and cross-platform support 🐍🐍🐍
![](src/P2P-чат-P2P-чат.png)
![](src/document.jpg)
```
import qrcode

# Данные, которые будут закодированы в QR-код
data = ""

# Создание QR-кода
qr = qrcode.QRCode(
    version=1,  # Версия QR-кода (1-40, None для автоматического определения)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Уровень коррекции ошибок (L, M, Q, H)
    box_size=10,  # Размер каждого "пикселя" QR-кода
    border=4,  # Толщина границы вокруг QR-кода
)

qr.add_data(data)
qr.make(fit=True)

# Создание изображения QR-кода
img = qr.make_image(fill_color="black", back_color="white")

# Сохранение изображения в файл
img.save("exampleee.png")

print("QR-код успешно создан и сохранен в файл example.png")
```
![](example.png)


















