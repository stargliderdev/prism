#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import parameters as pa
import libpg
import psycopg2


def insert_debug(text):
    global conn_string
    if 1 == 1:
        text = text.replace('%', '@')
        text = text.replace('\'', 'A')
        debug_info = 'insert into debug(debug_strin) values(\'' + text + '\')'
        try:
            conn = psycopg2.connect(pa.conn_string)
            cur = conn.cursor()
            conn.set_client_encoding('UTF8')
            cur.execute(debug_info)
            conn.commit()
            cur.close()
            conn.close()
        
        except Exception as e:
            print('SQL Execute SQL Error:', str(e), debug_info)
            sys.exit(2)
        # execute_query('insert into debug(debug_strin) values(%s)', (text,))


def software_update():
    pa.ass_marca_modelo = libpg.OutputQueryOne('select sft_software from software_type where sft_id = %s',(pa.current_unit['un_software'],)).output[0]
    text = pa.current_unit['un_software_version']
    pa.gasta_ticket = False
    pa.ass_facturar = False
    pa.ass_facturado = 0
    pa.ass_relatorio_interno = 'VERSÃO ACTUAL DO SOFTWARE:' + text + '\n'
    pa.ass_falha = 2
    pa.status_id = 3
    pa.ass_meio = -1
    if pa.current_unit['un_updates_until'] <= datetime.date.today():
        pa.ass_relatorio_factura += 'NÂO TEM DIREITO A UPGRADES!\n'
    else:
        pa.ass_relatorio_factura += 'TEM DIREITO A UPGRADES!\n'
    # processa updates de software
    pa.pendente = True
    

def copy_cl_external():
    unidades = libpg.query_many('select un_id, un_cliente_id, un_nome from unidades')
    for n in unidades:
        # print('unidade',n)
        insert_debug('''select cl_id, cl_nome from clientes where cl_external_id=%s ''' + str(n[1]))
        client = libpg.query_one('select cl_id, cl_nome from clientes where cl_external_id=%s',(n[1],))
        # print('    cleinte',client)
        if not client is None:
            # print('unidade ',n[0],' de ', n[1], ' para ', client)
            insert_debug('''update unidades set un_cliente_id=%s where un_id=%s  ''' + str(client[0]) + ' ' + str(n[0]))
            libpg.execute_query('''update unidades set un_cliente_id=%s where un_id=%s  ''',(client[0], n[0]))
  
  
def insert_unit_type_ref():
    libpg.execute_query('''delete from unit_types_ref''')
    commit_types = libpg.query_many('''select cmt_id from comit_types where cmt_active=True''')
    settings_types = libpg.query_many('''select unit_set_id from unit_set_types where unit_set_active=True''')
    for f in range(1,8):
        for n in commit_types:
            sql = 'insert into unit_types_ref ( un_type_ref_class, un_type_ref_unit_type, un_type_ref_setting_id) VALUES (%s,%s,%s) '
            data = (1,f,n)
            libpg.execute_query(sql, data)
        for g in settings_types:
            data = (0,f,g)
            libpg.execute_query(sql, data)
  
  
def main():
    # insert_unit_type_ref()
    pass


if __name__ == '__main__':
    main()
