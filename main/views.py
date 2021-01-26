from django.shortcuts import render, HttpResponse
import sys
import os
import hashlib
import hmac
import base64
import requests
import urllib
import time
import json
import MySQLdb

# Create your views here.

def index(reqst):
    return render(reqst, 'main/index.html')

config = {
    'host': '211.252.87.118',
    'user': 'admin',
    'password': 'admin1234',
    'database': 'intern',
    'port': 11000,
    'charset': 'utf8',
    'use_unicode': True
}

apikey = {'api_key': 'wE5RQFjA0fCx7UK_mFjiwir699ajBho6OgFrokxShnc_74WvWRhlFXxt1PJ14P-GP-ngAwpMIXy7tkb9GP2oQA',
          'secret_key': "VC6_trYKxTyx1eCwS1LYy7AdiVHkdoq5Av99U5Kgoj8rrxntJuxPkzNEqPm4rRPE-9evXOfTY2rXILP66vOKxA"}


def listAPI(key, command, v):
    baseurl = 'https://api.ucloudbiz.olleh.com/server/v{}/client/api?'.format(str(v))
    rq = dict()
    rq['apikey'] = key['api_key']
    rq['command'] = command
    rq['response'] = 'json'
    secret_key = key['secret_key']
    secret_key = bytes(secret_key, 'UTF-8')
    request_str = '&'.join(['='.join([k, urllib.parse.quote_plus(rq[k])]) for k in rq.keys()])
    make_request = bytes(request_str, 'UTF-8')
    signatureKey = urllib.parse.quote_plus(
        base64.b64encode(hmac.new(secret_key, make_request.lower(), digestmod=hashlib.sha1).digest()))
    req = baseurl + request_str + '&signature=' + signatureKey
    print(req)
    res = json.loads(urllib.request.urlopen(req).read())
    return res



def listVM(key: dict):
    ls = []
    command = 'listVirtualMachines'
    for v in [1, 2]:
        res = listAPI(key, command, v)
        for r in res['listvirtualmachinesresponse']['virtualmachine']:
            dict = {}
            dict['name'] = r['displayname']
            dict['state'] = r['state']
            dict['ip'] = r['nic'][0]['ipaddress']
            dict['zone'] = r['zonename']
            try:
                dict['key'] = r['keypair']
            except:
                dict['key'] = ''
            ls.append(dict)
    return ls

def listPort(key: dict):
    ls = []
    command = 'listPortForwardingRules'
    for v in [1, 2]:
        res = listAPI(key, command, v)
        for r in res['listportforwardingrulesresponse']['portforwardingrule']:
            dict = {}
            dict['name'] = r['virtualmachinedisplayname']
            dict['port'] = r['publicport']
            dict['publicIp'] = r['ipaddress']
            dict['privateIp'] = r['vmguestip']
            ls.append(dict)
    return ls


def hello(reqst):

    # data = listVM(apikey)
    # data = listPort(apikey)

    sql = 'select * from test_vm'
    conn = MySQLdb.connect(**config)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()

    data = []
    for row in rows:
        dic = {}
        dic['IP'] = row[0]
        dic['name'] = row[1]
        dic['state'] = row[2]
        dic['zone'] = row[3]
        dic['publicIP'] = row[4]
        dic['port'] = row[5]
        dic['key'] = row[6]
        data.append(dic)


    # os.system('start C:\\Users\\imkyw\\Desktop\\KT\\a.bat')

    if reqst.method == 'POST':
        createBat(reqst)
        direc = 'C:/Users/imkyw/Desktop/KT/'

    return render(reqst, 'main/hello.html', {'data': data})

def createBat(reqst):

    sql = 'select publicIP, port from test_vm where IP = "' + reqst.POST['ip'] + '" and port = ' + reqst.POST['port'] + ''
    conn = MySQLdb.connect(**config)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchone()
    IP = data[0]
    port = data[1]
    # print(IP)
    # print(port)


    direc = 'C:/Users/imkyw/Desktop/KT/'
    s = [
        '@echo off',
        'ssh root@{} -p {} -i C:/Users/imkyw/Downloads/intern_key_file/intern.pem'.format(IP, port)
    ]
    f = open(direc + 'ttt.bat', 'w')
    for a in s:
        f.write(a)
        f.write('\n')
    f.close()
    os.system('start {}ttt.bat'.format(direc))
    time.sleep(1)
    # os.remove('{}ttt.bat'.format(direc))

    return




