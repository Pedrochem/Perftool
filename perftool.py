#!/usr/bin/env python

import time
import socket
import sys
import argparse
from random import randint
import statistics as st


backlog = 5


def read_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', action="store_true", dest="client")
    parser.add_argument('-s', action="store_true", dest="server")
    parser.add_argument('-tcp', action="store_true", dest="tcp")
    parser.add_argument('-udp', action="store_true", dest="udp")
    parser.add_argument('-port', action="store", dest="port", type=int, required=True)
    parser.add_argument('-a', action="store", dest="address", type=str, required=False)
    parser.add_argument('-w', action="store", dest="interval", type=str, required=False)
    parser.add_argument('-n', action="store", dest="num", type=int, required=False)
    parser.add_argument('-b', action="store", dest="buffer", type=int, required=True)
    args = parser.parse_args()
    if (args.client and args.server) or (args.tcp and args.udp):
        print("Invalid args")
        sys.exit()
    return parser.parse_args()

def tcp_server(port, address, buffer):
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Enable reuse address/port
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the port
        server_address = (address, port)
        print ("Starting up echo server  on %s port %s" % server_address)
        sock.bind(server_address)
        # Listen to clients, backlog argument specifies the max no. of queued connections
        sock.listen(backlog)
        client, address = sock.accept()
        with client:
            print('Connected by', address)
            while True:
                print ("Waiting to receive message from client")
                data = client.recv(buffer)
                time.sleep(1)
                if not data:
                    break
                print ("Data: %s" %data)
                client.sendall(data)
                print ("sent %d bytes back to %s" % (len(data), address))

def tcp_client(port, address, interval, num, buffer):
    # Create a TCP/IP socket    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the server
    server_address = (address, port)
    print ("Connecting to %s port %s" % server_address)
    sock.connect(server_address)
    
    #defines data size interval
    try:
        ini, fin, inc = interval.split(',')  
        initial_size = int(ini)
        increment = int(inc)
        final_size = int(fin)     
    except Exception as e:
        print ('Invalid arg value for w (range)')
        sys.exit()

    print(initial_size,increment,final_size)

    # Send data
    n = 1
    while initial_size<=final_size:
        latency_lst = []
        throughput_lst = []
        print('Data size = ',initial_size)
        for i in range(num):
            try:
                #time.sleep(1)
                message = 'a' * initial_size
                # print ("Sending %s" % message)
                start_time = time.time()
                sock.sendall(message.encode('utf-8'))
                # Look for the response
                amount_received = 0
                amount_expected = len(message)
                while amount_received < amount_expected:
                    data = sock.recv(buffer)
                    amount_received += len(data)
                    # print('received = ',amount_received)
                    # print ("Received: %s" % data)
                end_time = time.time()
                rtp = end_time - start_time
                latency_lst.append(rtp / 2)
                throughput_lst.append(len(message) / rtp * 100)
            except socket.error as e:
                print ("Socket error: %s" %str(e))
            except Exception as e:
                print ("Other exception: %s" %str(e))
        print(latency_lst)
        print(throughput_lst)
        print('%d , %d, %f, %f, %f, %f' % (n,initial_size,st.mean(latency_lst), st.stdev(latency_lst),st.mean(throughput_lst), st.stdev(throughput_lst)))
        n+=1
        initial_size+=increment
              
    print ("Closing connection to the server")
    sock.close()

def udp_server(port, address, buffer):
    return None

def udp_client(port, address, interval, num, buffer):
    return None


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

    print('client = ',client)
    print('server = ',server)
    print('tcp = ',tcp)
    print('udp = ',udp)
    print('port = ',port)
    print('address = ',address)
    print('interval = ',interval)
    print('num = ',num)
    print('buffer = ',buffer)

    if server:
        if tcp:
            tcp_server(port, address, buffer)
        elif udp:
            udp_server(port, address, buffer)
    elif client:
        if tcp:
            tcp_client(port, address, interval, num, buffer)
        elif udp:
            udp_client(port, address, interval, num, buffer)
            





    
