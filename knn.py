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

class KnnNode():

    """
    构造函数
    """
    def __init__(self):
        self.value = None
        self.vector = None
        self.feature_item = None
        self.left = None
        self.right = None
        self.father = None
    """
    一系列基础方法
    """
    def change_value(self, value):
        self.value = value
    def change_vector(self, vector):
        self.vector = vector
    def change_feature_item(self, feature_item):
        self.feature_item = feature_item
    def change_left(self, left):
        self.left = left
    def change_right(self, right):
        self.right = right
    def change_father(self, father):
        self.father = father


class KnnClass():

    #记录特征（切词）
    list_term_feature = []
    #kd-树：每个节点有如下key：vector、value、left、right
    kd_tree_dic = {}
    #初始化根节点
    kd_root = KnnNode()

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
        feature_item = ''
        for category in obj_category_file_vsm:
            for file_num in obj_category_file_vsm[category]:
                for term in obj_category_file_vsm[category][file_num]:
                    map_value_vector = {}
                    list_value = []
                    if term not in self.list_term_feature:
                        feature_item = term
                        self.list_term_feature.append(term) 
                        value_key = obj_category_file_vsm[category][file_num][term]
                        #判断是否删除？                    
                        #if value_key not in map_value_vector:
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
#                        生成两种形式：一种dict；一种实例对象指向
                        self.kd_tree_dic['value'] = median_term_value
                        self.kd_tree_dic['vector'] = map_value_vector[median_term_value][0]
                        self.kd_tree_dic['feature_item'] = feature_item
                        self.kd_root.change_value(median_term_value)
                        self.kd_root.change_vector(map_value_vector[median_term_value][0])
                        self.kd_root.change_feature_item(feature_item)
#                        print (json.dumps(map_value_vector))
                        print (self.print_map_value(map_value_vector))
                        del map_value_vector[median_term_value][0]
#print (json.dumps(map_value_vector))
                        
                        # self.kd_tree_dic['left'] = self.gen_kd_node_dic(median_term_value, map_value_vector, True, feature_item) 
                        # self.kd_tree_dic['right'] = self.gen_kd_node_dic(median_term_value, map_value_vector, False, feature_item)
                        self.kd_root.change_left(self.gen_kd_node(median_term_value, map_value_vector, True, feature_item, self.kd_root))
                        self.kd_root.change_right(self.gen_kd_node(median_term_value, map_value_vector, False, feature_item, self.kd_root))
#print (json.dumps(list_value))
                        print (json.dumps(self.kd_tree_dic))
                        print (json.dumps(self.list_term_feature))
                        print (json.dumps(self.knn_traverse()))


#print (json.dumps(self.kd_tree_dic))
#这里break需要考虑下?
                    break
                break
            break
        list_vector = self.gen_feature_vector(obj_category_file_vsm)
        for vector in list_vector:
            self.get_k_node(vector)

    """
    递归函数，生成kd树左右节点（dict形式）
    """
    def gen_kd_node_dic(self, median_term_value_last, map_value_vector_last, is_left, feature_item_last):
        
        kd_tree_dic = {}
        feature_item = ''
        term_value_log = 0
        key_vsm_log = 0
        loop_feature_flag = True
        has_son_node = False
        #特征值对应的特征向量本身
        map_value_vector = {}
        #特征值列表，用于排序   
        list_value = []
        

        #有几种情况：
        #1.没有符合的一侧子节点候选
        #2.有符合的一侧子节点候选，但是特征全部用完
        #3.有。。。并且取到特征
        for term_value in map_value_vector_last:
            if (term_value <= median_term_value_last and is_left) or (term_value > median_term_value_last and (not is_left)):
                has_son_node = True
                for key_vsm, vsm in enumerate(map_value_vector_last[term_value]):
                    for term in vsm:
                        if term not in self.list_term_feature:
                            loop_feature_flag = False
                            feature_item = term
                            self.list_term_feature.append(term)
                            value_key = vsm[term]
                            #if value_key not in map_value_vector:
                            map_value_vector[value_key] = []
                            map_value_vector[value_key].append(vsm)
                            list_value.append(value_key)
                            term_value_log = term_value
                            key_vsm_log = key_vsm
                            break
                    break
                break
        if has_son_node:
            if loop_feature_flag:
                try:
                    pos_feature_item_last = self.list_term_feature.index(feature_item_last)
                    if  pos_feature_item_last < (len(self.list_term_feature) - 1):
                        feature_item = self.list_term_feature[pos_feature_item_last + 1]
                    else:
                        feature_item = self.list_term_feature[0]
                except Exception:
                    sys.stderr.write('出错源：特征列表中无法匹配到上次用到的特征。特征列表：' + json.dumps(self.list_term_feature))
                    sys.stderr.write(traceback.format_exc())
                for term_value in map_value_vector_last:
                    if (term_value <= median_term_value_last and is_left) or (term_value > median_term_value_last and (not is_left)):
                        vsm = map_value_vector_last[term_value][0]
                        if feature_item in vsm:
                            value_key = vsm[feature_item]
                        else:
                            value_key = 0
                        map_value_vector[value_key] = []
                        map_value_vector[value_key].append(vsm)
                        list_value.append(value_key)
                        term_value_log = term_value
                        key_vsm_log = 0
                        break

            #再次遍历，获取中位数
            for term_value_again in map_value_vector_last:
                if (term_value_again <= median_term_value_last and is_left) or (term_value_again > median_term_value_last and (not is_left)):
                    for key_vsm_again, vsm_again in enumerate(map_value_vector_last[term_value_again]):
                        try:
                            if term_value_log != term_value_again or key_vsm_log != key_vsm_again:
                                if feature_item in vsm_again:
                                    value_key = vsm_again[feature_item]
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
            kd_tree_dic['value'] = median_term_value
            kd_tree_dic['vector'] = map_value_vector[median_term_value][0]
            kd_tree_dic['feature_item'] = feature_item
            print (self.print_map_value(map_value_vector))
            del map_value_vector[median_term_value][0]
            #有几种情况：
            #中位数对应一个且没有其他value值对应vector
            #中位数对应一个有一侧value对应vector或者两侧 ->一侧无法满足直接return None
            #中位数对应多个
            if len(map_value_vector[median_term_value]) == 0:
                if len(map_value_vector) == 1:
                    kd_tree_dic['left'] = None
                    kd_tree_dic['right'] = None
                    return kd_tree_dic
                else:
                    del map_value_vector[median_term_value]
            kd_tree_dic['left'] = self.gen_kd_node_dic(median_term_value, map_value_vector, True, feature_item)
            kd_tree_dic['right'] = self.gen_kd_node_dic(median_term_value, map_value_vector, False, feature_item)
            #return 保证最外层for循环只进行一次
            return kd_tree_dic
        return None

    """
    递归函数，生成kd树左右节点（实例形式）
    """
    def gen_kd_node(self, median_term_value_last, map_value_vector_last, is_left, feature_item_last, father_node):
        kd_node = KnnNode()
        kd_tree_dic = {}
        feature_item = ''
        term_value_log = 0
        key_vsm_log = 0
        loop_feature_flag = True
        has_son_node = False
        #特征值对应的特征向量本身
        map_value_vector = {}
        #特征值列表，用于排序   
        list_value = []
        

        #有几种情况：
        #1.没有符合的一侧子节点候选
        #2.有符合的一侧子节点候选，但是特征全部用完
        #3.有。。。并且取到特征
        for term_value in map_value_vector_last:
            if (term_value <= median_term_value_last and is_left) or (term_value > median_term_value_last and (not is_left)):
                has_son_node = True
                for key_vsm, vsm in enumerate(map_value_vector_last[term_value]):
                    for term in vsm:
                        if term not in self.list_term_feature:
                            loop_feature_flag = False
                            feature_item = term
                            self.list_term_feature.append(term)
                            value_key = vsm[term]
                            #if value_key not in map_value_vector:
                            map_value_vector[value_key] = []
                            map_value_vector[value_key].append(vsm)
                            list_value.append(value_key)
                            term_value_log = term_value
                            key_vsm_log = key_vsm
                            break
                    break
                break
        if has_son_node:
            if loop_feature_flag:
                try:
                    pos_feature_item_last = self.list_term_feature.index(feature_item_last)
                    if  pos_feature_item_last < (len(self.list_term_feature) - 1):
                        feature_item = self.list_term_feature[pos_feature_item_last + 1]
                    else:
                        feature_item = self.list_term_feature[0]
                except Exception:
                    sys.stderr.write('出错源：特征列表中无法匹配到上次用到的特征。特征列表：' + json.dumps(self.list_term_feature))
                    sys.stderr.write(traceback.format_exc())
                for term_value in map_value_vector_last:
                    if (term_value <= median_term_value_last and is_left) or (term_value > median_term_value_last and (not is_left)):
                        vsm = map_value_vector_last[term_value][0]
                        if feature_item in vsm:
                            value_key = vsm[feature_item]
                        else:
                            value_key = 0
                        map_value_vector[value_key] = []
                        map_value_vector[value_key].append(vsm)
                        list_value.append(value_key)
                        term_value_log = term_value
                        key_vsm_log = 0
                        break

            #再次遍历，获取中位数
            for term_value_again in map_value_vector_last:
                if (term_value_again <= median_term_value_last and is_left) or (term_value_again > median_term_value_last and (not is_left)):
                    for key_vsm_again, vsm_again in enumerate(map_value_vector_last[term_value_again]):
                        try:
                            if term_value_log != term_value_again or key_vsm_log != key_vsm_again:
                                if feature_item in vsm_again:
                                    value_key = vsm_again[feature_item]
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
            
            kd_node.change_value(median_term_value)
            kd_node.change_vector(map_value_vector[median_term_value][0])
            kd_node.change_feature_item(father_node)
            kd_node.change_father(father_node)
            del map_value_vector[median_term_value][0]
            #有几种情况：
            #中位数对应一个且没有其他value值对应vector
            #中位数对应一个有一侧value对应vector或者两侧 ->一侧无法满足直接return None
            #中位数对应多个
            if len(map_value_vector[median_term_value]) == 0:
                if len(map_value_vector) == 1:
                    kd_node.change_left(None)
                    kd_node.change_right(None)
                    return kd_node
                else:
                    del map_value_vector[median_term_value]
            kd_node.change_left(self.gen_kd_node(median_term_value, map_value_vector, True, feature_item, kd_node))
            kd_node.change_right(self.gen_kd_node(median_term_value, map_value_vector, False, feature_item, kd_node))
            #return 保证最外层for循环只进行一次
            return kd_node
        return None


    """
    kd树最近邻搜索
    """
    def get_k_node(self, feature_vector, k=1):
        current_node = self.kd_root
        father_node = current_node
        num = 0
        len_list_feature = len(self.list_term_feature)
        while current_node != None:
            father_node = current_node
            if not (num < len_list_feature):
                num == 0
            feature_item = self.list_term_feature[num]
            if feature_item in feature_vector:
                print('命中')
                feature_value = feature_vector[feature_item]
            else:
                feature_value = 0
            print('feature:' + str(feature_value) + '\t' + 'current:' + str(current_node.value))
            if feature_value <= current_node.value:
                current_node = current_node.left
            else:
                current_node = current_node.right
            num += 1

        if father_node.father.left != None:
            nearest_node = father_node.father.left
        elif father_node.father.right != None:
            nearest_node = father_node.father.right
        else:
            nearest_node = father_node

        list_print = [feature_vector, nearest_node.vector]
        print(json.dumps(list_print)) 


    """
    辅助函数：输出map_value_vector中vector中少量信息
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
    """
    辅助函数：二叉树层级遍历
    """
    def knn_traverse(self):  # 层次遍历
        if self.kd_root == None:
            return None
        q = [self.kd_root]
        res = [self.kd_root.value, '(father:' + 'None' + ')']
        while q != []:
            pop_node = q.pop(0)
            if pop_node.left is not None:
                q.append(pop_node.left)
                res.append(pop_node.left.value)
                res.append('(father:' + str(pop_node.left.father.value) + ')')

            if pop_node.right is not None:
                q.append(pop_node.right)
                res.append(pop_node.right.value)
                res.append('(father:' + str(pop_node.right.father.value) + ')')
        return res

    """
    辅助函数：生成feature_vector
    """
    def gen_feature_vector(self, obj_category_file_vsm):
        list_vector = []
        for category in obj_category_file_vsm:
            for file_num in obj_category_file_vsm[category]:
                list_vector.append(obj_category_file_vsm[category][file_num])
        return list_vector

    def test(self):
        print ('test success')
    


    
