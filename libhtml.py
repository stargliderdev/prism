# -*- coding: utf-8 -*-
import sys


def make_table(css_name,title,dataset,header=''):
    #sql = 'select mc_id, mc_nome, mc_freguesia, mc_concelho, mc_distrito from mercados order by mc_nome'
    #data_set = db.output_query(sql) 

    if css_name == 'green':
        css = '<style type="text/css">#customers\
            {font-family:"Tahoma", Arial, Helvetica, sans-serif;width:100%;border-collapse:collapse;}\
            #customers td, #customers th {font-size:1em;border:1px solid #98bf21;padding:3px 7px 2px 7px;}\
            #customers th {font-size:14px;font-weight:bold;text-align:center;padding-top:1px;padding-bottom:1px;background-color:#A7C942;color:#000000;}\
            #customers tr.alt td {color:#0000px00;background-color:#EAF2D3;}\
            #right-cell {text-align: right;}</style></head>'
    elif css_name == 'green_small':
        css = '<style type="text/css">#customers\
            {font-family:"Tahoma", Arial, Helvetica, sans-serif;width:100%;border-collapse:collapse;}\
            #customers td, #customers th {font-size:1em;border:1px solid #98bf21;padding:1px 1px 1px 1px;}\
            #customers th {font-size:14px;font-weight:bold;text-align:center;padding-top:1px;padding-bottom:1px;background-color:#A7C942;color:#000000;}\
            #customers tr.alt td {color:#0000px00;background-color:#EAF2D3;}\
            #right-cell {text-align: right;}</style></head>'
    css_table_header = 'customers'

    html_header = '<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"><title>' + title + '</title>'
    listToHtml = ''
    if header == '':
        row_header = '<table id="' + css_table_header + '"> '
    else:
        print('create_header')
        row_header = create_header(css_table_header,header)

    listToHtml = create_lines(dataset)
    
    toto = html_header + css + '<body>' + row_header + listToHtml + '</table></body></html>'
    return toto

def create_header(css_style,header):
    toto = '<table id="' + css_style + '"> <tr>' 
    for n in header: #['<th>id</th>', '<th>Nome da Feira ^</th>','<th>Freguesia</th>','<th>Concelho</th>','<th>Distrito</th>']:
        toto +=  '<th>' +  n  +'</th>' #pply_style('#customers th', n)
    toto += '</tr>'
    return toto

def create_lines(dataset, stripes = True):
    toto = ''
    odd = True
    col1 = True
    for n in dataset:
        if odd:
          dum = '<tr class="alt">'
        else:
            dum =  '<tr>'
        for tr in n: # dados
            if type(tr) == int:
                dum += '<td id="right-cell">' + str(tr) + '</td>'
            else:
                if col1:
                    dum += '<td align="right">' + str(tr) + '</td>'
                else:
                    dum += '<td>' + str(tr) + '</td>'
                col1 = not(col1) 
        if stripes : odd = not(odd)
        toto += dum + '</tr>'
    return toto





def format_report(texto):
    toto = texto.replace('\n','<br>')
    return toto