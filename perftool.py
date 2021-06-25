#!/usr/bin/env python

import time
import socket
import sys
import argparse
from random import randint
import statistics as st

backlog = 5

def read_args():
    """Read the necessary entries to run the program.

        Utilization
        ----------
        read_args()
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', action="store_true", dest="client")
    parser.add_argument('-s', action="store_true", dest="server")
    parser.add_argument('-tcp', action="store_true", dest="tcp")
    parser.add_argument('-udp', action="store_true", dest="udp")
    parser.add_argument('-port', action="store", dest="port", type=int, required=True)
    parser.add_argument('-a', action="store", dest="address", type=str, required=False)
    parser.add_argument('-w', action="store", dest="interval", type=str, required=False)
    parser.add_argument('-n', action="store", dest="num", type=int, required=False)
    parser.add_argument('-b', action="store", dest="buffer", type=int, required=False)
    args = parser.parse_args()
    if (args.client and args.server) or (args.tcp and args.udp):
        print("Invalid args")
        sys.exit()
    return parser.parse_args()

def tcp_server(port, address, buffer):
    """Create a socket TCP echo server to receive packets from client.

        Parameters
        ----------
        port : int, required
            The port the server will be listening on.

        address: str, required
            The server IP address.

        buffer: int, required
            Buffer size for receiving data.

        Utilization
        ------
        tcp_server(24, 10.0.1.10, 1024)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (address, port)

        # Starting up echo server
        sock.bind(server_address)
        sock.listen(backlog)
        
        client, address = sock.accept()
        with client:
            # Connected by some client
            while True:
                # Waiting to receive data from client
                data = client.recv(buffer)
            
                if not data:
                    break

                # Sending data back to client
                client.sendall(data)
                print ("sent %d bytes back to %s" % (len(data), address))

def tcp_client(port, address, num, buffer, initial_size, increment, final_size):
    """Create a socket TCP client to send packets to server.

        Parameters
        ----------
        port : int, required
            The port the server will be listening on.

        address: str, required
            The server IP address.

        num: int, required
            Times the packet will be sent to the server.

        buffer: int, required
            Buffer size for sending data.

        initial_size: int, required
            Initial packet size.

        increment: int, required
            packet size increment value.

        final_size: int, required
            Final packet size.

        Utilization
        ------
        tcp_client(24, 10.0.1.10, 10, 1024, 1000, 50, 2000)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (address, port)
    
    # Connecting to server
    sock.connect(server_address)

    n = 1
    while initial_size<=final_size:
        latency_lst = []
        throughput_lst = []

        for i in range(num):
            try:
                message = 'a' * initial_size
                
                # Sending data to server
                start_time = time.time() * 1000
                sock.sendall(message.encode('utf-8'))
                
                amount_received = 0
                amount_expected = len(message)
                while amount_received < amount_expected:
                    # Receiving data from server
                    data = sock.recv(buffer)
                    amount_received += len(data)

                end_time = time.time() * 1000
                rtp = end_time - start_time
                latency_lst.append(rtp / 2)
                throughput_lst.append(len((message)* 1000) / rtp)
                
            except socket.error as e:
                print ("Socket error: %s" %str(e))
            except Exception as e:
                print ("Other exception: %s" %str(e))
        
        print('%d, %d, %.2f, %.2f, %.2f, %.2f' % (n,initial_size,st.mean(latency_lst), st.stdev(latency_lst),st.mean(throughput_lst), st.stdev(throughput_lst)))
        n+=1
        initial_size+=increment
              
    # Closing connection to the server
    sock.close()

def udp_server(port, address, buffer):
    """Create a socket UDP echo server to receive packets from client.

        Parameters
        ----------
        port : int, required
            The port the server will be listening on.

        address: str, required
            The server IP address.

        buffer: int, required
            Buffer size for receiving data.

        Utilization
        ------
        udp_server(24, 10.0.1.10, 1024)
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        server_address = (address, port)
        print ("Starting up echo server on %s port %s" % server_address)
        sock.bind(server_address)
        
        while True:
            print ("Waiting to receive message from client")
            data, address = sock.recvfrom(buffer)
            if not data:
                break
            print ("received %s bytes from %s" % (len(data), address))
           
            sent = sock.sendto(data, address)
            print ("sent %s bytes back to %s" % (sent, address))

def udp_client(port, address, num, buffer, initial_size, increment, final_size):
    """Create a socket UDP client to send packets to server.

        Parameters
        ----------
        port : int, required
            The port the server will be listening on.

        address: str, required
            The server IP address.

        num: int, required
            Times the packet will be sent to the server.

        buffer: int, required
            Buffer size for sending data.

        initial_size: int, required
            Initial packet size.

        increment: int, required
            packet size increment value.

        final_size: int, required
            Final packet size.

        Utilization
        ------
        udp_client(24, 10.0.1.10, 10, 1024, 1000, 50, 2000)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (address, port)

    n = 1
    while(initial_size<=final_size):   
        latency_lst = []
        throughput_lst = []
        lost = 0
        
        for i in range(num): 
            try:
                message = 'a' * initial_size

                # Sending data to server
                start_time = time.time() * 1000
                sent = sock.sendto(message.encode('utf-8'), server_address)
                sock.settimeout(1)

                # Receiving data from server
                data, server = sock.recvfrom(buffer)
                
                end_time = time.time() * 1000
                rtp = end_time - start_time
                latency_lst.append(rtp / 2)
                throughput_lst.append(len((message)* 1000) / rtp)

            except socket.timeout:
                lost+=1

        # Calculating jitter and average
        if num-lost >=2:
            jitter = st.stdev(latency_lst)
            media = st.mean(latency_lst)
        else:
            jitter = 0
            media = 0
        for _ in range (lost):
            latency_lst.append(0)
            throughput_lst.append(0)

        send_porcentage = (num - lost) / num        
        print('{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}'.format(n,initial_size,st.mean(latency_lst),media, st.stdev(latency_lst),st.mean(throughput_lst), st.stdev(throughput_lst),send_porcentage,jitter))

        n+=1
        initial_size+=increment
    
    # Closing connection to the server
    sock.close()

if __name__ == '__main__':
    
    args = read_args()
    client = args.client
    server = args.server
    tcp = args.tcp
    udp = args.udp
    port = args.port
    address = args.address
    interval = args.interval
    num = args.num
    buffer = args.buffer
    if buffer == None: 
        buffer = 131072


    if interval:
        try:
            ini, fin, inc = interval.split(',')  
            initial_size = int(ini)
            increment = int(inc)
            final_size = int(fin)     
        except Exception as e:
            print ('Invalid arg value for w (range)')
            sys.exit()
    
    # Uncomment theese lines if it is necessary checking param values
    # print('client = ',client)
    # print('server = ',server)
    # print('tcp = ',tcp)
    # print('udp = ',udp)
    # print('port = ',port)
    # print('address = ',address)
    # print('interval = ',interval)
    # print('num = ',num)
    # print('buffer = ',buffer)

    if server:
        if tcp:
            tcp_server(port, socket.gethostbyname(socket.gethostname()), buffer)
        elif udp:
            udp_server(port, socket.gethostbyname(socket.gethostname()), buffer)
    elif client:
        if tcp:
            tcp_client(port, address, num, buffer,initial_size,increment,final_size)
        elif udp:
            udp_client(port, address, num, buffer,initial_size,increment,final_size)
            
