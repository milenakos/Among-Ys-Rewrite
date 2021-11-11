import socket
import threading

PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', PORT))

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
			print(f"Disconnected with {str(client)}!")
			clients.remove(client)
			client.close()
			break

def receive():
	while True:
		client, _ = server.accept()
		print(f"Connected with {str(client)}!")

		clients.append(client)

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()

receive()
