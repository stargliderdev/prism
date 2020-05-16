#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import os
import parameters as gl
import datetime
import base64

def attach_file(file_path):
    f = open(file_path, 'rb')
    binary = f.read()
    c = attachment_info(file_path)
    c['file_size'] = len(binary)
    conn = psycopg2.connect(gl.conn_string)
    curs = conn.cursor()
    curs.execute("INSERT into att_unit (att_data) values (%s)", (psycopg2.Binary(binary),))
    conn.commit()
    curs.close()
    conn.close()


def attachment_info(file_path):
    if os.path.exists(file_path):
        ext = file_path[file_path.rfind('.') +1 :]
        file_name = file_path[file_path.rfind('/') +1 :]
        file_name = file_name[: file_name.rfind('.')]
        return {'ext':ext,'file_name':file_name, 'file_size':0}
    else:
        print('file not found')
        return {'ext':'','file_name':'', 'file_size': -1}


