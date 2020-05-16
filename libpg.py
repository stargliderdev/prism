#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2

# note that we have to import the Psycopg2 extras library!
import base64
import psycopg2.extras
import parameters as gl
import liberror


def query_one(sql, data=(True,)):
    # type: (object, object) -> object
    try:
        conn = psycopg2.connect(gl.conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        return cur.fetchone()
    except Exception as e:
        f = liberror.Dialog('SQL Query One Error', str(e), sql, data)
        f.exec_()


def query_many(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        hl = cur.fetchall()
        cur.close()
        conn.close()
        return hl
    except Exception as e:
        print(str(e))
        print(sql, data)

def sql_query(sql):
    try:
        conn = psycopg2.connect(gl.conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        # print 'mogrify:', cur.mogrify(sql, data)
        cur.execute(sql, (True,))
        return cur.fetchall()
    except Exception as e:
        f = liberror.Dialog('SQL Query Many Error', str(e), sql, '')
        f.exec_()


def execute_query(sql, data=(True,)):
    try:
        conn = psycopg2.connect(gl.conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        # print ('mogrify:', cur.mogrify(sql, data))
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(str(e))
        f = liberror.Dialog('SQL Execute SQL Error', str(e), sql, data)
        f.exec_()


def get_record_dic(sql, id):
    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute(sql, id)
    rec = dict_cur.fetchone()
    dict_cur.close()
    conn.close()
    return rec


def write_unit_bin(_file, uuid):
    try:
        conn = psycopg2.connect(gl.conn_string)
        f = open(_file, 'rb')  # .read()
        binary = f.read()
        encoded_var = base64.b64encode(binary)
        cursor = conn.cursor()
        # cursor.execute("INSERT INTO unit_files (un_filles_uuid, un_files_data) VALUES (%s,%s);",(uuid, psycopg2.Binary(encoded_var)))
        cursor.execute("INSERT INTO unit_files (un_files_uuid, un_files_data) VALUES (%s,%s);", (uuid, encoded_var))
        conn.commit()
        cursor.close()
        conn.close()
        sql = "SELECT  octet_length(un_files_data) FROM unit_files where un_files_uuid =%s;"
        a = query_one(sql, (uuid,))
        return a[0], a[0] / 1000.0 / 1000.0
    except Exception as e:
        return -1, str(e)


def read_unit_bin(_file, uuid):
    try:
        conn = psycopg2.connect(gl.conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT (un_files_data) FROM unit_files WHERE un_files_uuid=\'" + uuid + "\'")
        xl = cursor.fetchone()
        a = base64.b64decode(xl[0])
        open(_file, 'wb').write(a)
        # open(_file, 'wb').write(str(xl[0]))
        cursor.close()
        conn.close()
    except Exception as e:
        print('-----------erro --------------')
        print(str(e))


if __name__ == "__main__":
    pass
