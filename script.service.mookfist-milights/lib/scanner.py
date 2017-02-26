import sys, time
from socket import *

def get_bridges():

    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('',0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    s.sendto('Link_Wi-Fi', ('255.255.255.255', 48899))
    data = s.recv(1024)
    if data:
        ip, mac = data.split(',')[:2]
        return (ip, mac)

