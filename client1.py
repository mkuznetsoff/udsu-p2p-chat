import socket
import threading
import sys

server = ('0.0.0.0', 3000)

print('connecting to a server')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind( ('0.0.0.0', 3002) )
sock.sendto(b'0', server)

while True:
    data = sock.recv(1024).decode()

    if data.strip() == 'ready':
        print('checked in with server, waiting')
        break

data = sock.recv(1024).decode()
ip, sport, dport = data.split(' ')
sport = int(sport)
dport = int(dport)

print('\ngot peer')
print('   ip:             {}'.format(ip))
print('   source port:    {}'.format(sport))
print('   dest port:      {}\n'.format(dport))


#punch hole
print('punching hole')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind( ('0.0.0.0', sport) )
sock.sendto(b'0', (ip, dport))

print('ready to exchange msgs\n')

def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind( ('0.0.0.0', sport) )

    while True:
        data = sock.recv(1024)
        print('\npeer: {}\n> '.format(data.decode()), end='')

listener = threading.Thread(target=listen, daemon=True);
listener.start()

# send msgs
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind( ('0.0.0.0', dport) )

while True:
    msg = input('> ')
    sock.sendto(msg.encode(), (ip, sport))
