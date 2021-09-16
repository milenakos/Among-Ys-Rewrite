# this code isnt stolen from youtube tutorial, how would i do such a thing


import socket
import threading

HOST = '0.0.0.0'
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

def broadcast(message):
	for client in clients: 
		client.send(message)

def handle(client):
	while True:
		try:
			message = client.recv(1024)
			broadcast(message)
		except:
			index = clients.index(client)
			clients.remove(client)
			client.close()
			nickname = nicknames[index]
			print(f"User {nickname} left!")
			nicknames.remove(nickname)
			break

def receive():
	while True:
		client, address = server.accept()
		print(f"Connected with {str(address)}!")

		client.send("NICK".encode("utf-8"))
		nickname = client.recv(1024)
		decoden = nickname.decode("utf-8")

		clients.append(client)
		nicknames.append(decoden)

		print(f"Nickname of the client is {decoden}!")

		thread = threading.Thread(target=handle, args=(client,))
		thread.start()

receive()