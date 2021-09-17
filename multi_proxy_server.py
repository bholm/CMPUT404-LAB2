#!/usr/bin/env python3
import socket
import sys
import time
from multiprocessing import Process

# define address & buffer size
HOST = ""
PORT = 8001
BUFFER_SIZE = 1024

# get host information
def get_remote_ip(host):
    print(f'Getting IP for {host}')
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting.')
        sys.exit()
    print(f'IP address of {host} is {remote_ip}')
    return remote_ip

# send data to server
def handle_request(serversocket, payload, conn):
    print("Sending payload")
    try:
        serversocket.sendall(payload)
    except socket.error:
        print("Send failed")
        sys.exit()
    print("Payload sent successfully")
    serversocket.shutdown(socket.SHUT_WR)
                
    data = serversocket.recv(BUFFER_SIZE)
    print(f"Sending received data {data} to client")
    # send data back
    conn.send(data)

def main():
    host = "www.google.com"
    port = 80

    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_start:
        print("Starting proxy server")
        # allow reused addresss, bind, and set to listening mode
        proxy_start.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_start.bind((HOST, PORT))
        proxy_start.listen(1)

        while True:
            #connect proxy_start
            conn, addr = proxy_start.accept()
            print("Connected by", addr)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_end:
                print(f'Connecting to {host}')
                remote_ip = get_remote_ip(host)

                # connect proxy_end
                proxy_end.connect((remote_ip, port))

                # send data
                send_full_data = conn.recv(BUFFER_SIZE)
                p = Process(target=handle_request, args=(proxy_end, send_full_data, conn))
                p.daemon = True
                p.start()
                print("Started process", p)

        conn.close()

if __name__ == "__main__":
    main()
