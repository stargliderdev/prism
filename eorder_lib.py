#!/usr/bin/python
# -*- coding: utf-8 -*-
import lib_css
import datetime
import libpg
import data_sets


def to_html(lic_dict, lic_type):
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
    
    body_text += '<tr>  <td id="label1"; colspan="2">Cliente</td> </tr>'
    body_text += td_caixa + 'Designação Comercial' + td_data + lic_dict['dc'] + td_end
    body_text += td_caixa + 'Designação Social' + td_data + lic_dict['ds'] + td_end
    body_text += td_caixa + 'NIF' + td_data + lic_dict['nif'] + td_end
    body_text += '''<tr>  <td id="label1"; colspan="2">Conteudo da Licença</td> </tr>'''
    body_text += td_caixa + '''Ligações ''' + td_data + str(int(lic_dict['connections']) + 1) + td_end
    body_text += td_caixa + '''Ligações Adicionais''' + td_data + lic_dict['connections'] + td_end
    if not lic_dict['invoice'] == '':
        body_text += td_caixa + '''Facturação''' + td_data + lic_dict['invoice'] + td_end
    body_text += td_caixa + '''Serie''' + td_data + lic_dict['serie'] + td_end
    body_text += td_caixa + '''Password''' + td_data + lic_dict['password'] + td_end
    try:  # v 2.8.2
        body_text += td_caixa + 'Data de Validade' + td_data + lic_dict['date_valid'] + td_end
    except:
        body_text += td_caixa + 'Data de Validade' + td_data + 'n/d' + td_end
    body_text += td_caixa + 'Total Infornash' + td_data + str(lic_dict['total_infornash']) + td_end
    body_text += '<tr>  <td id="label1"; colspan="2">Comentários</td> </tr>'
    body_text += '</table>'
    body_text += lic_dict['comments'].replace('\n', '<br>')
    body_text += '</html>'
    return body_text


if __name__ == '__main__':
    pass