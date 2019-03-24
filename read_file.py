# -*- coding: utf-8 -*-
import json
import math
import sys
import traceback

#fp = open('..\datasets\TanCorp-12-Txt\TanCorp-12-Txt\财经\0.txt', 'r')
#['财经','地域','电脑','房产','教育','科技','汽车','人才','体育','卫生','艺术','娱乐']

class TextPretreatment():
    text_category_list = []
    #category对应词频
    obj_category_TF = {}
    #category对应文件下切词总数
    obj_category_file_termcount = {}
    #category对应词卡方
    obj_category_file_CHI = {}
    #category对应词卡方a,b,c,d
    obj_category_file_CHI_param = {}
#    category对应词tf-idf
    obj_category_file_TF_IDF = {}
#    输入文档总数
    N = 0
#    每个类别下文件总数，修改
    sum = 1
    def __init__(self, text_category_list):
        self.text_category_list = text_category_list
    #生成category对应词频
    def get_term_frequency(self, file_dir, file_result):
        fp_result = open(file_result, 'w')
        for category in text_category_list:
            counter = 1
            self.obj_category_TF[category] = {}
            self.obj_category_file_termcount[category] = {}
            while counter <= sum:
                self.obj_category_TF[category][counter] = {}
                self.obj_category_file_termcount[category][counter] = 0
                fp = open(file_dir + category + '/' + str(counter) + '.txt', 'r')
                for line in fp:
                    line = line.strip('\r\n')
                    word_list = line.split()
                    for word in word_list: 
                        if word in self.obj_category_TF[category][counter]:
                            self.obj_category_TF[category][counter][word] = self.obj_category_TF[category][counter][word] + 1
                        else:
                            self.obj_category_TF[category][counter][word] = 1;
                        self.obj_category_file_termcount[category][counter] = self.obj_category_file_termcount[category][counter] + 1
                fp.close()  
                counter = counter + 1        

        fp_result.write(json.dumps(self.obj_category_TF))
        fp_result.close()
        print (self.obj_category_file_termcount)
        return self.obj_category_TF
#    生成category对应词卡方
    def get_term_CHI(self, file_CHI, file_CHI_param):
#    特征提取都是以文件为单位
#    卡方检验

        fp_CHI_result = open(file_CHI, 'w')
        fp_CHI_param_result = open(file_CHI_param, 'w')
        for category in self.obj_category_TF:
            self.obj_category_file_CHI_param[category] = {}
            self.obj_category_file_CHI[category] = {}
            for file_num in self.obj_category_TF[category]:
                self.obj_category_file_CHI_param[category][file_num] = {}
                self.obj_category_file_CHI[category][file_num] = {}
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
#                    修改：分母为零时如何处理
                    if (deno == 0):
                        self.obj_category_file_CHI[category][file_num][word] = float(math.pow((a*d)-(b*d), 2))
                    else:
                        self.obj_category_file_CHI[category][file_num][word] = float(math.pow((a*d)-(b*d), 2))/float(deno)
                    self.obj_category_file_CHI_param[category][file_num][word] = {}
                    self.obj_category_file_CHI_param[category][file_num][word]['word'] = word
                    self.obj_category_file_CHI_param[category][file_num][word]['a'] = a
                    self.obj_category_file_CHI_param[category][file_num][word]['b'] = b
                    self.obj_category_file_CHI_param[category][file_num][word]['c'] = c
                    self.obj_category_file_CHI_param[category][file_num][word]['d'] = d
                    
        fp_CHI_result.write(json.dumps(self.obj_category_file_CHI))
        fp_CHI_result.close()
        fp_CHI_param_result.write(json.dumps(self.obj_category_file_CHI_param))
        fp_CHI_param_result.close()
        return self.obj_category_file_CHI
#    获得obj_category_file_CHI_param
    def get_term_CHI_param(self):
        return self.obj_category_file_CHI_param
    
#    tf-IDF权重 
    def get_term_TFIDF(self, file_TF_IDF):
#       文档总数
        self.N = 0
        for category in self.obj_category_TF:
            self.N = self.N + len(self.obj_category_TF[category])
        print(self.N)
        fp_TF_IDF_result = open(file_TF_IDF, 'w')
        for category in self.obj_category_file_CHI_param:
            self.obj_category_file_TF_IDF[category] = {}
            for file_num in self.obj_category_file_CHI_param[category]:
                self.obj_category_file_TF_IDF[category][file_num] = {}
                for term in self.obj_category_file_CHI_param[category][file_num]:
                    try:
                        tf = float(self.obj_category_TF[category][file_num][term]) / float(self.obj_category_file_termcount[category][file_num])
                        idf = math.log(float(N) / float((self.obj_category_file_CHI_param[category][file_num][term]['a'] + self.obj_category_file_CHI_param[category][file_num][term]['b'])))
                        self.obj_category_file_TF_IDF[category][file_num][term] = tf * idf
                    except Exception:
                        sys.stderr.write(traceback.format_exc())
                        continue
        fp_TF_IDF_result.write(json.dumps(self.obj_category_file_TF_IDF))
        fp_TF_IDF_result.close()
    def test(self):
        print (self.text_category_list)

   



if __name__ == '__main__':
    text_category_list = ['财经','地域','电脑','房产','教育']
    #category对应词频
    obj_category_TF = {}
    #category对应词卡方
    obj_category_file_CHI = {}
    #category对应词卡方a,b,c,d
    obj_category_file_CHI_param = {}
#    初始化对象
    text_pre = TextPretreatment(text_category_list)   
#    待读入文件目录
    file_dir = '../datasets/TanCorp-12-Txt/TanCorp-12-Txt/'
    file_result = './result_file/result'
#    CHI输出文件
    file_CHI = './result_file/CHIresult'
    file_CHI_param = './result_file/CHI_param_result'
    file_TF_IDF = './result_file/TF_IDF_result'
#    特征提取流程
    obj_category_TF = text_pre.get_term_frequency(file_dir, file_result)
    obj_category_file_CHI = text_pre.get_term_CHI(file_CHI, file_CHI_param)
    obj_category_file_CHI_param = text_pre.get_term_CHI_param()
    text_pre.get_term_TFIDF(file_TF_IDF)
    
    
    
    
    
   
      

        