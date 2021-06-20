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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (address, port)
        # print ("Starting up echo server  on %s port %s" % server_address)
        sock.bind(server_address)
        sock.listen(backlog)
        client, address = sock.accept()
        with client:
            # print('Connected by', address)
            while True:
                # print ("Waiting to receive message from client")
                data = client.recv(buffer)
                #time.sleep(1)
                if not data:
                    break
                # print ("Data: %s" %data)
                client.sendall(data)
                print ("sent %d bytes back to %s" % (len(data), address))

def tcp_client(port, address, num, buffer, initial_size, increment, final_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (address, port)
    # print ("Connecting to %s port %s" % server_address)
    sock.connect(server_address)

    # print(initial_size,increment,final_size)

    n = 1
    while initial_size<=final_size:
        latency_lst = []
        throughput_lst = []
        # print('Data size = ',initial_size)
        for i in range(num):
            try:
                #time.sleep(1)
                message = 'a' * initial_size
                # print ("Sending %s" % message)
                start_time = time.time() * 1000
                sock.sendall(message.encode('utf-8'))
                amount_received = 0
                amount_expected = len(message)
                while amount_received < amount_expected:
                    data = sock.recv(buffer)
                    amount_received += len(data)
                    # print('Received = ',amount_received)
                    # print ("Received: %s" % data)
                end_time = time.time() * 1000
                rtp = end_time - start_time
                latency_lst.append(rtp / 2)
                throughput_lst.append(len((message)* 1000) / rtp)
            except socket.error as e:
                print ("Socket error: %s" %str(e))
            except Exception as e:
                print ("Other exception: %s" %str(e))
        # print(latency_lst)
        # print(throughput_lst)
        print('%d, %d, %.2f, %.2f, %.2f, %.2f' % (n,initial_size,st.mean(latency_lst), st.stdev(latency_lst),st.mean(throughput_lst), st.stdev(throughput_lst)))
        n+=1
        initial_size+=increment
              
    # print ("Closing connection to the server")
    sock.close()

def udp_server(port, address, buffer):
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
            # print ("Data: %s" %data)
           
            #time.sleep(2)
            sent = sock.sendto(data, address)
            print ("sent %s bytes back to %s" % (sent, address))

def udp_client(port, address, num, buffer, initial_size, increment, final_size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = (address, port)
    # print ("Connecting to %s port %s" % server_address)

    n = 1
    while(initial_size<=final_size):   
        latency_lst = []
        throughput_lst = []
        lost = 0
        # print('Data size = ',initial_size)
        for i in range(num): 
            try:
                message = 'a' * initial_size
                #print ("Sending %s" % message)
                start_time = time.time() * 1000
                sent = sock.sendto(message.encode('utf-8'), server_address)
                sock.settimeout(1)

                data, server = sock.recvfrom(buffer)
                # print ("Received %s" % data)
                end_time = time.time() * 1000
                rtp = end_time - start_time
                latency_lst.append(rtp / 2)
                throughput_lst.append(len((message)* 1000) / rtp)

            except socket.timeout:
                lost+=1
                #print("------------LOST!--------------------")

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
        # print('Latency list = ',latency_lst)
        # print('Throughput list = ',throughput_lst)
        # print('Lost porcentage = ',send_porcentage)        
        print('{},{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}'.format(n,initial_size,st.mean(latency_lst),media, st.stdev(latency_lst),st.mean(throughput_lst), st.stdev(throughput_lst),send_porcentage,jitter))

        n+=1
        initial_size+=increment
    # print ("Closing connection to the server")
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

    if interval:
        try:
            ini, fin, inc = interval.split(',')  
            initial_size = int(ini)
            increment = int(inc)
            final_size = int(fin)     
        except Exception as e:
            print ('Invalid arg value for w (range)')
            sys.exit()

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
            tcp_server(port, address, buffer)
        elif udp:
            udp_server(port, address, buffer)
    elif client:
        if tcp:
            tcp_client(port, address, num, buffer,initial_size,increment,final_size)
        elif udp:
            udp_client(port, address, num, buffer,initial_size,increment,final_size)
            





    
