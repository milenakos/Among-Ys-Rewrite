# this code isnt stolen from youtube tutorial, how would i do such a thing


import socket
import threading

HOST = '0.0.0.0'
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
			index = clients.index(client)
			clients.remove(client)
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