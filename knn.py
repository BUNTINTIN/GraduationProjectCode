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

"""
kd树节点类
"""
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
        self.category = None
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
    def change_category(self, category):
        self.category = category


class KnnClass():

    #记录特征（切词）
    list_feature = []
    #kd-树：每个节点有如下key：vector、value、left、right
    kd_tree_dic = {}
    #初始化根节点
    kd_root = None

    """
    构造函数
    """
    def __init__(self):
        self.kd_root = KnnNode()
        reload(sys)
        sys.setdefaultencoding('utf8')

    """
    构造kd树
    @param:分类-文件-vsm（字典）
    @param:特征列表
    @return:
    """
    def gen_kd_tree(self, obj_category_file_vsm, list_feature, file_kd, file_list_feature):
        map_value_vector = {}
        list_value = []
        feature_item = ''

        self.list_feature = list_feature
        feature_pos = 0
        feature_item = self.list_feature[feature_pos]
        for category in obj_category_file_vsm:
            for file_num in obj_category_file_vsm[category]:
                if feature_item in obj_category_file_vsm[category][file_num]:
                    feature_value = obj_category_file_vsm[category][file_num][feature_item]
                else:
                    feature_value = 0
                if feature_value not in map_value_vector:
                    map_value_vector[feature_value] = []
                list_category_vsm = [category, obj_category_file_vsm[category][file_num]]
                map_value_vector[feature_value].append(list_category_vsm)
                list_value.append(feature_value)
        list_value.sort()
        median_term_value = list_value[int(len(list_value)/2)]
#        生成两种形式：一种dict；一种实例对象指向
        self.kd_tree_dic['value'] = median_term_value
        self.kd_tree_dic['category'] = map_value_vector[median_term_value][0][0]
        self.kd_tree_dic['vector'] = map_value_vector[median_term_value][0][1]
        self.kd_tree_dic['feature_item'] = feature_item
        self.kd_root.change_value(median_term_value)
        self.kd_root.change_category(map_value_vector[median_term_value][0][0])
        self.kd_root.change_vector(map_value_vector[median_term_value][0][1])
        self.kd_root.change_feature_item(feature_item)

        print (self.print_map_value(map_value_vector))
        del map_value_vector[median_term_value][0]
        # 生成两种形式：一种dict；一种实例对象指向
        self.kd_tree_dic['left'] = self.gen_kd_node_dic(median_term_value, map_value_vector, True, feature_item, feature_pos) 
        self.kd_tree_dic['right'] = self.gen_kd_node_dic(median_term_value, map_value_vector, False, feature_item, feature_pos)
        # self.kd_root.change_left(self.gen_kd_node(median_term_value, map_value_vector, True, feature_item, self.kd_root, feature_pos))
        # self.kd_root.change_right(self.gen_kd_node(median_term_value, map_value_vector, False, feature_item, self.kd_root, feature_pos))
        print (json.dumps(self.kd_tree_dic))
        print (json.dumps(self.knn_traverse()))
        fp_kd_tree_result = open(file_kd, 'w')
        fp_kd_tree_result.write(json.dumps(self.kd_tree_dic))
        fp_kd_tree_result.close()
        fp_list_feature = open(file_list_feature, 'w')
        fp_list_feature.write(json.dumps(self.list_feature))
        fp_list_feature.close()


    """
    递归函数，生成kd树左右节点（dict形式）
    """
    def gen_kd_node_dic(self, median_term_value_last, map_value_vector_last, is_left, feature_item_last, feature_pos_last):
        
        kd_tree_dic = {}
        feature_item = ''
        has_son_node = False
        #特征值对应的特征向量本身
        map_value_vector = {}
        #特征值列表，用于排序   
        list_value = []
        

        """
        4.5重构
        """
        feature_pos = feature_pos_last + 1
        if feature_pos >= len(self.list_feature):
            feature_pos = 0
        feature_item = self.list_feature[feature_pos]

        for term_value in map_value_vector_last:
            if (term_value <= median_term_value_last and is_left) or (term_value > median_term_value_last and (not is_left)):
                has_son_node = True
                for list_category_vsm in map_value_vector_last[term_value]:
                    category = list_category_vsm[0]
                    vsm = list_category_vsm[1]
                    if feature_item in vsm:
                        feature_value = vsm[feature_item]
                    else:
                        feature_value = 0
                    if feature_value not in map_value_vector:
                        map_value_vector[feature_value] = []
                    map_value_vector[feature_value].append(list_category_vsm)
                list_value.append(feature_value)
        if has_son_node:
            list_value.sort()
            median_term_value = list_value[int(len(list_value)/2)]
            
            kd_tree_dic['value'] = median_term_value
            kd_tree_dic['category'] = map_value_vector[median_term_value][0][0]
            kd_tree_dic['vector'] = map_value_vector[median_term_value][0][1]
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
            kd_tree_dic['left'] = self.gen_kd_node_dic(median_term_value, map_value_vector, True, feature_item, feature_pos)
            kd_tree_dic['right'] = self.gen_kd_node_dic(median_term_value, map_value_vector, False, feature_item, feature_pos)
            return kd_tree_dic
        return None


    """
    递归函数，生成kd树左右节点（实例形式）
    """
    def gen_kd_node(self, median_term_value_last, map_value_vector_last, is_left, feature_item_last, father_node, feature_pos_last):
        kd_node = KnnNode()
        feature_item = ''
        has_son_node = False
        #特征值对应的特征向量本身
        map_value_vector = {}
        #特征值列表，用于排序   
        list_value = []
        
        """
        4.5重构
        """
        feature_pos = feature_pos_last + 1
        if feature_pos >= len(self.list_feature):
            feature_pos = 0
        feature_item = self.list_feature[feature_pos]

        for term_value in map_value_vector_last:
            if (term_value <= median_term_value_last and is_left) or (term_value > median_term_value_last and (not is_left)):
                has_son_node = True
                for list_category_vsm in map_value_vector_last[term_value]:
                    category = list_category_vsm[0]
                    vsm = list_category_vsm[1]
                    if feature_item in vsm:
                        feature_value = vsm[feature_item]
                    else:
                        feature_value = 0
                    if feature_value not in map_value_vector:
                        map_value_vector[feature_value] = []
                    map_value_vector[feature_value].append(list_category_vsm)
                list_value.append(feature_value)
        if has_son_node:
            list_value.sort()
            median_term_value = list_value[int(len(list_value)/2)]
            
            kd_node.change_value(median_term_value)
            kd_node.change_category(map_value_vector[median_term_value][0][0])
            kd_node.change_vector(map_value_vector[median_term_value][0][1])
            kd_node.change_feature_item(feature_item)
            kd_node.change_father(father_node)
            print (self.print_map_value(map_value_vector))
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
            kd_node.change_left(self.gen_kd_node(median_term_value, map_value_vector, True, feature_item, kd_node, feature_pos))
            kd_node.change_right(self.gen_kd_node(median_term_value, map_value_vector, False, feature_item, kd_node, feature_pos))
            return kd_node
        return None

    """
    测试kd树最近邻搜索
    """
    def do_classification(self, obj_category_file_vsm):
        list_vector = self.gen_feature_vector(obj_category_file_vsm)
        for vector in list_vector:
            self.kd_nearest_neighbor_search(vector)


    """
    kd树最近邻搜索
    """
    def kd_nearest_neighbor_search(self, feature_vector, k=1):
        current_node = self.kd_root
        father_node = current_node
        num = 0
        len_list_feature = len(self.list_feature)
        #遍历到叶子节点
        while current_node != None:
            father_node = current_node
            if not (num < len_list_feature):
                num == 0
            feature_item = self.list_feature[num]
            if feature_item in feature_vector:
                print('命中' + feature_item)
                flag = True
                feature_value = feature_vector[feature_item]
            else:
                feature_value = 0
            print('feature:' + str(feature_value) + '\t' + 'current:' + str(current_node.value))
            if feature_value <= current_node.value:
                current_node = current_node.left
            else:
                current_node = current_node.right
            num += 1

        if father_node.left != None:
            nearest_node = self.get_leaf_node(father_node)
        elif father_node.right != None:
            nearest_node = self.get_leaf_node(father_node, False)
        else:
            nearest_node = father_node

        #遍历到根节点找出距离最小的节点或者排序获得k个节点
        dict_distance_vector = {}
        min_distance = None
        current_node = nearest_node
        while True: 
            #操作当前节点
            current_distance = self.get_node_distance(feature_vector, current_node.vector)
            if current_distance not in dict_distance_vector:
                dict_distance_vector[current_distance] = []
            dict_node_info = {
                'category' : current_node.category,
                'vector' : current_node.vector
            }
            dict_distance_vector[current_distance].append(dict_node_info)
            if min_distance == None or current_distance < min_distance:
                min_distance = current_distance
                nearest_node = current_node
            #操作兄弟节点
            if current_node != self.kd_root:
                bro_node = self.get_bro_node(current_node)
                if bro_node != None:
                    bro_distance = self.get_node_distance(feature_vector, bro_node.vector)
                    if bro_distance not in dict_distance_vector:
                        dict_distance_vector[bro_distance] = []
                    dict_node_info = {
                        'category' : bro_node.category,
                        'vector' : bro_node.vector
                    }
                    dict_distance_vector[bro_distance].append(dict_node_info)
                    if bro_distance < min_distance:
                        min_distance = bro_distance
                        nearest_node = bro_node
            else:
                break
            current_node = current_node.father

        print (json.dumps(dict_distance_vector))
        list_dict_node_info = self.get_k_node(dict_distance_vector, k)
        

        list_print = [feature_vector, list_dict_node_info]
        print(json.dumps(list_print)) 
        final_category = self.get_node_category(list_dict_node_info)
        print (final_category)

    """
    分析最终的分类结果
    """
    def get_node_category(self, list_dict_node_info):
        dict_category_sum = {}
        for dict_node_info in list_dict_node_info:
            category = dict_node_info['category']
            if category not in dict_category_sum:
                dict_category_sum[category] = 0
            dict_category_sum[category] += 1
        list_dict_category_sum = sorted(dict_category_sum.items(),key=lambda x:x[1], reverse=True)
        category = list_dict_category_sum[0][0]
        return category

    """
    kd树搜索--找到叶子节点
    """
    def get_leaf_node(self, node, is_left = True):
        print ('用到')
        last_node = node
        while node != None:
            last_node = node
            if is_left:
                node = node.left
            else:
                node = node.right
        return last_node


    """
    获取兄弟节点
    @param：当前节点
    @return：兄弟节点/None
    """
    def get_bro_node(self, current_node):
        try:
            father_node = current_node.father
        except Exception:
            sys.stderr.write('获取父节点失败')
            sys.stderr.write(traceback.format_exc())
        if father_node.left == current_node:
            return father_node.right
        else:
            return father_node.left

    """
    获取距离最近的k个节点
    """
    def get_k_node(self, dict_distance_vector, k):
        list_distance_vector = sorted(dict_distance_vector.items(),key=lambda x:x[0])
        pos = 0
        count = 0
        list_dict_node_info = []
        break_flag = False

        while True:
            list_dict = list_distance_vector[pos][1]
            for dict_node_info in list_dict:
                count += 1
                if count > k:
                    break_flag = True
                    break
                list_dict_node_info.append(dict_node_info)
            pos += 1
            if break_flag:
                break
        return list_dict_node_info

    """
    计算向量距离---欧氏距离
    @param:两个向量
    @param: p：距离度量参数
    """
    def get_node_distance(self, vector1, vector2, p = 2):
        sum = 0
        for feature_item in self.list_feature:
            if feature_item in vector1:
                feature_value1 = vector1[feature_item]
            else:
                feature_value1 = 0
            if feature_item in vector2:
                feature_value2 = vector2[feature_item]
            else:
                feature_value2 = 0
            sum += float(pow(abs(feature_value1-feature_value2), p))
        return pow(sum, 1.0/p)

    """
    根据kd_dict（json文件）生成可利用kd数
    """
    def gen_kd_tree_by_json(self, file_kd, file_list_feature):
        fp_kd_tree_result = open(file_kd, 'r')
        for line in fp_kd_tree_result:
            self.kd_tree_dic = json.loads(line)
        fp_list_feature = open(file_list_feature, 'r')
        for line in fp_list_feature:
            line = line.strip()
            list_feature = json.loads(line)
        for feature in list_feature:
            self.list_feature.append(self.trans_coding(feature, 'utf8'))
        current_node = self.kd_tree_dic
        if current_node['left'] != None or current_node['right'] != None:
            self.kd_root.change_value(current_node['value'])
            self.kd_root.change_category(self.trans_coding(current_node['category'], 'utf8'))
            self.kd_root.change_vector(self.trans_dict_coding(current_node['vector']))
            self.kd_root.change_feature_item(self.trans_coding(current_node['feature_item'], 'utf8'))
            self.kd_root.change_father(None)
            self.kd_root.change_left(self.get_left_right_node(current_node['left'], self.kd_root))
            self.kd_root.change_right(self.get_left_right_node(current_node['right'], self.kd_root))
        self.knn_traverse()

    """
    通过dict递归生成kd树
    """
    def get_left_right_node(self, current_node, father):
        if current_node == None:
            return None
        kd_node = KnnNode()
        kd_node.change_value(current_node['value'])
        kd_node.change_category(self.trans_coding(current_node['category'], 'utf8'))
        kd_node.change_vector(self.trans_dict_coding(current_node['vector']))
        kd_node.change_feature_item(self.trans_coding(current_node['feature_item'], 'utf8'))
        kd_node.change_father(father)
        kd_node.change_left(self.get_left_right_node(current_node['left'], kd_node))
        kd_node.change_right(self.get_left_right_node(current_node['right'], kd_node))
        return kd_node




    """
    辅助函数：输出map_value_vector中vector中少量信息
    """
    def print_map_value(self, map_value_vector):
        line = '{\n'
        for key in map_value_vector:
            line  = line + '\t' + str(key) + ':[\n'
            
            for vector in map_value_vector[key]:
                line = line + '\t\t[\n' 
                line = line + '\t\t\t' + vector[0] + '\n'
                line = line + '\t\t\t{\n'
                count = 1
                for term in vector[1]:
                    line = line + '\t\t\t\t' + str(term) + ':' + str(vector[1][term]) + '\n'
                    count += 1
                    if count > 5:
                        break
                line = line + '\t\t\t}\n'
                line = line + '\t\t]\n'
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
    辅助函数：生成feature_vector，以便测试kd树最近邻搜索
    """
    def gen_feature_vector(self, obj_category_file_vsm):
        list_vector = []
        for category in obj_category_file_vsm:
            for file_num in obj_category_file_vsm[category]:
                list_vector.append(obj_category_file_vsm[category][file_num])
        return list_vector

    """
    辅助函数：转换内容编码，统一转成utf8格式
    """
    def trans_coding(self, line, coding='gbk'):
        try:
            line = line.strip('\n')
            if coding == 'gbk':
                return line.decode('gbk', "ignore").encode('utf8')
            else:
                return line.decode('utf8', "ignore").encode('utf8')
        except Exception:
            if coding == 'gbk':
                sys.stderr.write ('该行不能由gbk转换成utf8：' + line + ';最终的解决方案是返回原编码行')
            else:
                sys.stderr.write ('该行不能由utf8转换成Unicode编码再转换成utf8：' + line + ';最终的解决方案是返回原编码行')
        return line
    """
    辅助函数：将dict中key转换成utf8格式
    """
    def trans_dict_coding(self, dict_demo):
        try:
            for key in dict_demo:
                value = dict_demo[key]
                del dict_demo[key]
                dict_demo[key.decode('utf8', 'ignore').encode('utf8')] = value

        except Exception:
            sys.stderr.write(traceback.format_exc())
        return dict_demo

    def test(self):
        print ('test success')
    


    
