#!/usr/bin/python
# -*- coding:UTF-8 -*-
#自定义函数

import sys
import pycurl
import cStringIO
import json
import re
import os
import time
import def_bobo

def path(name):
    fhand = open('configuration.txt')
    ffile = fhand.read()
    path = re.findall(name+".*'(.*?)'", ffile)
    path = str(path).strip('[]')
    fhand.close()
    return path

def get_request_json_response(url):
	#发送get请求，并且得到返回一个dict
    buf = cStringIO.StringIO() 
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.setopt(c.HTTPHEADER, ['Accept: application/json'])
    c.perform()
    response = buf.getvalue()
    response = json.loads(response)
    return response

def ip(configuration):
	#获取configuration中的ip地址
    fhand = open(configuration)
    ffile = fhand.read()
    ip = re.findall('IP:(.*?);', ffile)
    ip = str(ip)
    fhand.close()
    return ip

def api(testcase,configuration):
	#获取configuration中测试用例所对应的接口
    fhand = open(configuration)
    ffile = fhand.read()
    api = re.findall(testcase+'.*api=(.*);', ffile)
    api = str(api)
    fhand.close()
    return api

def parameter(testcase,configuration):
	#获取configuration中测试用例api对应的参数和值，以tuple的形式输出,在执行脚本中，需要用(key, value) = def_bobo.parameter(api),输出一个key的list和value的list.
    fhand = open(configuration)
    ffile = fhand.read()
    #api = api.lstrip("['").rstrip("]'")
    p = re.findall(testcase+'.*-parameter(&.*);', ffile)
    #print "P:", p
    #p = re.findall(api+'.*?(&.*);', ffile)
    key = re.findall('&(.*?)=', str(p))
    value = re.findall('=(.*?)&', str(p))
    fhand.close()
    return key, value

def parameter_with_value(key,value):
	#获取api后面的一串东西
    keyvalue = zip(key,value)#输出类似于这样的list[('mail', 'EB2806EE35374C31165A86A735BD14FBF743D9EB38B8010F'), ('pass', '5C0193A391CA91E5F2BEF0820D248F52'), ('entype', '1')]
    dic = dict()
    for x, y in keyvalue:
        dic[x] = y #输出一个dictionary
    y = ''
    for i in dic:
        y = y + i + '='+dic.get(i)+'&'
    y = y.rstrip('&')
    return y

def api_with_parameter(ip,api,keyvalue):
	#用IP，API，parameter组装成URL
    url = ip.lstrip("['").rstrip("]'")+api.lstrip("['").rstrip("]'")+keyvalue
    return url

def url(testcase, configuration):
	#直接组装成URL
    ip = def_bobo.ip(configuration)
    api = def_bobo.api(testcase,configuration)
    (key, value) = def_bobo.parameter(testcase,configuration)
    parameter = def_bobo.parameter_with_value(key, value)
    url = def_bobo.api_with_parameter(ip, api, parameter)
    return url

def result(actual_result_filename, testcase, url):
	#把结果按照json格式写入结果文件
    response = def_bobo.get_request_json_response(url)
    lst = list()
    dic = dict()
    u = u's'
    count = 0
    for key in response:
        value = response.get(key,'null')
        key = key.encode('utf-8')
        if type(value) == type(0):
            value = str(value)
        elif type(value) == type(dic):
            value = str(value)
        elif type(value) == type(lst):
            value = str(value)
        elif type(value) == type(u):
            value = value.encode('utf-8')
        if count == 0:
            fhand = open(actual_result_filename,'w')
            fhand.write(testcase+'-'+key+':'+value+'\n')
            count = count + 1
        else:
            fhand = open(actual_result_filename,'a')
            fhand.write(testcase+'-'+key+':'+value+'\n')
    fhand.close()
    print "write successed", actual_result_filename

def list_result(actual_result_filename,testcase,url):
	#把list结果按照json格式写入结果文件
    response = def_bobo.get_request_json_response(url)
    lst = list()
    dic = dict()
    u = u's'
    for key in response:
        r = response[key]
        key = key.encode('utf-8')
        if str(key) == 'sui':
            for k in r:
                v = r.get(k,'null')
                k = k.encode('utf-8')
                v = str(v)
                fhand = open(actual_result_filename,'a')
                s = testcase+'-'+'[sui]-'+k+':'+v+'\n'
                fhand.write(s)
                fhand.close()
            print "write [sui] successed", actual_result_filename
        if str(key) == 'list':
            n = len(r)
            for i in range(n):
                r1 = r[i]
                for k in r1:
                    v = r1.get(k,'null')
                    k = k.encode('utf-8')
                    if type(v) == type(0):
                        v = str(v)
                    elif type(v) == type(dic):
                        v = str(v)
                    elif type(v) == type(lst):
                        v = str(v)
                    elif type(v) == type(u):
                        v = v.encode('utf-8')
                    fhand = open(actual_result_filename,'a')
                    s = testcase+'-'+'[list]['+str(i)+']-'+k+':'+v+'\n'
                    fhand.write(s)
                    fhand.close()
            print "write [list] successed", actual_result_filename

def test():
	#执行configuration中的所有测试用例，configuration中只需要有test_case名字，url,就可以
    configuration = def_bobo.path('configuration').strip("'")
    fhand = open(configuration)
    ffile = fhand.read()
    testcase = re.findall("Test_Case.*= (.*);", ffile)#等号后面有空格
    for ts in testcase:
        ts = ts.strip("'")
        print "ts:", ts
        url = def_bobo.url(ts, configuration)
        print "url:",url
        Test_Result_Path = def_bobo.path("Test_Result_Path").strip("'")
        actual_result_filename = Test_Result_Path+'/'+ts+'.txt'
        response= def_bobo.get_request_json_response(url)
        def_bobo.result(actual_result_filename, ts, url)    
        def_bobo.list_result(actual_result_filename, ts, url)
    fhand.close()
    return

def expected_and_actual_result_file():
    #自动获取expected_result和actual_result两个文件夹中的文件路径，以参数的形式传递给函数def result_list(f1, f2)
    f1 = list()
    f2 = list()
    test_result_file_path = def_bobo.path("Test_Result").strip("'")
    expected_result_file_path = def_bobo.path("Expected_Result").strip("'")
    for filename in os.listdir(test_result_file_path):
        if re.search('.txt$', filename) is not None:
            f1_expected_result = expected_result_file_path+'/'+filename
            f2_test_result = test_result_file_path+'/'+filename
            f1.append(f1_expected_result)
            f2.append(f2_test_result)
            #print f1_expected_result,f2_test_result
    return f1, f2

def result_list(f1, f2):
    #把期望结果和实际结果提取到两个list，便于下一步进行比较
    fhand1 = open(f1)
    fhand2 = open(f2)
    lst1 = list()
    lst2 = list()
    for line1 in fhand1:
        msg = re.search(".*Time.*", line1)
        msg1 = re.search(".*time.*", line1)
        msg2 = re.search(".*Token.*", line1)
        msg3 = re.search(".*url.*", line1)
        if msg or msg1 or msg2 or msg3 is not None:
            m = msg or msg1 or msg2 or msg3
        else:
            lst1.append(line1)

    for line2 in fhand2:
        msg = re.search(".*Time.*", line2)
        msg1 = re.search(".*time.*", line2)
        msg2 = re.search(".*Token.*", line2)
        msg3 = re.search(".*url.*", line2)
        if msg or msg1 or msg2 or msg3 is not None:
            m = msg or msg1 or msg2 or msg3
        else:
            lst2.append(line2)
    return lst1, lst2

def test_report(f1, lst1, lst2):
# 输出每个测试用例的测试结果
    r = def_bobo.path('Test_Report')
    r = r.strip("''") + '/'+'Test_report.txt'
    tm = def_bobo.GetNowTime()
    n1 = len(lst1)
    n2 = len(lst2)
    if n1 == n2:
        n = n1
        for i in range(n):
            if lst1[i] != lst2[i]:
                print lst1[i], lst2[i]
                s = re.search('result/(.*).txt', f1)
                s = s.group(1)
                s = str(s).strip("'[]'")
                print s+" failed."+"Because the list1 and list2 are different."
                fhand= open(r,'a')
                fhand.write(s+'-failed. Because the list1 and list2 are different.'+'-*'+tm+'*-'"\n")
                fhand.close()
             elif lst1[i] == lst2[i]:
                s = re.search('result/(.*).txt', f1)
                s = s.group(1)
                s = str(s).strip("'[]'")
                fhand= open(r,'a')
                fhand.write(s+'-passed'+'-*'+tm+'*-'+"\n")
                fhand.close()
        print s+"-passed."
    elif n1 != n2:
        s = re.search('result/(.*).txt', f1)
        s = s.group(1)
        s = str(s).strip("'[]'")
        error = str(lst2)
        print error, type(error)
        print s+' failed.'+"the len(list) is different."
        fhand= open(r,'a')
        fhand.write(s+' failed. because the len(list) is different'+'-*'+tm+'*-'+"\n"+error+"\n")
        fhand.close()
    return

def test_and_report():
    #执行测试用例，比对测试结果和预期结果，输入测试结果报表
    r = def_bobo.path('Test_Report')
    r = r.strip("''") + '/'+'Test_report.txt'
    fhand = open(r,'w')
    fhand = fhand.close()
    def_bobo.test()
    (f1, f2) = def_bobo.expected_and_actual_result_file()
    n1 = len(f1)
    n2 = len(f2)
    if n1 == n2:
        n = n1
        print "The total of test_report_file is "+str(n)+". The number of test_result_file is the same as expected_result_file."
        for i in range(n):
            (lst1, lst2) = def_bobo.result_list(f1[i], f2[i])
            def_bobo.test_report(f1[i], lst1, lst2)
    else:
        print "The number of test_result_file is not the same as expected_result_file."
    return

def GetNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    
def test_one_case(ts):
    #传入测试测试用例名称，执行单挑测试用例
    configuration = def_bobo.path('configuration').strip("'")
    fhand = open(configuration)
    ffile = fhand.read()
    #ts = raw_input("Enter the name of test case: ")
    print "ts:", ts
    url = def_bobo.url(ts, configuration)
    print "url:", url
    Test_Result_Path = def_bobo.path("Test_Result_Path").strip("'")
    actual_result_filename = Test_Result_Path+'/'+ts+'.txt'
    response= def_bobo.get_request_json_response(url)
    def_bobo.result(actual_result_filename, ts, url)    
    def_bobo.list_result(actual_result_filename, ts, url)
    fhand.close()
    test_result_file_path = def_bobo.path("Test_Result").strip("'")
    expected_result_file_path = def_bobo.path("Expected_Result").strip("'")
    f1 = expected_result_file_path+'/'+ts+'.txt'
    #print f1
    f2 = test_result_file_path+'/'+ts+'.txt'
    #print f2
    (lst1, lst2) = def_bobo.result_list(f1, f2)
    def_bobo.test_report(f1, lst1, lst2)
    return
    
