# -*- coding: utf-8 -*-
import json
import math
import sys
import traceback
import chardet
import os
#引入外部python文件
import knn

#fp = open('..\datasets\TanCorp-12-Txt\TanCorp-12-Txt\财经\0.txt', 'r')
#['财经','地域','电脑','房产','教育','科技','汽车','人才','体育','卫生','艺术','娱乐']

class TextPretreatment():
    text_category_list = []
    #停用词列表
    list_stop_word = []
    #特征列表
    list_feature = []
    #category对应词频
    obj_category_TF = {}
    #category对应文件下切词总数
    obj_category_file_termcount = {}
    #category对应词卡方
    obj_category_file_CHI = {}
    #category对应词卡方a,b,c,d
    obj_category_file_CHI_param = {}
    #临时：category对应词卡方
    obj_category_file_CHI_temp = {}
    #临时：category对应词卡方a,b,c,d
    obj_category_file_CHI_param_temp= {}
#    category对应词tf-idf
    obj_category_file_TF_IDF = {}
    #最终的vsm
    obj_category_file_vsm = {}
    #用于计算tf-idf的参数
    dict_tfidf_param = {'N':0, 'count_include_feature':{}}
#    输入文档总数
    N = 0
#    每个类别下文件总数，修改
    sum = 1
    def __init__(self, text_category_list):
        self.text_category_list = text_category_list
        reload(sys)
        sys.setdefaultencoding('utf8')
    """
    转换文件编码格式
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
    根据停用词文件生产停用词list
    """
    def get_stop_list(self, file_stop_word):
        fp_stop_word = open(file_stop_word, 'r')
        for line in fp_stop_word:
#需要通用处理行吗？
            line = self.trans_coding(line.strip('\n'), 'utf8')
            if line not in self.list_stop_word:
                self.list_stop_word.append(line)
#        print (json.dumps(self.list_stop_word))
    
    """
    生成category对应词频
    """
    def get_term_frequency(self, file_dir, file_tf_result = None, file_category_file_termcount = None, file_count_limit = None):
        for category in self.text_category_list:
            counter = 1
            self.obj_category_TF[category] = {}
            self.obj_category_file_termcount[category] = {}

            path = file_dir + category
            level = 1
            dir_list = []  
            # 所有文件  
            file_list = []  
            # 返回一个列表，其中包含在目录条目的名称 
            files = os.listdir(path)  
            # 先添加目录级别  
            dir_list.append(str(level))  
            for f in files:  
                if(os.path.isdir(path + '/' + f)):  
                    # 排除隐藏文件夹。因为隐藏文件夹过多  
                    if(f[0] == '.'):  
                        pass  
                    else:  
                        # 添加非隐藏文件夹  
                        dir_list.append(f)  
                if(os.path.isfile(path + '/' + f)):  
                 # 添加文件  
                    file_list.append(f)  
            print (json.dumps(file_list))

            for file in file_list:
            # while counter <= self.sum:
                self.obj_category_TF[category][file] = {}
                self.obj_category_file_termcount[category][file] = 0
                with open(path + '/' + file , 'r') as fp:
                    data = fp.read()
                    file_encoding = 'gbk'
                    try:
                        if chardet.detect(data)['encoding'] != None:

                            if chardet.detect(data)['encoding'].startswith('utf-8') or chardet.detect(data)['encoding'].startswith('UTF-8'):
                                file_encoding = 'utf8'
                            else:
                                file_encoding = 'gbk'
                        else:
                            print (json.dumps(chardet.detect(data)))
                    except Exception:
                        sys.stderr.write('出错源：\n' + json.dumps(chardet.detect(data)) + '\n' + data)
                        sys.stderr.write(traceback.format_exc())
                    
                with open(path + '/' + file, 'r') as fp_again:
                    for line in fp_again:
                        # 文件默认是gbk格式，同一转成utf8格式
                        if file_encoding == 'gbk':
                            line = self.trans_coding(line)
                        else:
                            line = self.trans_coding(line, file_encoding)
                        word_list = line.split()
                        for word in word_list:
                            if word not in self.list_stop_word:
                                # 存入的都是decode('utf8')，也就是转成Unicode编码
                                word = word.decode('utf8')
                                if word in self.obj_category_TF[category][file]:
                                    self.obj_category_TF[category][file][word] += 1
                                else:
                                    self.obj_category_TF[category][file][word] = 1;
                                self.obj_category_file_termcount[category][file] +=  1
                            # else:
                            #     print (word)
                    counter = counter + 1 
                    if file_count_limit != None:
                        if counter > file_count_limit:
                            break
        #       文档总数
        self.N = 0
        for category in self.obj_category_TF:
            self.N = self.N + len(self.obj_category_TF[category])
        print(self.N)
        self.dict_tfidf_param['N'] = self.N   
        # if file_tf_result != None:
        #     with open(file_tf_result, 'w') as fp_result:
        #         json.dump(self.obj_category_TF, fp_result)
        
        if file_category_file_termcount != None:
            with open(file_category_file_termcount, 'w') as fp_category_file_termcount:
                json.dump(self.obj_category_file_termcount, fp_category_file_termcount)


    """
    生成category对应词卡方
    """
    def get_term_CHI(self, file_CHI, file_CHI_param, file_tfidf_param, file_list_feature = None, feature_num_one_doc = 5):
#    特征提取都是以文件为单位
#    卡方检验

        
        for category in self.obj_category_TF:
            self.obj_category_file_CHI_param_temp[category] = {}
            self.obj_category_file_CHI_temp[category] = {}
            for file_num in self.obj_category_TF[category]:
                self.obj_category_file_CHI_param_temp[category][file_num] = {}
                self.obj_category_file_CHI_temp[category][file_num] = {}
                for word in self.obj_category_TF[category][file_num]:
                    a = 0
                    b = 0
                    c = 0
                    d = 0
        #           生成a，b
                    for file_num_again in self.obj_category_TF[category]:
        #                print (obj_category_TF[category][file_num_again])
                        if word in self.obj_category_TF[category][file_num_again]:
                            a = a+1
                        else:
                            c = c+1
                    for category_again in self.obj_category_TF:
                        if category_again != category:
                            for file_num_check in self.obj_category_TF[category_again]:
                                if word in self.obj_category_TF[category_again][file_num_check]:
                                    b = b+1
                                else:
                                    d = d+1
                    deno = ((a+b)*(c+d))
#                    修改：分母为零时如何处理----经过分析和实际测试，不可能有等于零的情况
                    if (deno == 0):
                        self.obj_category_file_CHI_temp[category][file_num][word] = float(math.pow((a*d)-(b*d), 2))
                    else:
                        self.obj_category_file_CHI_temp[category][file_num][word] = float(math.pow((a*d)-(b*d), 2))/float(deno)
                    self.obj_category_file_CHI_param_temp[category][file_num][word] = {}
                    self.obj_category_file_CHI_param_temp[category][file_num][word]['a'] = a
                    self.obj_category_file_CHI_param_temp[category][file_num][word]['b'] = b
                    self.obj_category_file_CHI_param_temp[category][file_num][word]['c'] = c
                    self.obj_category_file_CHI_param_temp[category][file_num][word]['d'] = d
                    
        
        self.simplify_dict(feature_num_one_doc)

        with open(file_CHI, 'w') as fp_CHI_result:
            json.dump(self.obj_category_file_CHI, fp_CHI_result)
        with open(file_CHI_param, 'w') as fp_CHI_param_result:
            json.dump(self.obj_category_file_CHI_param, fp_CHI_param_result)
        with open(file_tfidf_param, 'w') as fp_tfidf_param_result:
            json.dump(self.dict_tfidf_param, fp_tfidf_param_result)
        if file_list_feature != None:
            with open(file_list_feature, 'w') as fp_list_feature_result:
                json.dump(self.list_feature, fp_list_feature_result)

    """
    根据特征选择值结果，筛选必要的特征值
    """
    def simplify_dict(self, feature_num_one_doc):
        for category in self.obj_category_file_CHI_temp:
            self.obj_category_file_CHI_param[category] = {}
            self.obj_category_file_CHI[category] = {}
            for file in self.obj_category_file_CHI_temp[category]:
                self.obj_category_file_CHI_param[category][file] = {}
                self.obj_category_file_CHI[category][file] = {}
                self.obj_category_file_termcount[category][file] = 0
                dict_feature_chi = self.obj_category_file_CHI_temp[category][file]
                feature_chi_list = sorted(dict_feature_chi.items(),key=lambda x:x[1],reverse=True)
                len_list = len(feature_chi_list)
                # feature_list = []
                for i in range(feature_num_one_doc):
                    if i < len_list:
                        try:
                            feature = feature_chi_list[i][0]
                        except Exception:
                            sys.stderr.write('出错源【文档原始特征数目少于10个】:\n' + json.dumps(feature_chi_list))
                            sys.stderr.write(traceback.format_exc())
                            continue
                        self.obj_category_file_CHI_param[category][file][feature] = self.obj_category_file_CHI_param_temp[category][file][feature]
                        self.obj_category_file_CHI[category][file][feature] = self.obj_category_file_CHI_temp[category][file][feature]
                        self.obj_category_file_termcount[category][file] += self.obj_category_TF[category][file][feature]
                        #为了后面求tf-idf做准备
                        if feature not in self.dict_tfidf_param['count_include_feature']:
                            self.dict_tfidf_param['count_include_feature'][feature] = self.obj_category_file_CHI_param[category][file][feature]['a'] \
                            + self.obj_category_file_CHI_param[category][file][feature]['b']
                        if feature not in self.list_feature:
                            self.list_feature.append(feature)
        self.obj_category_file_CHI_temp.clear()
        self.obj_category_file_CHI_param_temp.clear()





    """
    tf-IDF权重
    """
    def get_term_TFIDF(self, file_TF_IDF):

        fp_TF_IDF_result = open(file_TF_IDF, 'w')
        for category in self.obj_category_file_CHI_param:
            self.obj_category_file_TF_IDF[category] = {}
            for file_num in self.obj_category_file_CHI_param[category]:
                self.obj_category_file_TF_IDF[category][file_num] = {}
                for term in self.obj_category_file_CHI_param[category][file_num]:
                    try:
                        tf = float(self.obj_category_TF[category][file_num][term]) / float(self.obj_category_file_termcount[category][file_num])
                        idf = math.log(float(self.N) / float((self.dict_tfidf_param['count_include_feature'][term])))
                        self.obj_category_file_TF_IDF[category][file_num][term] = tf * idf
                    except Exception:
                        sys.stderr.write(traceback.format_exc())
                        continue
        fp_TF_IDF_result.write(json.dumps(self.obj_category_file_TF_IDF))
        fp_TF_IDF_result.close()
    def test(self, file_VSM, file_list_feature):
        #测试dict中中文key和list中文内容能否匹配
        with open(file_VSM, 'r') as fp_vsm:
            with open(file_list_feature, 'r') as fp_list_feature:
                obj_category_file_vsm = json.load(fp_vsm)
                list_feature = json.load(fp_list_feature)
                # for category in obj_category_file_vsm:
                #     for file_num in obj_category_file_vsm[category]:
                #         # if '整合'.decode('utf8') in obj_category_file_vsm[category][file_num]:
                #         #     print ('整合')
                #         for term in obj_category_file_vsm[category][file_num]:
                #             if term in list_feature:
                #                 print (term)
                for feature in list_feature:
                    for category in obj_category_file_vsm:
                        for file_num in obj_category_file_vsm[category]:
                            if feature in obj_category_file_vsm[category][file_num]:
                                print (feature)
                            break
                        break

    """
    获得vsm，赋值到self.obj_category_file_CHI
    """
    def get_VSM(self, file_VSM):
        # 原先理解出错，以为卡方和权重乘积是最终的vsm
        # for category in self.obj_category_file_CHI:
        #     for file_num in self.obj_category_file_CHI[category]:
        #         for term in self.obj_category_file_CHI[category][file_num]:
        #             try:
        #                 print (self.obj_category_file_CHI[category][file_num][term], self.obj_category_file_TF_IDF[category][file_num][term])
        #                 self.obj_category_file_vsm = self.obj_category_file_CHI[category][file_num][term] * self.obj_category_file_TF_IDF[category][file_num][term] 
        #             except Exception:
        #                 sys.stderr.write('相关数据无法获取,category:' + str(category)  + 'file_num:' + str(file_num)  + 'term:' + str(term))
        #                 sys.stderr.write(traceback.format_exc())
        #                 break
        # with open(file_VSM, 'w') as fp_VSM_result:
        #     json.dump(self.obj_category_file_vsm, fp_VSM_result)
        self.obj_category_file_vsm = self.obj_category_file_TF_IDF
        with open(file_VSM, 'w') as fp_VSM_result:
            json.dump(self.obj_category_file_vsm, fp_VSM_result, ensure_ascii=False, indent=4)

    """
    生成测试用文本向量
    """
    def get_test_file_VSM(self, file_tfidf_param, file_test_vsm):
        with open(file_tfidf_param, 'r') as fp_tfidf_param:
            self.dict_tfidf_param = json.load(fp_tfidf_param)
        self.N = self.dict_tfidf_param['N']
        for category in self.obj_category_TF:
            self.obj_category_file_vsm[category] = {}
            for file in self.obj_category_TF[category]:
                self.obj_category_file_vsm[category][file] = {}
                for term in self.obj_category_TF[category][file]:
                    if term in self.dict_tfidf_param['count_include_feature']:
                        tf = float(self.obj_category_TF[category][file][term]) / float(self.obj_category_file_termcount[category][file])
                        # 通过之前模型的的tfidf文件生成当前向量的tfidf值
                        idf = math.log(float(self.N + 1) / float((self.dict_tfidf_param['count_include_feature'][term] + 1)))
                        self.obj_category_file_vsm[category][file][term] = tf * idf
        with open(file_test_vsm, 'w') as fp_test_vsm:
            json.dump(self.obj_category_file_vsm, fp_test_vsm)

    """
    获得obj_category_file_CHI_param
    """
    def get_term_CHI_param(self):
        return self.obj_category_file_CHI_param
   
    """
    获取obj_category_file_vsm
    """
    def get_obj_category_file_vsm(self):
        return self.obj_category_file_vsm

    """
    """
    def get_list_feature(self):
        return self.list_feature

def gen_model():
    text_category_list = ['财经','地域','电脑','房产','教育']
    #category对应词频
    obj_category_TF = {}
    #category对应词卡方
    obj_category_file_CHI = {}
    #category对应词卡方a,b,c,d
    obj_category_file_CHI_param = {}
#   最终的obj_category_file_vsm
    obj_category_file_vsm = {}
#    初始化对象
    text_pre = TextPretreatment(text_category_list)
#   停用词表文件路径
    file_stop_word = './functional_file/stopword.txt'
#    待读入文本文件目录
    file_dir = './datasets/TanCorp-12-Txt/TanCorp-12-Txt/'
    file_tf_result = './result_file/tf_result'
    file_category_file_termcount = './result_file/termcount_result'
#   特征列表文件
    file_list_feature = './result_file/list_feature_json'
#    CHI输出文件
    file_CHI = './result_file/CHIresult'
    file_CHI_param = './result_file/CHI_param_result'
    file_tfidf_param = './result_file/tfidf_param_result'
    file_TF_IDF = './result_file/TF_IDF_result'
#    VSM输出文件
    file_VSM = './result_file/VSM_result'
#    特征提取流程
    text_pre.get_stop_list(file_stop_word)
    text_pre.get_term_frequency(file_dir, file_tf_result, file_category_file_termcount, file_count_limit = 100)
    text_pre.get_term_CHI(file_CHI, file_CHI_param, file_tfidf_param, file_list_feature, feature_num_one_doc = 50)
    text_pre.get_term_TFIDF(file_TF_IDF)
    text_pre.get_VSM(file_VSM)
    # text_pre.test(file_VSM, file_list_feature)
    
    obj_category_file_vsm = text_pre.get_obj_category_file_vsm()
    list_feature = text_pre.get_list_feature()
    print (json.dumps(list_feature))
#   初始化knn对象
    knn_model = knn.KnnClass()
    file_kd = './result_file/kd_tree_result'
    file_kd_dict = './result_file/kd_tree_dict_result'
    
    #生成kd树并且保存到文件中
    knn_model.gen_kd_tree(obj_category_file_vsm, list_feature, file_kd, file_kd_dict)
    knn_model.do_classification(obj_category_file_vsm)



def test_kd_tree():
    text_category_list = ['财经']
#   最终的obj_category_file_vsm
    obj_category_file_vsm = {}
#    初始化对象
    text_pre = TextPretreatment(text_category_list)
#   停用词表文件路径
    file_stop_word = './functional_file/stopword.txt'
#    待读入文本文件目录
    file_dir = './datasets/test_category/'
    file_tfidf_param = './result_file/tfidf_param_result'
    file_list_feature = './result_file/list_feature_json'
#    VSM输出文件
    file_test_vsm = './result_file/test_vsm_result'
    file_knn_vsm = './result_file/VSM_result'
#    特征提取流程
    text_pre.get_stop_list(file_stop_word)
    text_pre.get_term_frequency(file_dir, file_count_limit = 50)
    text_pre.get_test_file_VSM(file_tfidf_param, file_test_vsm)
    # text_pre.test(file_VSM, file_list_feature)
    
    obj_category_file_vsm = text_pre.get_obj_category_file_vsm()
    print (json.dumps(obj_category_file_vsm))

    file_kd = './result_file/kd_tree_result'
    knn_classification = knn.KnnClass()
    # knn_classification.gen_kd_tree_by_file(file_kd, file_list_feature)

    # knn_classification.do_classification(obj_category_file_vsm)
    knn_classification.violence_travel(file_knn_vsm, file_list_feature, obj_category_file_vsm, k=3)


if __name__ == '__main__':
    # gen_model()
    test_kd_tree()
    

    # knn_classification = knn.KnnClass()
    # knn_classification.gen_kd_tree_by_file(file_kd, file_list_feature)

    # knn_classification.do_classification(obj_category_file_vsm)


    
    
   
      

        
