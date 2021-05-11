#!/usr/bin/python3
# -*- coding: utf-8; mode: python -*-
# Elena Martín Cantero, DNI - 70592187N

import socket
import hashlib
import sys

########################################## GET_ID ######################################################
def get_id(mensaje):
    linea_1 = mensaje.splitlines()[0] 
    id = mensaje[11:len(linea_1)]
    return id

########################################## CLEAN_BUFFER ################################################
def clean_buffer(sock):
    while True: 
        msgR = sock.recv(1024).decode(encoding = 'utf-8', errors = 'ignore' )
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
    
    if msgR[0:10] == "identifier":
        reto1(get_id(msgR))
    sock.close()

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
        except socket.timeout as e:
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
    if next != "error": 
        reto3(next)
    sock.close()

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

    clean_buffer(sock) 
    
    sock.close()

reto0()


