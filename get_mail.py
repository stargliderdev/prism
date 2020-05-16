#!/usr/bin/python
# -*- coding: utf-8 -*-

import poplib
import string, random
import io, rfc822


def readMail():
    SERVER = "hosting15.serverhs.org"

    USER = 'saft@jheg.pt'
    PASSWORD = 'D*F,5N$w2u4)'
    # connect to server
    server = poplib.POP3(SERVER)
    
    # login
    server.user(USER)
    server.pass_(PASSWORD)
    
    # list items on server
    resp, items, octets = server.list()
    
    database = []
    # for i in range(0, 100):
    for i in range(0, len(items)):
        id, size = string.split(items[i])
        resp, text, octets = server.retr(id)
    
        text = string.join(text, "\n")
        f_ile = io.StringIO(text)
    
        message = rfc822.Message(f_ile)
    
        stack = ''
        for n in list(message.items()):
            if n[0] == 'to':
                a = n[1].split(',')
                for f in a:
                    if f != 'saft@jheg.pt':
                        stack += f + ','
            if n[0] == 'subject':
                a = n[1].find('NIF:')
                x = n[1][a+4:a+9+5]
        database.append((x, stack))
    
        # for k, v in message.items():
        # print k['from'],v
        # print k, "=", v
    
    xl = {}
    for n in database:
        if n[0] in list(xl.keys()):
            pass
        else:
            xl[n[0]] = n[1]
    import stdio
    stdio.debug_dict(xl)
readMail()