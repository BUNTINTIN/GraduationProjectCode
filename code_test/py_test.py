#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
File: py_test.py
Author: liuzihang(liuzihang@baidu.com)
Time: 2019-04-04 11:18:25
Descript:
"""
import json
import sys
"""
测试函数参数
"""
def test_param(a, b):
    reload(sys)
    sys.setdefaultencoding('utf8')
    # print (a + b)
    # a = 'null'
    # print (a)
    # a = 1
    # print (a)
    # arr = 'a'
    # print (arr)
    # arr = ['a', 'b']
    # print (arr)
    # if 0 == 0.0:
    # 	print('相等')
    """
    测试字典排序
    """
    # dict_data = {
    #     3:['a','b'],
    #     2:['123','456']
    # }
    # test_data_1=sorted(dict_data.items(),key=lambda x:x[0])
    # print (test_data_1)
    # p = 3
    # print (pow(abs(0-4),1.0/p))
    # list_1 = ['"123"']
    # print (list_1)
    """
    测试json
    """
    dict_test = {
        '刘'.decode('utf-8') : 'a'
    }
    list_test = ['刘', '子']
    fp_re = open('./re', 'w')
    fp_re.write(json.dumps(dict_test))
    # json.dump(dict_test, fp_re, ensure_ascii=False, encoding='utf8')
    fp_re.close()
    fp_re_again = open('./re', 'r')
    for line in fp_re_again:
        line = line.strip()
        dict_file = json.loads(line)
    # dict_file = json.load(fp_re_again,encoding='utf8')

    # for key in dict_file:
    #     value = dict_file[key]
    #     del dict_file[key]
    #     dict_file[key.decode('utf8').encode('utf8')] = value
    for key in dict_file:
        print (key + dict_file[key])

    if '刘'.decode('utf8') in dict_file:
        print (dict_file['刘'.decode('utf8')])
    if '刘'.decode('utf8') in dict_test:
        print (dict_test['刘'.decode('utf8')])

if __name__ == '__main__':
	test_param(b='b', a='a')
