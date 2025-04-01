import socket

server_ip = '192.168.150.139'
server_port = 3000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = "Hello from Linux!"

s.sendto(message.encode(), (server_ip, server_port))
s.close()

