#code nicked from https://www.youtube.com/watch?v=Ar94t2XhKzM, no need to reinvent the wheel here
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))

server.listen()

client, addr = server.accept()

done = False

while not done:
    msg = client.recv(2048).decode('utf-8')
    print("User Input: "+msg)
    client.send(input().encode('utf-8'))