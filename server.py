# License for this file:
#
#            DO WHAT THE HECK YOU WANT TO PUBLIC LICENSE
#
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE HECK YOU WANT TO.


import socket
import threading

HOST = ''
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []

def broadcast(message):
	for client in clients: 
		client.send(message)

def handle(client):
	while True:
		try:
			message = client.recv(4096)
			broadcast(message)
		except ConnectionResetError:
			clients.pop(index)
			client.close()
			break

def receive():
	while True:
		client, address = server.accept()
		print(f"Connected with {str(address)}!")

		clients.append(client)

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()

receive()
