#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ftplib
import parameters as gl

def get_lic(nif='*'):
    u = 'espiridiao@infornash.pt'
    # u = gl.file1[0]
    # descarrega do ftp
    # a = 4250040
    # p = gl.file1[1]
    # Connection information
    server = 'ftp.infornash.pt'
    # u = u[:10]
    # p = str(a*2+1)
    # Directory and matching information
    directory = '/lic'
    # Establish the connection
    try:
        ftp = ftplib.FTP(gl.file1[2],timeout=15)
        ftp.login(gl.file1[0], gl.file1[1])
    except Exception as err:
        return False, 'Erro ao ligar ao FTP:' + str(err)
    # Change to the proper directory
    ftp.cwd(directory)
    files = []
    try:
        files = ftp.nlst('*' + nif + '*')
        ftp.quit()
        return True,ftp_to_list(files)
    except Exception as resp:
        return False, str(resp)


def ftp_to_list(mask):
    f = []
    dx = {}
    for n in mask:
        dx = {}
        d = n.rfind('.rar')
        a = n[:d]
        d = a.find('-')
        name = a[:d].replace('_',' ').title()
        g = a[d+1:].split('-')
        nif = g[0]
        version = g[1]
        f.append((name,nif,version,n))
    hl = sorted(f, key=lambda student: student[2], reverse=True)
    return hl

def send_lic_ftp(file_ftp):
    try:
        file_name = file_ftp[file_ftp.rfind('/')+1:]
        session = ftplib.FTP(gl.file1[2],gl.file1[0],gl.file1[1], timeout=5)
        myfile = open(file_ftp,'rb')

        file_name = make_file_name(file_name, gl.PRODUCTION_VERSION)
        session.cwd('/lic/')
        session.storbinary('STOR ' + file_name, myfile)
        myfile.close()
        session.quit()
        return True, file_ftp + 'OK!'
    except Exception as resp:
        return False, str(resp)
        

def get_lic_ftp(filename, t_file):
    try:
        session = ftplib.FTP(gl.file1[2], gl.file1[0], gl.file1[1], timeout=5)
        session.cwd('/lic/')
        lic_file = open('c:\\tmp\\' + t_file, 'wb')
        session.retrbinary('RETR %s' % filename, lic_file.write)
        # Clean up time
        session.quit()
        # lic_file.close()
        return True, filename + ' OK!'
    except Exception as resp:
        return False, str(resp)

def make_file_name(f, v='2015.03'):
    k = f.rfind('_')
    f = f[:k]+'-'+f[k+1:]
    return f.replace('.rar','-' + v + '.rar')

def ftp_get_list(mask):
    f = []
    dx = {}
    for n in mask:
        dx = {}
        d = n.rfind('.rar')
        a = n[:d]
        d = a.find('-')
        name = a[:d].replace('_',' ').title()
        g = a[d+1:].split('-')
        nif = g[0]
        version = g[1]
        f.append((name,nif,version,n))
    hl = sorted(f, key=lambda student: student[2], reverse=True)
    return hl

if __name__ == '__main__':
    print('run it')