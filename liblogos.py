#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint

import lib_css
import datetime
import libpg
import data_sets
import parameters as gl


def assistencia_to_html(as_id):
    assistencia = data_sets.assistencia_to_dict(as_id)
    # gera html
    html = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
              <style> ''' + lib_css.get_lib(1) + '</style></head>'
    
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '</td></tr>\n'
    html += ''' <table>
            '''
    html += div_title + ' Assistencia Técnica<td> ' + div_end
    html += td_caixa + 'Unidade:</td>' + td_data + assistencia['proc_unit_name'] + td_end
    html += td_caixa + 'Referencia:</td>' + td_data + str(assistencia['proc_id']) + td_end
    html += td_caixa + 'Data e hora:</td>' + td_data + assistencia['proc_date'].strftime('%d.%b.%Y %H:%M') + td_end
    html += td_caixa + 'Duração:</td>' + td_data + assistencia['proc_duracao'].strftime("%H:%M:%S") + td_end
    html += td_caixa + 'Contacto:</h3>' + td_data + assistencia['proc_quem'] + '/' + assistencia[
        'proc_contacto'] + td_end
    html += td_caixa + 'Meio:</h3>' + td_data + assistencia['proc_meio'] + td_end
    
    dum_tags = ''
    if assistencia['proc_tags'] is None:
        dum_tags = '''<h3 class="round_tags">Avariado</h3> '''
    else:
        for n in assistencia['proc_tags'].split(','):
            dum_tags += '''<h3 class="round_tags">''' + n + '</h3> '
    html += td_caixa + 'Tags:' + td_data + dum_tags + td_end
    
    if not assistencia['proc_model'] == '':
        try:
            html += td_caixa + 'Modelo:' + td_data + assistencia['proc_model'] + td_end
        except TypeError:
            pass
        try:
            html += td_caixa + 'Num. de Série:' + td_data + assistencia['proc_serial_number'] + td_end
        except TypeError:
            pass
    html += td_caixa + 'Problema:' + td_data + assistencia['proc_reported'] + td_end
    html += td_caixa + 'Relatório:' + td_data + assistencia['proc_report_internal'].replace('\n', '<br>') + td_end
    
    html += td_caixa + 'Relatório p/ Fac.:\n' + td_data + assistencia['proc_relatorio_internal'].replace('\n', '<br>') + td_end
    html += td_caixa + 'Técnico:</h3>' + td_data + assistencia['proc_tecnico'] + td_end
    html += td_caixa + 'Estado:</h3>' + td_data + assistencia['proc_status'] + td_end
    if assistencia['proc_pendente']:
        toto = 'Sim'
    else:
        toto = 'Não'
    html += td_caixa + 'Pendente?:</h3>' + td_data + toto + td_end
    toto = ''
    if assistencia['proc_facturado'] == -1:
        toto = 'Não facturado pelo admin'
    elif assistencia['proc_facturado'] != None and assistencia['proc_facturar'] is False:
        toto = 'Factura: ' + assistencia['proc_facturado']
    elif assistencia['proc_facturado'] is None and assistencia['proc_facturar']:
        toto = 'A Facturar.'
    elif assistencia['proc_facturado'] is None and assistencia['proc_facturar'] is False:
        toto = 'Não facturavel.'
    html += td_caixa + 'Facturação:</h3>' + td_data + toto + td_end
    html += '</table>\n'
    
    html += '</html>'
    return html


def lic_to_html(lic_dict, lic_type):
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    
    body_text = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline; background:#56C5EA;
                height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_title {color:#000000; font:19px verdana,sans-serif; background:#56C5EA;
                height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:center; } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000;
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:right;
                } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px; padding-left:10px;
                padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; } #label { border: solid #CCC 1.0pt; width="200" text-align: left;
                font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; }
                #label1 { border: solid #CCC 1.0pt; width="200" text-align: left;
                font-family: Verdana; font-size: 15px; color: #333; font-weight: bold; vertical-align: middle; height: 20px;
                </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '</td></tr>\n'
    body_text += ''' <table>'''
    
    body_text += div_title + lic_type + '<td> ' + div_end
    # body_text += td_caixa + 'Referencia:</td>' + td_data + ass_dict['proc_id'] + td_end
    
    body_text += '<tr>  <td id="label1"; colspan="2">Cabeçalho</td> </tr>'
    body_text += td_caixa + 'Designação Comercial' + td_data + lic_dict['dc'] + td_end
    body_text += td_caixa + 'Telefone' + td_data + lic_dict['telefone'] + td_end
    body_text += td_caixa + 'Morada' + td_data + lic_dict['morada'] + td_end
    body_text += td_caixa + 'Localidade' + td_data + lic_dict['localidade'] + td_end
    body_text += td_caixa + 'Código Postal' + td_data + lic_dict['cp1'] + ' ' + lic_dict['cp2'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Sede Social</td> </tr>'
    body_text += td_caixa + 'Designação Social' + td_data + lic_dict['ds'] + td_end
    body_text += td_caixa + 'NIF' + td_data + lic_dict['nif'] + td_end
    body_text += td_caixa + 'Morada' + td_data + lic_dict['morada_sede'] + td_end
    body_text += td_caixa + 'Localidade' + td_data + lic_dict['localidade_sede'] + td_end
    body_text += td_caixa + 'Código Postal' + td_data + lic_dict['cp_sede'] + td_end
    body_text += td_caixa + 'Capital Social' + td_data + lic_dict['cs'] + td_end
    body_text += td_caixa + 'Reg. C.R.C.' + td_data + lic_dict['crc'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Conteudo da Licença</td> </tr>'
    body_text += td_caixa + 'Versão Comercial' + td_data + lic_dict['commercial_version'] + td_end
    body_text += td_caixa + 'Tipo Software' + td_data + lic_dict['software_name'] + td_end
    body_text += td_caixa + 'Postos adicionais' + td_data + lic_dict['terminals'] + td_end
    body_text += td_caixa + 'Série' + td_data + lic_dict['serie'] + td_end
    body_text += td_caixa + 'Sector' + td_data + lic_dict['sector'] + td_end
    body_text += td_caixa + 'Data de Validade' + td_data + lic_dict['date_valid'] + td_end
    if lic_dict['consolidate'] == '1':
        body_text += td_caixa + 'Sede Consolidada' + td_data + lic_dict['consolidate'] + td_end
    body_text += td_caixa + 'Stocks/Compras/C.Correntes' + td_data + lic_dict['stocks'] + td_end
    body_text += td_caixa + 'Sucursais Adicionais' + td_data + lic_dict['succ_add'] + td_end
    body_text += td_caixa + 'Web Service ligações adicionais' + td_data + lic_dict['webserviceadd'] + td_end
    try:
        body_text += td_caixa + 'Imprime Directamente' + td_data + lic_dict['printon'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Remote Desktop' + td_data + lic_dict['rdp'] + td_end
    except KeyError:
        pass
    body_text += td_caixa + 'Data do Contracto' + td_data + lic_dict['date_contract'] + td_end
    body_text += td_caixa + 'P.V.P.' + td_data + str(lic_dict['total_public']) + td_end
    body_text += td_caixa + 'Pedido por' + td_data + lic_dict['who'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Comentários</td> </tr>'
    body_text += '</table>'
    body_text += lic_dict['comments'].replace('\n', '<br>')
    body_text += '</html>'
    return body_text


def lic_view(lic_dict, lic_type):
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    
    body_text = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline; background:#56C5EA;
                height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_title {color:#000000; font:19px verdana,sans-serif; background:#56C5EA;
                height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:center; } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000;
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:right;
                } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px; padding-left:10px;
                padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; } #label { border: solid #CCC 1.0pt; text-align: center;
                font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; }
                #label1 { border: solid #CCC 1.0pt; text-align: center;
                font-family: Verdana; font-size: 15px; color: #333; font-weight: bold; vertical-align: middle; height: 20px;
                </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '</td></tr>\n'
    body_text += ''' <table>'''
    
    body_text += div_title + lic_type + '<td> ' + div_end
    # body_text += td_caixa + 'Referencia:</td>' + td_data + ass_dict['proc_id'] + td_end
    
    body_text += '<tr>  <td id="label1"; colspan="2">Cabeçalho</td> </tr>'
    body_text += td_caixa + 'Designação Comercial' + td_data + lic_dict['dc'] + td_end
    body_text += td_caixa + 'Telefone' + td_data + lic_dict['telefone'] + td_end
    body_text += td_caixa + 'Morada' + td_data + lic_dict['morada'] + td_end
    body_text += td_caixa + 'Localidade' + td_data + lic_dict['localidade'] + td_end
    body_text += td_caixa + 'Código Postal' + td_data + lic_dict['cp1'] + ' ' + lic_dict['cp2'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Sede Social</td> </tr>'
    body_text += td_caixa + 'Designação Social' + td_data + lic_dict['ds'] + td_end
    body_text += td_caixa + 'NIF' + td_data + lic_dict['nif'] + td_end
    try:
        body_text += td_caixa + 'Morada' + td_data + lic_dict['morada_sede'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Localidade' + td_data + lic_dict['localidade_sede'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Código Postal' + td_data + lic_dict['cp_sede'] + td_end
    except KeyError:
        pass
    body_text += td_caixa + 'Capital Social' + td_data + lic_dict['cs'] + td_end
    body_text += td_caixa + 'Reg. C.R.C.' + td_data + lic_dict['crc'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Conteudo da Licença</td> </tr>'
    body_text += td_caixa + 'Versão Comercial' + td_data + lic_dict['software'] + td_end
    try:
        body_text += td_caixa + 'Tipo Software' + td_data + lic_dict['software_name'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Postos adicionais' + td_data + lic_dict['terminals'] + td_end
    except KeyError:
        body_text += td_caixa + 'Postos adicionais' + td_data + lic_dict['units'] + td_end
    body_text += td_caixa + 'Data de Validade' + td_data + lic_dict['date_valid'] + td_end
    try:
        if lic_dict['consolidate'] == '1':
            body_text += td_caixa + 'Sede Consolidada' + td_data + lic_dict['consolidate'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Relógio de Ponto' + td_data + lic_dict['clockin'] + td_end
    except KeyError:
        body_text += td_caixa + 'Relógio de Ponto' + td_data + '' + td_end
    try:
        body_text += td_caixa + 'Stocks/Compras/C.Correntes' + td_data + lic_dict['stocks'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Backup Off-Site' + td_data + lic_dict['backupoff'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Gestão de Mesas' + td_data + lic_dict['gestm'] + td_end
    except KeyError:
        pass
    try:
        body_text += td_caixa + 'Versão Binario' + td_data + lic_dict['version'] + td_end
    except KeyError:
        pass
    body_text += td_caixa + 'Data do Contracto' + td_data + lic_dict['date_contract'] + td_end
    body_text += td_caixa + 'P.V.P.' + td_data + str(lic_dict['total_public']) + td_end
    try:
        body_text += td_caixa + 'Pedido por' + td_data + lic_dict['who'] + td_end
    except KeyError:
        pass
    body_text += '<tr>  <td id="label1"; colspan="2">Comentários</td> </tr>'
    body_text += '</table>'
    body_text += lic_dict['comments'].replace('\n', '<br>')
    body_text += '</html>'
    return body_text


def eorder_to_html(lic_dict, lic_type):
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    
    body_text = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline; background:#56C5EA;
                height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_title {color:#000000; font:19px verdana,sans-serif; background:#56C5EA;
                height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:center; } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000;
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:right;
                } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px; padding-left:10px;
                padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; } #label { border: solid #CCC 1.0pt; text-align: center;
                font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; height: 20px; }
                #label1 { border: solid #CCC 1.0pt; text-align: center;
                font-family: Verdana; font-size: 15px; color: #333; font-weight: bold; vertical-align: middle; height: 20px;
                </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '</td></tr>\n'
    body_text += ''' <table>'''
    
    body_text += div_title + lic_type + '<td> ' + div_end
    body_text += '<tr>  <td id="label1"; colspan="2">Cabeçalho</td> </tr>'
    body_text += td_caixa + 'Designação Comercial' + td_data + lic_dict['dc'] + td_end
    body_text += td_caixa + 'Morada' + td_data + lic_dict['morada'] + td_end
    body_text += td_caixa + 'Localidade' + td_data + lic_dict['localidade'] + td_end
    body_text += td_caixa + 'Código Postal' + td_data + lic_dict['cp1'] + ' ' + lic_dict['cp2'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Sede Social</td> </tr>'
    body_text += td_caixa + 'Designação Social' + td_data + lic_dict['ds'] + td_end
    body_text += td_caixa + 'NIF' + td_data + lic_dict['nif'] + td_end
    body_text += td_caixa + 'Morada' + td_data + lic_dict['morada'] + td_end
    body_text += td_caixa + 'Localidade' + td_data + lic_dict['localidade'] + td_end
    body_text += td_caixa + 'Código Postal' + td_data + lic_dict['cp1'] + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Conteudo da Licença</td> </tr>'
    body_text += td_caixa + 'Versão Comercial' + td_data + lic_dict['software'] + td_end
    body_text += td_caixa + 'Password' + td_data + lic_dict['password'] + td_end
    body_text += td_caixa + 'Serie' + td_data + lic_dict['serie'] + td_end
    body_text += td_caixa + 'Data de Validade' + td_data + lic_dict['date_valid'] + td_end
    body_text += td_caixa + 'P.V.P.' + td_data + str(lic_dict['total_public']) + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Comentários</td> </tr>'
    body_text += '</table>'
    body_text += lic_dict['comments'].replace('\n', '<br>')
    body_text += '</html>'
    return body_text


def log_conta(conta, msg):
    toto = datetime.datetime.now().strftime('%d.%m.%Y %H:%M') + ' ' + msg + '''\n'''
    libpg.execute_query('UPDATE contas set ct_log = %s || ct_log where ct_id = %s;', (toto, conta))


def make_ass_html(ass_dict, mode=0):
    LF = '\n'
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    
    div_label = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_conner'>'''
    div_value = '''<h3 class="round_small">'''
    toto = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline; 
                background:#56C5EA; height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px; 
                padding-bottom:3px; padding-top:2px; text-align:right; } .round_title {color:#000000; 
                font:19px verdana,sans-serif; background:#56C5EA; height: 25px; border-radius: 7px; 
                padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:center; 
                } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37 
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; 
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000; 
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; 
                text-align:right; } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px; 
                padding-left:10px; padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; } #label {border: solid #CCC 1.0pt; 
                text-align: center; font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle; 
                height: 20px; } </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '</td></tr>\n'
    toto += ''' <table>
            '''
    toto += div_title + ' Assistencia Técnica<td> ' + div_end
    toto += td_caixa + 'Problema:' + td_data + ass_dict['proc_avaria'] + td_end
    if mode == 0:
        toto += td_caixa + 'Relatório:' + td_data + ass_dict['proc_relatorio_interno'].replace('\n', '<br>') + td_end
    toto += td_caixa + 'Referencia:</td>' + td_data + ass_dict['proc_id'] + td_end
    toto += td_caixa + 'Data e hora:</td>' + td_data + ass_dict['proc_data'] + td_end
    toto += td_caixa + 'Duração:</td>' + td_data + ass_dict['proc_duracao'] + td_end
    toto += td_caixa + 'Unidade:</td>' + td_data + ass_dict['proc_unit_name'] + td_end
    toto += td_caixa + 'Morada:</td>' + td_data + ass_dict['un_morada'] + td_end
    toto += td_caixa + 'Localidade:</td>' + td_data + ass_dict['un_localidade'] + td_end
    toto += td_caixa + 'C.P.:</td>' + td_data + ass_dict['un_cp'] + td_end
    toto += td_caixa + 'N.I.F.:</td>' + td_data + ass_dict['cl_nif'] + td_end
    toto += td_caixa + 'Proprietário:</td>' + td_data + ass_dict['cl_nome'] + td_end
    toto += td_caixa + 'Contacto:</h3>' + td_data + ass_dict['proc_quem'] + '/' + ass_dict['proc_contacto'] + td_end
    toto += td_caixa + 'Meio:</h3>' + td_data + ass_dict['proc_meio'] + td_end
    dum_tags = ''
    for n in ass_dict['proc_tags'].split(','):
        dum_tags += '''<h3 class="round_tags">''' + n + '</h3> '
    toto += td_caixa + 'Tags:' + td_data + str(dum_tags) + td_end
    try:
        toto += td_caixa + 'Modelo:' + td_data + ass_dict['proc_model']
        toto += '<td id="label">' + 'Num. de Série:' + td_data + ass_dict['proc_serial_number'] + td_end
    except TypeError:
        pass
    if mode == 0:
        print('--------Debug---------')
        print('make_ass_html')
        print(ass_dict['proc_report_invoice'])
        print('------end debug-------')
        
        toto += td_caixa + 'Relatório p/ Fac.:\n' + td_data + ass_dict['proc_report_invoice'].replace('\n', '<br>') + td_end
    toto += td_caixa + 'Técnico:</h3>' + td_data + ass_dict['proc_tecnico'] + td_end
    toto += td_caixa + 'Estado:</h3>' + td_data + ass_dict['proc_status'] + td_end
    toto += '</table>\n'
    toto += '</html>'
    return toto


def get_renew_data(cat_date):
    y = datetime.datetime(datetime.datetime.now().date().year, cat_date.month, cat_date.day)
    if y.year == datetime.datetime.now().date().year:
        y = datetime.datetime(datetime.datetime.now().date().year + 1, cat_date.month, cat_date.day)
    
    return get_end_day(y)


def next_day_of_week(date):
    today = datetime.date.today()
    today = date
    next_monday = today + datetime.timedelta(days=-date.weekday() + randint(0, 2), weeks=1)
    return next_monday


def get_end_day(date_to):
    dt = datetime.datetime(date_to.year, date_to.month, date_to.day)
    if date_to.month in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        pass
    else:
        if date_to.month == 12:
            if date_to.day > 17:
                dt = datetime.datetime(date_to.year, 1, 7)
            else:
                pass
        elif date_to.month == 1:
            if date_to.day < 6:
                dt = datetime.datetime(date_to.year, 1, 7)
            else:
                pass
    return next_day_of_week(dt)


def add_unit_contacts(ct_type, unit):
    libpg.execute_query('''INSERT INTO contacts (ct_ctt_id, ct_unit, ct_value1, ct_value2) VALUES (%s, %s, %s, %s) ''',
                        (ct_type, unit, '', ''))
    return libpg.query_one('SELECT ct_id FROM contacts ORDER BY ct_id DESC LIMIT 1', (True,))[0]


def edit_unit_contacts(index, value1, value2):
    libpg.execute_query('''UPDATE contacts SET ct_value1 =%s, ct_value2 = %s
                           where ct_id = %s ''',
                        (value1, value2, index))


def edit_unit_settings(index, value1, value2):
    libpg.execute_query('''UPDATE unit_settings SET us_value1 =%s, us_value2 = %s
                                WHERE us_id = %s''',
                        (value1, value2, index))


def add_unit_setting(unit, setting, value1='', value2=''):
    libpg.execute_query('''INSERT INTO unit_settings (us_unit_id, us_act_id, us_value1, us_value2)
                                VALUES (%s, %s, %s, %s);''',
                        (unit, setting, value1, value2))
    # ''' o ultimo registo criado, para que possa ser editado'''


def get_unit_setting1(un_id, unit_setting_id):
    setting_values = libpg.query_one('select us_value1 from unit_settings where us_unit_id=%s and us_act_id=%s',
                                     (un_id, unit_setting_id))
    if setting_values is None:
        return 'N/D'
    else:
        return setting_values[0]


def add_unit_comitment(unit, cm_act_id, value, invoice=None, reset=False):
    if reset:
        libpg.execute_query('''update comitments_unit set cm_archive = True where cm_unit_id=%s and cm_act_id=%s''',
                            (unit, cm_act_id))
    libpg.execute_query(
        '''INSERT INTO comitments_unit (cm_value, cm_invoice, cm_unit_id,cm_act_id) VALUES (%s, %s, %s, %s) ''',
        (value, invoice, unit, cm_act_id))


def set_unit_comitment(unit, cm_act_id, value, invoice=None):
    libpg.execute_query(
        '''update comitments_unit set cm_value= %s, cm_invoice=%s where cm_unit_id = %s and cm_act_id = %s''',
        (value, invoice, unit, cm_act_id))


def change_logic_unit_comitment(unit, cm_act_id):
    a = libpg.query_one('''select cm_value from comitments_unitwhere cm_unit_id=%s and cm_act_id = %s ''',
                        (unit, cm_act_id))[0]
    if a == 'Sim':
        libpg.execute_query('''update comitments_unit set cm_value= %s where cm_unit_id = %s and cm_act_id = %s''',
                            ('Não', unit, cm_act_id))
    elif a == 'Não':
        libpg.execute_query('''update comitments_unit set cm_value= %s where cm_unit_id = %s and cm_act_id = %s''',
                            ('Sim', unit, cm_act_id))


def get_unit_tickets(unit_id):
    a = libpg.sql_query(
        '''select cm_value from comitments_unit where cm_act_id = 25 and cm_unit_id = ''' + str(unit_id))
    if a == []:
        # insere o tickets
        libpg.execute_query('''INSERT INTO comitments_unit (cm_value,  cm_unit_id,cm_act_id) VALUES (%s, %s, %s) ''',
                            (0, unit_id, 25))
        return 0
    else:
        return a[0][0]


def get_users(unit_id):
    a = libpg.sql_query(
        '''select cm_value from comitments_unit where cm_act_id = 18 and cm_unit_id = ''' + str(unit_id))
    if a == []:
        # insere o tickets
        libpg.execute_query('''INSERT INTO comitments_unit (cm_value,  cm_unit_id,cm_act_id) VALUES (%s, %s, %s) ''',
                            (0, unit_id, 18))
        return 0
    else:
        return a[0][0]


def log_actions(user_dict, what, comments=''):
    a = libpg.execute_query('insert into log (lg_what, lg_who, lg_comments) values (%s, %s, %s)',
                            (user_dict['user_name'], what, comments))


def licence_to_dict(software_id):
    """acede com]"""
    # params.conn_string = "host=" + params.db_host + " dbname=" + params.db_database + " user=" + params.db_user + " password=" + params.db_password
    conn = psycopg2.connect(gl.conn_string)
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = '''SELECT
              software.sf_id,
              software_type.sft_software ,
              software.sf_date_contract,
              software.sf_date_valid,
              (case when software.sf_active = True then 'Activo '
                else
                    'Inactivo'
                end) as status, software.sf_lic_type,
                software.sf_lic_json
            FROM
              software,
              software_type
            WHERE
              software.sf_id = %s and
              software.sf_version = software_type.sft_id
             '''
    dict_cur.execute(sql, (software_id,))
    rec = dict_cur.fetchone()
    return rec


def update_unit_tags(id, t_list):
    # id = unidade
    dum = t_list.rstrip(',')
    tags_list = dum.split(',')
    if tags_list[0] == '':
        cleantag_rfs = libpg.execute_query('delete from tag_un_refs where tag_unit_id = %s', (id,))
    else:
        cleantag_rfs = libpg.execute_query('delete from tag_un_refs where tag_unit_id = %s', (id,))
    tags_id = []
    tag_max = libpg.query_one('''Select max(tau_id)+1 as t from tags_unit''', (True,))[0]
    # print tag_max
    for n in tags_list:
        c = n.lower().strip()
        if c != '':
            a = libpg.query_one('select tau_id from tags_unit where tau_name = %s', (c,))
            if a == None:  # é nova
                libpg.execute_query('insert into tags_unit (tau_name) values(%s)', (c,))
                tags_id.append((id, tag_max))
                tag_max += 1
            else:
                tags_id.append((id, a[0]))
    sql = ''' INSERT INTO tag_un_refs (tag_unit_id, tau_tag_id) VALUES''' + str(tags_id)[1:-1]
    libpg.execute_query(sql, (True,))


def update_model_tags(model_id, t_list):
    dum = t_list.rstrip(',')
    tags_list = dum.split(',')
    libpg.execute_query('delete from tag_md_refs where tam_model_id = %s', (model_id,))
    tags_id = []
    tag_max = libpg.query_one('''Select max(tam_id)+1 as t from tags_model''', (True,))[0]
    for n in tags_list:
        c = n.lower().strip()
        if c != '':
            a = libpg.query_one('select tam_id from tags_model where tam_name = %s', (c,))
            if a == None:  # é nova
                libpg.execute_query('insert into tags_model (tam_name) values(%s)', (c,))
                tags_id.append((model_id, tag_max))
                tag_max += 1
            else:
                tags_id.append((model_id, a[0]))
    sql = ''' INSERT INTO tag_md_refs (tam_model_id, tam_tag_id) VALUES''' + str(tags_id)[1:-1]
    libpg.execute_query(sql, (True,))


def set_unit_comitments(unit_id, cm_act_id, value):
    a = libpg.query_one('''select cm_id from comitments_unit where cm_unit_id=%s and cm_act_id=%s''',
                        (unit_id, cm_act_id))
    if a == None:
        libpg.execute_query('''insert into comitments_unit (cm_unit_id, cm_act_id, cm_value) VALUES(%s,%s,%s)''',
                            (unit_id, cm_act_id, value))
    else:
        libpg.execute_query('''update comitments_unit set cm_value=%s where cm_unit_id=%s and cm_act_id=%s''',
                            (value, unit_id, cm_act_id))


def set_unit_settings(unit_id, us_act_id, value, v2=''):
    unit_setting_id = libpg.query_one('''SELECT us_id FROM unit_settings WHERE us_unit_id=%s AND us_act_id=%s''',
                                      (unit_id, us_act_id))
    if unit_setting_id is None:
        libpg.execute_query(
            '''INSERT INTO unit_settings (us_unit_id,us_act_id, us_value1, us_value2) VALUES(%s,%s,%s, %s)''',
            (unit_id, us_act_id, value, v2))
    else:
        libpg.execute_query(
            '''UPDATE unit_settings SET us_value1=%s, us_value2=%s WHERE us_id=%s''', (value, v2, unit_setting_id))


def get_install_date(unit_id):
    a = libpg.query_one('''SELECT us_id FROM unit_settings WHERE us_unit_id=%s AND us_act_id=%s''', (unit_id, 11))
    if a is None:
        return False
    else:
        return True


def scall_same_unit(unit_it, call_id):
    a = libpg.query_one('''SELECT proc_id FROM assistencias WHERE proc_unit_id=%s and proc_id=%s''', (unit_it, call_id))
    if a is None:
        return False
    else:
        return True


def get_unit_version(unit_it):
    a = libpg.query_one('''SELECT us_value2 from unit_settings WHERE us_unit_id=%s AND us_act_id=%s''', (unit_it, 1))
    if a is None:
        return '2013.1'
    else:
        return a[0]


def get_dbms_version(unit_it):
    a = libpg.query_one('''SELECT us_value1 from unit_settings WHERE us_unit_id=%s AND us_act_id=%s''', (unit_it, 8))
    if a is None:
        return 'ports 8.1'
    else:
        return a[0]


def get_sys_admin(unit_it):
    a = libpg.query_one('''SELECT ct_value1,ct_value2 from contacts WHERE ct_unit=%s AND ct_ctt_id=%s''', (unit_it, 11))
    if a is None:
        return False, ''
    else:
        return True, a[0], a[1]


def order_mark_upload(unit_id):
    """ pode carregar sem restrições mesmo se já tiver carregada """
    lic_status: int = 3
    sql = '''SELECT sf_id FROM software WHERE sf_status = 0 AND sf_unit_id =%s ORDER BY sf_id DESC LIMIT 1'''
    try:
        lic_number = libpg.query_one(sql, (unit_id,))[0]
        """coloca a lic em carregada """
        libpg.execute_query('update software set sf_status=1 where sf_id=%s', (lic_number,))
    except TypeError:
        sql = '''SELECT sf_id FROM software WHERE sf_unit_id =%s ORDER BY sf_id DESC LIMIT 1'''
        lic_number = libpg.query_one(sql, (unit_id,))[0]
        # print('TypeError')
        # print('get last lic ', lic_number)
        # print('re-upload')
        # '''já foi carregada e actualizada e activa passa a re-carregada'''
        # lic_status = 3
    """coloca todas em 5 substituida """
    libpg.execute_query('update software set sf_status=5 where sf_status = 3 and sf_unit_id=%s', (unit_id,))
    """ cria novo registo do que foi carregado """
    sql = '''INSERT INTO software (sf_unit_id, sf_lic_json, sf_version, sf_date_contract,
                sf_date_valid, sf_lic_type,sf_json_version, sf_status, sf_who)
                SELECT sf_unit_id, sf_lic_json, sf_version, sf_date_contract,
                sf_date_valid, sf_lic_type,sf_json_version, %s, %s
                FROM software where sf_id= %s'''
    data = (lic_status, gl.user_dict['user_name'], lic_number)
    libpg.execute_query(sql, data)

    return lic_number


def hardware_update_settings(unit_id):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    setting_id = libpg.query_one('''select us_id from unit_settings where us_unit_id = %s and us_act_id = 25''',
                                 (unit_id,))
    if setting_id is None:
        libpg.execute_query(
            '''INSERT INTO unit_settings (us_unit_id, us_act_id, us_value1, us_value2) VALUES (%s,25,%s,%s)''',
            (unit_id, dt, gl.user_dict['user_name']))
    else:
        libpg.execute_query('''UPDATE unit_settings  SET us_value1=%s, us_value2=%s WHERE us_id=%s''',
                            (dt, gl.user_dict['user_name'], setting_id[0]))


def software_update_settings(unit_id):
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    setting_id = libpg.query_one('''select us_id from unit_settings where us_unit_id = %s and us_act_id = 26''',
                                 (unit_id,))
    if setting_id is None:
        libpg.execute_query(
            '''INSERT INTO unit_settings (us_unit_id, us_act_id, us_value1, us_value2) VALUES (%s,26,%s,%s)''',
            (unit_id, dt, gl.user_dict['user_name']))
    else:
        libpg.execute_query('''UPDATE unit_settings  SET us_value1=%s, us_value2=%s WHERE us_id=%s''',
                            (dt, gl.user_dict['user_name'], setting_id[0]))


def process_to_html(ass_dict):
    # LF = '\n'
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    
    # div_label = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_conner'>'''
    # div_value = '''<h3 class="round_small">'''
    toto: str = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
                <style> .round_conner {color:#000000; font:14px verdana,sans-serif; display: inline;
                background:#56C5EA; height: 25px; border-radius: 7px; padding-left:10px; padding-right:10px;
                padding-bottom:3px; padding-top:2px; text-align:right; } .round_title {color:#000000;
                font:19px verdana,sans-serif; background:#56C5EA; height: 25px; border-radius: 7px;
                padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px; text-align:center;
                } .round_small {color:#FFDF00; font:14px verdana,sans-serif; display: inline; background:#6F4E37;6F4E37
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .round_tags {color:#ffffff; font:10px verdana,sans-serif; display: inline; background:#6FD000;
                height: 25px; border-radius: 4px; padding-left:10px; padding-right:10px; padding-bottom:3px; padding-top:2px;
                text-align:right; } .terminal {color:#00DD00; font:14px verdana,sans-serif; background-color:#000000; border-radius: 6px;
                padding-left:10px; padding-right:10px; padding-bottom:4px; padding-top:2px; text-align:left; } 
                #label {border: solid #CCC 1.0pt;
                text-align: right; font-family: Verdana; font-size: 10px; color: #333; font-weight: bold; vertical-align: middle;
                height: 20px; width:100px  } </style> </head>'''
    td_caixa = '<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '</td></tr>\n'
    toto += ''' <table>'''
    toto += div_title + ass_dict['proc_type'] + ' #' + str(ass_dict['proc_id']) + '/' + ass_dict['proc_date'].strftime("%d-%m-%Y %H:%M") + div_end  #' Assistencia Técnica<td> ' + div_end
    toto += td_caixa + 'Unidade:</td>' + td_data + ass_dict['proc_unit_name'] + td_end
    toto += td_caixa + 'Problema:' + td_data + ass_dict['proc_reported'] + td_end
    toto += td_caixa + 'Relatório:' + td_data + ass_dict['proc_report_internal'].replace('\n', '<br>') + td_end
    toto += td_caixa + 'Meio:</h3>' + td_data + ass_dict['proc_meio'] + td_end
    if not ass_dict['proc_quem'] == '':
        toto += td_caixa + 'Contacto:</h3>' + td_data + ass_dict['proc_quem'] + ' ' + ass_dict['proc_contacto'] + td_end
    toto += '</table>\n'
    toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="6">'
    toto += ''' <table>'''
    # toto += td_caixa + 'Data e hora:</td>' + td_data + ass_dict['proc_date'].strftime("%d-%m-%Y %H:%M") + td_end
    if ass_dict['proc_duracao'].second == 00:
        toto += td_caixa + 'Duração:</td>' + td_data + ass_dict['proc_duracao'].strftime("%H:%M") + td_end
    else:
        toto += td_caixa + 'Duração:DEBUG</td>' + td_data + ass_dict['proc_duracao'].strftime("%H:%M") + td_end
    toto += td_caixa + 'Morada:</td>' + td_data + ass_dict['un_morada'] + td_end
    toto += td_caixa + 'Localidade:</td>' + td_data + ass_dict['un_localidade'] + td_end
    toto += td_caixa + 'C.P.:</td>' + td_data + ass_dict['un_cp'] + td_end
    toto += '</table>\n'
    toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="6">'
    toto += ''' <table>'''
    toto += td_caixa + 'Proprietário:</td>' + td_data + ass_dict['cl_nome'] + td_end
    toto += td_caixa + 'N.I.F.:</td>' + td_data + ass_dict['cl_nif'] + td_end
    toto += td_caixa + 'Morada:</td>' + td_data + ass_dict['cl_morada'] + td_end
    toto += td_caixa + 'Sede C.P.:</td>' + td_data + ass_dict['cl_cp'] + td_end
    toto += td_caixa + 'C. Corrente:</td>' + td_data + '{0:.2f}'.format(ass_dict['cl_cc']) + td_end
    
    try:
        toto += td_caixa + 'Modelo:' + td_data + ass_dict['proc_model']
    except TypeError:
        pass
    try:
        toto += '<td id="label">' + 'Num. de Série:' + td_data + ass_dict['proc_serial_number'] + td_end
    except TypeError:
        pass
    try:
        toto += td_caixa + 'Relatório p/ Fac.:\n' + td_data + ass_dict['proc_report_invoice']
    except (TypeError, AttributeError):
        pass
    if not ass_dict['proc_tecnico'] == '':
        toto += td_caixa + 'Técnico:</h3>' + td_data + ass_dict['proc_tecnico'] + td_end
    else:
        toto += td_caixa + 'Técnico:</h3>' + td_data + ass_dict['proc_user'].upper() + td_end
    toto += td_caixa + 'Recebido:</h3>' + td_data + ass_dict['proc_user'] + td_end
    toto += td_caixa + 'Estado:</h3>' + td_data + ass_dict['proc_status'] + td_end
    toto += '</table>\n'
    toto += '</html>'
    # print(toto, file=open("output.html", "a"))
    return toto


def msg_to_html(msg_dict):
    # LF = '\n'
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    toto: str = '''<html>
                  <head>
                    <title>m</title>
                    '''

    toto += '''<pre>''' + msg_dict['msg_type_name'] + ' @' + msg_dict['msg_date_time'].strftime("%d-%m-%Y %H:%M") + '''<br></pre>'''
    toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="4">'
    toto += '''<pre> Unidade: ''' + msg_dict['un_nome'] + '''</pre>'''
    toto += '''<pre>    Para: ''' + msg_dict['msg_to_name'] + ' / ' + msg_dict['msg_to'] + '''</pre>'''
    if msg_dict['msg_type_id'] == 2:
        toto += '''<code> Assunto''' + msg_dict['msg_subject'] + '''<br></code>'''
    toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="6">'
    toto += '''<code> ''' + msg_dict['msg_body'] + '''<br></code>'''
    toto += '<hr style="border: 1px dashed #C0C0C0" color="#FFFFFF" size="6">'
    toto += '''<pre> ''' + msg_dict['msg_date_time'].strftime("%d-%m-%Y %H:%M") + ' ' + msg_dict['msg_who'] + '''</pre>'''
    toto += '</html>'
    # print(toto, file=open("output.html", "a"))
    return toto


if __name__ == '__main__':
    pass
