#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-
# Elena Martín Cantero, DNI - 70592187N


import socket
import hashlib
import sys
import base64
import struct
import array
import requests
import threading
import queue

########################################## GET_ID ######################################################
def get_id(mensaje):
    linea_1 = mensaje.splitlines()[0] 
    id = mensaje[11:len(linea_1)]
    return id

########################################## CLEAN_BUFFER ################################################
def clean_buffer(sock):
    while True: 
        msgR = sock.recv(2048).decode(encoding = 'utf-8', errors = 'ignore' )
        initial = msgR.split(":")[0]
        if initial == "identifier": 
            print(msgR) 
            return get_id(msgR) 
        elif  initial == "[EE": 
            print(msgR)
            return "error"

########################################## RETO 0 ######################################################
#You should reply to this message with your username.

def reto0():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect(("rick", 2000)) 

    msgR = sock.recv(1024).decode() 
    print(msgR)

    sock.sendall("sweet_franklin".encode()) 

    msgR = sock.recv(1024).decode() 
    print(msgR)
    sock.close()
    if msgR[0:10] == "identifier":
        reto1(get_id(msgR))
    

########################################## RETO 1 ######################################################
#Test Chamber 1: UDP
def reto1(id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    msgS = '65419 ' + id 
    idUpper = id.upper() 
    sock.bind(('', 65419)) 

    sock.sendto(msgS.encode(), ('rick', 4000)) 
    msgR, peer = sock.recvfrom(1024) 
    sock.sendto(idUpper.encode(), peer) 
    msgR, peer = sock.recvfrom(1024) 
    print(msgR.decode())
    msgR = msgR.decode()
    sock.close()
    initial = msgR.split(":")[0]
    if (initial == "identifier"):
        reto2(get_id(msgR)) 

########################################## RETO 2 ######################################################
#Test Chamber 2: Words len
def reto2(id):
    suma = 0
    msgR = ''
    longitud = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect(('rick',3010)) 
    
    msgS = id + ' '
    sock.settimeout(1)
    while 1: 
        try:
            msgR += sock.recv(2048).decode() 
        except:
            break

    i = 0 
    while suma < 1000 and i < len(msgR):  
        if msgR[i] == ' ': 
            msgS = msgS + str(longitud) + ' ' 
            suma = suma + longitud
            longitud = 0 
        else: 
            longitud += 1 
        
        i += 1

    if longitud != 0:
        msgS = msgS + str(longitud) + ' '

    msgS = msgS + '--' 
    sock.send(msgS.encode()) 

    next = clean_buffer(sock) 
    sock.close()
    if next != "error": 
        reto3(next)
    

########################################## RETO 3 ######################################################            
#Test Chamber 3: Decrypt words
def reto3 (id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.connect(("rick",6501)) 
    msgR = ""
    condition = True
    num = 0
    msgS = id + " "

    while condition: 
        aux = sock.recv(1024).decode() 
        msgR += aux 
        for char in aux: 
            if char.isdigit(): 
                num = char 
                condition = False 
                break 

    palabras = msgR.split() 
    pos = int(palabras.index(num)) 
    num = int(num) 
    encrypted_split = palabras[(pos-num):pos] 
    encrypted = " ".join(encrypted_split) 

    for i in encrypted:
        first_pos = ord(i) 
        pos = first_pos-num  
        if (pos < 97 and first_pos > 96) or (pos < 65 and first_pos > 64): 
            pos += 26
                
        if i != " ": 
            msgS += chr(pos)
        else:
            msgS += i

    msgS += " --" 
    sock.send(msgS.encode())  

    next = clean_buffer(sock) 
    sock.close()
    if next != "error": 
        reto4(next)
    

########################################## RETO 4 ######################################################            
#Test Chamber 4: SHA1
def reto4(id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("rick", 9003)) 

    sock.send(id.encode()) 

    bin = b''
    size = sock.recv(1).decode()
    while True:
        nextC = sock.recv(1).decode()
        if nextC == ':':
            break
        else:
            size += nextC
    
    size = int(size)
    while size > len(bin): 
        bin += sock.recv(1024)
    
    bin = bin[:size]
    sol = hashlib.sha1(bin).digest() 
    sock.send(sol) 

    next = clean_buffer(sock) 
    sock.close()
    if next != "error":
        reto5(next)
    

########################################## RETO 5 ######################################################            
#Test Chamber 5: WYP
def reto5(id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    wyp = "WYP"
    
    
    header = struct.pack('!3sBHHH',wyp.encode(), 0, 0, 0, 1) 
    payload = base64.b64encode(id.encode())

    msgS = header + payload
    checksum = cksum(msgS)

    header = struct.pack('!3sBHHH',wyp.encode(), 0, 0, checksum, 1)
    msgS = header + payload

    sock.sendto(msgS, ('rick', 6000))
    msgR= sock.recv(4096)[10:]
    msgR = base64.b64decode(msgR)
    msgR = msgR.decode()
    print(msgR)
    sock.close()
    reto6(get_id(msgR))

########################################## CKSUM ######################################################            
#Autor: David Villa Alises
def cksum(pkt):
    # type: (bytes) -> int
    if len(pkt) % 2 == 1:
        pkt += b'\0'
    s = sum(array.array('H', pkt))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    s = ~s

    if sys.byteorder == 'little':
        s = ((s >> 8) & 0xff) | s << 8

    return s & 0xffff

########################################## RETO 6 ######################################################            
#Test Chamber 6: Web Server 
def reto6 (id):
    port = 22150
    sockR = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockR.bind(('', port))
    sockR.listen(25)

    sockS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockS.connect(('rick', 8002))
    msgS = str(id) + " " + str(port) 
    sockS.send(msgS.encode())

    t = threading.Thread(target=handleFirst, args=(sockR,))
    t.start()

    sockS.close()
        
########################################## HANDLE FIRST ######################################################            
def handleFirst(sockR):
    q = queue.Queue(1)
    cond = True
    next = ""
    while cond:
        client, addr = sockR.accept()
        if threading.active_count() < 18:
            t = threading.Thread(target = handle, args = (client,addr, q))
            t.start()
            next = q.get()
        if len(next) > 1:
            cond = False
            
    sockR.close()
    print(next)
    if next != "error":
        reto7(get_id(next))       
    
########################################## HANDLE ######################################################            
def handle(client, addr, q):
    msgR = client.recv(2048).decode()
    if msgR[0:3] == "GET":
        rfc = requests.get("http://rick:81/rfc" + msgR.split()[1])
        msgS = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n".encode()+rfc.content
        client.send(msgS)
        q.put(item="")
    elif msgR[0:4] == "POST":
        nextChallenge = msgR.splitlines()[8:]
        nextChallenge = "\n".join(nextChallenge)
        q.put(item = nextChallenge)
    else:
        q.put("error")
        
    client.close()

########################################## RETO 7 ######################################################            
#Reto final
def reto7(id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('rick', 33333))
    sock.send(id.encode())
    final = sock.recv(1024).decode()
    print(final)
    sock.close()

reto0()
