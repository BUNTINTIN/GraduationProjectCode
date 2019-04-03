#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
File: knn.py
Author: liuzihang(liuzihang@baidu.com)
Time: 2019-03-31 14:28:43
Descript: 实现KNN算法
"""
import sys
import traceback
import json

class KnnClass():

    #记录特征（切词）
    list_term_feature = []
    #kd-树：每个节点有如下key：vector、value、left、right
    kd_tree = {}

    """
    构造函数
    """
    def __init__(self):
        pass

    """
    构造kd树
    @param:分类-文件-vsm（字典）
    @return:
    """
    def gen_kd_tree(self, obj_category_file_vsm):
        map_value_vector = {}
        list_value = []
        for category in obj_category_file_vsm:
            for file_num in obj_category_file_vsm[category]:
                for term in obj_category_file_vsm[category][file_num]:
                    map_value_vector = {}
                    list_value = []
                    if term not in self.list_term_feature:
                        self.list_term_feature.append(term) 
                        value_key = obj_category_file_vsm[category][file_num][term]
                        #判断是否删除？                    
                        if value_key not in map_value_vector:
                            map_value_vector[value_key] = []
                        map_value_vector[value_key].append(obj_category_file_vsm[category][file_num])
                        list_value.append(value_key)
                        #再次遍历，获取中位数
                        for category_again in obj_category_file_vsm:
                            for file_num_again in obj_category_file_vsm[category_again]:
                                if category_again != category or file_num_again != file_num:
                                    if term in obj_category_file_vsm[category_again][file_num_again]:
                                        value_key = obj_category_file_vsm[category_again][file_num_again][term]
                                    else:
                                        value_key = 0
                                    if value_key not in map_value_vector:
                                        map_value_vector[value_key] = []
                                    map_value_vector[value_key].append(obj_category_file_vsm[category_again][file_num_again])
                                    list_value.append(value_key)
                        list_value.sort()
                        median_term_value = list_value[int(len(list_value)/2)]
#                        print (median_term_value)
                        self.kd_tree['vector'] = map_value_vector[median_term_value][0]
#                        print (json.dumps(map_value_vector))
#print (json.dumps(self.kd_tree['vector']))
                        print (self.print_map_value(map_value_vector))
                        del map_value_vector[median_term_value][0]
#print (json.dumps(map_value_vector))
                        self.kd_tree['value'] = median_term_value
                        
                        self.kd_tree['left'] = self.gen_kd_node(median_term_value, map_value_vector, True) 
                        self.kd_tree['right'] = self.gen_kd_node(median_term_value, map_value_vector, False)
#print (json.dumps(list_value))
                        print (json.dumps(self.kd_tree))
                        print (json.dumps(self.list_term_feature))
#print (json.dumps(self.kd_tree))
#这里break需要考虑下?
                    break
                break
            break
    """
    递归函数，生成kd树左右节点
    """
    def gen_kd_node(self, median_term_value, map_value_vector_last, is_left = True):
        return_vsm = {}
        return_flag = False
        kd_tree = {}
        # if len(map_value_vector_last) == 1:
        #     return_flag = True
        #     for term_value in map_value_vector_last:
        #         return_vsm = map_value_vector_last[term_value][0]
        #         if len(map_value_vector_last[term_value]) > 1:
        #             break_flag = Fasle
        # if return_flag:
        #     kd_tree['vector'] = return_vsm
        #     return kd_tree
        for term_value in map_value_vector_last:
            if (term_value < median_term_value and is_left) or (term_value >= median_term_value and (not is_left)):
                for key_vsm, vsm in enumerate(map_value_vector_last[term_value]):
                    for term in vsm:
                        #特征值对应的特征向量本身
                        map_value_vector = {}
                        #特征值列表，用于排序   
                        list_value = []
                        if term not in self.list_term_feature:
                            self.list_term_feature.append(term)
                            value_key = vsm[term]
                            if value_key not in map_value_vector:
                                map_value_vector[value_key] = []
                            map_value_vector[value_key].append(vsm)
                            list_value.append(value_key)

                            #再次遍历，获取中位数
                            for term_value_again in map_value_vector_last:

                                if (term_value_again < median_term_value and is_left) or (term_value_again >= median_term_value and (not is_left)):
                                    for key_vsm_again, vsm_again in enumerate(map_value_vector_last[term_value_again]):
                                        try:
                                            if term_value != term_value_again or key_vsm != key_vsm_again:
                                                if term in vsm_again:
                                                    value_key = vsm_again[term]
                                                else:
                                                    value_key = 0
                                                if value_key not in map_value_vector:
                                                    map_value_vector[value_key] = []
                                                map_value_vector[value_key].append(vsm_again)
                                                list_value.append(value_key)
                                        except Exception:
                                            sys.stderr.write(traceback.format_exc())
                            list_value.sort()
                            median_term_value = list_value[int(len(list_value)/2)]
                            kd_tree['value'] = median_term_value
                            kd_tree['vector'] = map_value_vector[median_term_value][0]
                            print (self.print_map_value(map_value_vector))
                            del map_value_vector[median_term_value][0]
                            #有几种情况：
                            #中位数对应一个且没有其他value值对应vector
                            #中位数对应一个有一侧value对应vector或者两侧 ->一侧无法满足直接return null
                            #中位数对应多个
                            if len(map_value_vector[median_term_value]) == 0:
                                if len(map_value_vector) == 1:
                                    return kd_tree
                                else:
                                    del map_value_vector[median_term_value]
                            kd_tree['left'] = self.gen_kd_node(median_term_value, map_value_vector, True)
                            kd_tree['right'] = self.gen_kd_node(median_term_value, map_value_vector, False)
                            return kd_tree
        return 'null'

    """
    输出map中value中少量信息
    """
    def print_map_value(self, map_value_vector):
        line = '{\n'
        for key in map_value_vector:
            line  = line + '\t' + str(key) + ':[\n'
            
            for vector in map_value_vector[key]:
                line = line + '\t\t\t{\n'
                count = 1
                for term in vector:
                    line = line + '\t\t\t\t' + str(term) + ':' + str(vector[term]) + '\n'
                    count += 1
                    if count > 5:
                        break
                line = line + '\t\t\t}\n'
            line = line + '\t\n'
        line = line + '}'
        print (line)

    def test(self):
        print ('test success')
    


    
