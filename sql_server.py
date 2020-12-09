#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import datetime
import pyodbc
import sys
import os


def query_one(sql, data=(True,)):
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        insert_debug(sql + str(data))
        return cur.fetchone()
    except Exception as e:
        print('SQL Query One Error:' + str(e) + sql, data)
        sys.exit(1)


def query_many(sql, data=(True,)):
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        # print 'mogrify:', cur.mogrify(sql, data)
        cur.execute(sql, data)
        hl = cur.fetchall()
        cur.close()
        insert_debug(sql + str(data))
        return hl
    except Exception as e:
        print('SQL Query One Error:' + str(e) + sql, data)
        sys.exit(1)


def execute_query(sql, data=(True,)):
    global conn_string
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        conn.set_client_encoding('UTF8')
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        conn.close()
        insert_debug(sql + str(data))
    
    except Exception as e:
        print('SQL Execute SQL Error:', str(e), sql, data)
        sys.exit(2)



def compras():
    global sql_server_conn_str
    cnxn = pyodbc.connect(sql_server_conn_str)
    cursor = cnxn.cursor()
    cursor.execute(''' SELECT  [NumSerie]
              ,UPPER(LinhasCompras.[NumDocExterno]) as docnumb
              ,LinhasCompras.[DataDoc] 
              ,[LinhasCompras].Artigo
              ,UPPER(Fornecedores.Nome)  as ent
              ,[LinhasCompras].[Descricao]
              FROM [LinhasNumSerie], LinhasCompras
              , [CabecCompras]
              ,Fornecedores
              ,[Artigo]            
          where [LinhasNumSerie].[Manual] = 1 and [Artigo].[UtilManutencao]= 1  
          and [Artigo].Artigo = [LinhasCompras].Artigo and 
           [LinhasNumSerie].[Modulo] = 'C' and
          [LinhasNumSerie].IdLinhas = LinhasCompras.[Id] and
          [CabecCompras].Id = LinhasCompras.IdCabecCompras and
           Fornecedores.Fornecedor = [CabecCompras].[Entidade]
          order by LinhasCompras.artigo''')
    xl = []
    for row in cursor:
        # print(row[3])
        xl.append((row[0], row[1], row[2], row[3], row[4], row[5]))
    cursor.close()
    return xl


def insert_hardware():
    print('insert new products')
    xl = compras()
    if file_ok('./log/compras.log'):
        os.remove('./log/compras.log')
    if file_ok('./log/sem_ref.log'):
        os.remove('./log/sem_ref.log')
    if file_ok('./log/ns_in_db.log'):
        os.remove('./log/ns_in_db.log')
    if file_ok('./log/ns_added.log'):
        os.remove('./log/ns_added.log')
    c = 0
    missing_articles = {}
    execute_query('''delete from articles_tmp''', (True,))
    for n in xl:
        # existe a refernecia da gc no prism?
        a = query_one('select md_id from models where md_ref_gc = %s', (n[3],))
        if a is not None:
            # existe ref
            is_serial = query_one('select hw_id from hardware where hw_sn =%s', (n[0],))
            # existe o n/s
            if is_serial is not None:
                # sim existe
                # print('existe n/s' , n[0], n[3] ,file=open("./log/ns_in_db.log", "a"))
                pass
            else:
                # não existe --  insere n/s
                execute_query('''INSERT INTO hardware
                              (hw_model_id, hw_sn, hw_unit_id, hw_status_id,
                               hw_supplier, hw_warranty, hw_supplier_warranty, hw_supplier_date,
                               hw_invoice_supplier)
                              VALUES (%s, %s, 0, 0, %s,12,12, %s, %s);''', (a, n[0], n[4], n[2], n[1]))
                c += 1
                # print('adicionado ' , n[0], n[3] ,file=open("./log/ns_added.log", "a"))
        else:
            if n[3] in missing_articles.keys():
                # print('in black list')
                pass
            else:
                # print('add to black list')
                missing_articles[n[3]] = n[5]
                # print('sem ref', n[3], n[5])
                print(n[3], n[5], file=open("./log/sem_ref.log", "a"))
                execute_query('''INSERT INTO articles_tmp (art_tmp_reference, art_tmp_name) VALUES (%s,%s)''',
                              (n[3], n[5]))   
    # print('total de adicionados', c, file=open("compras.log", "a"))
    print('total de adicionados', c)  # , file=open("compras.log", "a"))


def vendas():
    global sql_server_conn_str
    cnxn = pyodbc.connect(sql_server_conn_str)
    
    cursor = cnxn.cursor()
    cursor.execute('''SELECT TOP 20 
           [NumSerie]
          ,[CabecDoc].NumDoc
          ,CAST([CabecDoc].Data AS DATE) as data
          ,[CabecDoc].[NumContribuinte]
          ,[CabecDoc].TipoDoc
          FROM LinhasNumSerie, LinhasDoc,CabecDoc
           where [LinhasNumSerie].[Manual] = 0 and [LinhasNumSerie].[Modulo] = 'V' and
          [LinhasNumSerie].IdLinhas = [LinhasDoc].[Id] and
          [CabecDoc].Id = [LinhasDoc].IdCabecDoc and [CabecDoc].TipoDoc ='FA'
          and 		 
          [CabecDoc].Data >='2019-08-01' order by data ''')
    xl = []
    for row in cursor:
        xl.append((row[0], row[1], row[2], row[3], row[4]))
    return xl


def sync_vendas(xl):
    if file_ok('./log/vendas.log'):
        os.remove('./log/vendas.log')
    c = 0
    multi_unit = 0
    added = 0
    for n in xl:
        is_serial = query_one('SELECT hw_id from hardware where hw_sn = %s and hw_invoice ISNull', (n[0],))
        # ns está na base de dados.
        if is_serial is not None:
            # print('ok serial', is_serial, n[0])
            multi_units = query_many('''select un_id from unidades 
                where unidades.un_cliente_id = (select cl_id from clientes where cl_nif=%s)''', (n[3],))
            if len(multi_units) > 1:
                multi_unit += 1
                # print('cliente ', n[3], 'com ', multi_units[0], ' unidade', file=open("vendas.log", "a"))
                # print('cliente ', n[3], 'com ', multi_units)
                execute_query(
                    'update hardware SET hw_invoice = %s, hw_unit_id = %s, hw_status_id=1, hw_invoice_date = %s WHERE hw_sn = %s',
                    (n[1], multi_units[0], n[2], n[0]))
            elif len(multi_units) == 0:
                print('cliente ', n[3], 'sem unidade ... ')
                execute_query('update hardware SET hw_unit_id = 9999, hw_status_id=1 WHERE hw_sn = %s',
                              (n[0],))
            else:
                # print('cliente ', n[3], 'com ', multi_units)
                execute_query(
                    'update hardware SET hw_invoice = %s, hw_unit_id = %s,hw_status_id=1, hw_invoice_date = %s WHERE hw_sn = %s',
                    (n[1], multi_units[0], n[2], n[0]))
                added += 1
                # execute_query('')
    print('add', added)
    print('multi', multi_unit)


def sync_clientes_cc():
    global sql_server_conn_str
    print('update clients balance')
    cnxn = pyodbc.connect(sql_server_conn_str)
    cursor = cnxn.cursor()
    cursor.execute('''    SELECT[NumContrib]
         , [Nome]
         , [TotalDeb]
         FROM[Clientes]
         where [Cliente]<>\'VD\' order by [NumContrib]''')
    xl = 0.0
    
    for row in cursor:
        if row[2] > 0.99:
            # print(row)
            execute_query('update clientes SET cl_cc = %s WHERE cl_nif = %s', (row[2], row[0]))
            xl += row[2]
        else:
            execute_query('update clientes SET cl_cc = %s WHERE cl_nif = %s', (0.00, row[0]))
    return xl


def teste_server_connection():
    global sql_server_conn_str
    cnxn = pyodbc.connect(sql_server_conn_str)
    cursor = cnxn.cursor()
    cursor.execute('''    SELECT[NumContrib]
         , [Nome]
         , [TotalDeb]
         FROM[Clientes]
         where [Cliente]<>\'VD\' order by [NumContrib]''')
    print(cursor)


def insert_debug(text):
    global conn_string
    if 1 == 2:
        text = text.replace('%', '@')
        text = text.replace('\'', 'A')
        debug_info = 'insert into debug(debug_strin) values(\'' + text + '\')'
        try:
            conn = psycopg2.connect(conn_string)
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


def show_compras():
    for n in compras():
        # print(n)
        print('{:20}'.format(n[0]), '{:19}'.format(n[1]), '{:%Y-%m-%d}'.format(n[2]), '{:30}'.format(n[3]),
              '{:50}'.format(n[4]), n[5])


def show_vendas():
    sales = vendas()
    for n in sales:
        # print(n)
        cl_data = query_one('select cl_nome from clientes where cl_nif =%s', (n[3],))
        hwd_data = query_one('select * from hardware where upper(hw_sn)=%s', (n[0].upper().strip(),))
        if hwd_data == None:
            pass
        else:
            print('encontrado')
            print('{:20}'.format(n[0]), '{:19}'.format(n[1]), '{:%Y-%m-%d}'.format(n[2]), '{:30}'.format(n[3]),
                  '{:12}'.format(n[4]))
            print('  no cliente')
            print('    ', cl_data[0].strip())
            print('    o equipamento')
            print('       *', hwd_data)
    
    print('total', len(sales))


def add_new_products():
    xl = compras()
    execute_query('''delete from articles_tmp''', (True,))
    for n in xl:
        a = query_one('select md_id from models where md_ref_gc = %s', (n[3],))
        if a is not None:
            pass
        else:
            execute_query('''INSERT INTO articles_tmp (art_tmp_reference, art_tmp_name) VALUES (%s,%s)''', (n[3], n[5]))


def add_new_hardware():
    global sql_server_conn_str
    print('add new hardware from serial number...')
    add_new = 0
    cnxn = pyodbc.connect(sql_server_conn_str)
    cursor = cnxn.cursor()
    cursor.execute(''' SELECT  [LinhasCompras].Artigo,
              upper([NumSerie]),
              UPPER(LinhasCompras.[NumDocExterno]) as docnumb,
              LinhasCompras.[DataDoc],
              UPPER(Fornecedores.Nome)  as ent,
              [LinhasCompras].[Descricao]
              FROM [LinhasNumSerie], LinhasCompras,
              [CabecCompras],
              Fornecedores,
              [Artigo]
          where [LinhasNumSerie].[Manual] = 1 and [Artigo].[UtilManutencao]= 1
          and [Artigo].Artigo = [LinhasCompras].Artigo and
           [LinhasNumSerie].[Modulo] = 'C' and
          [LinhasNumSerie].IdLinhas = LinhasCompras.[Id] and
          [CabecCompras].Id = LinhasCompras.IdCabecCompras and
           Fornecedores.Fornecedor = [CabecCompras].[Entidade]
          order by LinhasCompras.artigo''')
    xl = []
    for row in cursor:
        # print(row[3])
        xl.append((row[0], row[1], row[2], row[3], row[4], row[5]))
        find_serial = query_one('select hw_id from hardware where upper(hw_sn)=%s', (row[1],))
        if find_serial is None:
            # print('não encontrado ', row[1])
            a = query_one('select md_id from models where md_ref_gc = %s', (row[0],))
            if a is None:
                pass  # na tem referencia comercial
                print('   não Tem referencia comercial:', row[0])
            else:
                # print('   tem referencia comercial insere', row[0])
                execute_query(
                    '''INSERT INTO hardware (hw_model_id, hw_sn, hw_unit_id, hw_status_id, hw_supplier, hw_warranty, hw_supplier_warranty, hw_supplier_date, hw_invoice_supplier) VALUES ((select md_id from models where md_ref_gc= %s), %s, 0, 0, %s,12,12, %s, %s);''',
                    (row[0], row[1], row[4], row[3], row[2]))
                add_new += 1
        
        else:
            pass
            # print('    encontrado ', row[1])
    cursor.close()
    cnxn.close()
    print('added:', add_new)


def sales_update():
    global sql_server_conn_str
    print('sales update')
    execute_query('delete from missing_units')
    cnxn = pyodbc.connect(sql_server_conn_str)
    
    cursor = cnxn.cursor()
    cursor.execute('''SELECT
          [CabecDoc].NumDoc,
          [NumSerie],
          CAST([CabecDoc].Data AS DATE) as data,
          [CabecDoc].[NumContribuinte],
          [CabecDoc].TipoDoc,
          clientes.nome
          FROM LinhasNumSerie, LinhasDoc,CabecDoc,clientes
           where [LinhasNumSerie].[Manual] = 0 and [LinhasNumSerie].[Modulo] = 'V' and
          [LinhasNumSerie].IdLinhas = [LinhasDoc].[Id] and
          [CabecDoc].Id = [LinhasDoc].IdCabecDoc and [CabecDoc].TipoDoc ='FA'
          and
            Clientes.NumContrib=CabecDoc.NumContribuinte and
          [CabecDoc].Data >='2010-01-01'
           order by data asc''')
    cnt = 0
    missing_unit = 0
    for row in cursor:
        serial_in_db = query_one('select hw_id, hw_unit_id from hardware where upper(hw_sn)=%s', (row[1],))
        # print('----------ROW',row)
        # print('Serial in bd', serial_in_db)
        if serial_in_db is None:
            pass
        else:
            # colocar só unidades activas
            unit_id = query_one(
                ''' SELECT un_id FROM unidades, clientes WHERE cl_nif=%s AND un_cliente_id=cl_id limit 1''', (row[3],))
            if unit_id is None:
                execute_query(
                    '''update hardware set hw_invoice=%s, hw_invoice_date=%s, hw_status_id=1, hw_unit_id=%s where hw_id=%s''',
                    (row[0], row[2], 9999, serial_in_db[0]))
                execute_query(
                    '''insert into missing_units ( ms_nif, ms_client_name, ms_invoice, ms_serial_number) values (%s,%s,%s,%s)''',
                    (row[3], row[5], row[0], row[1]))
                missing_unit += 1
            else:
                execute_query(
                    '''update hardware set hw_invoice=%s, hw_invoice_date=%s, hw_status_id=1, hw_unit_id=%s where hw_id=%s''',
                    (row[0], row[2], unit_id[0], serial_in_db[0]))
                cnt += 1
    cursor.close()
    cnxn.close()
    print('hardware updates', cnt, 'missing units', missing_unit)


sql_server_conn_str = ("Driver={SQL Server Native Client 11.0};"
                       "Server=WIN_SERVER\PRIMAVERAv10;"
                       "Database=PRIESPIRIDIAO;"
                       "uid=sa;pwd=1697fo")
conn_string = 'host=192.168.0.98 dbname=prism user=root password=masterkey'

print('version: 2020-06-02')
# print('sync compras')
# sync_compras(compras())
# print('sync vendas')
# sync_vendas(vendas())
# print (datetime.datetime.now(),';' , format(sync_clientes_cc(), '10.2f').replace(' ', ''), file=open("clientes.log", "a"))
# develop
# show_vendas()
print(datetime.datetime.now())
print(format(sync_clientes_cc(), '10.2f'))
add_new_products()
add_new_hardware()
sales_update()
