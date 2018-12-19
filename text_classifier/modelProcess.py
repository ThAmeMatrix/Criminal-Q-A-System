#-*- coding:utf-8 -*-
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
import jpype

import os
import re

# (2017)浙0411刑初299号在哪里

class Naive_Bayes:
    """
            casePerson
            0: 没有出现
            1: 出现case
            2: 出现Person

            yearLocation
            0: 没有出现
            1: 出现year
            2: 出现location
            3: year和location都出现
        """
    doubleExist = 0

    n_set = set()

    vocabulary = []
    abstractMap = {
        "nCase": "",
        "nPerson": "",
        "nYear": "",
        "nLocation": ""
    }
    questionsPattern = {}

    nVocabulary = 0
    nTrain = 0

    nCaseAdd = ["", "的", "是", "里", "里的", "内", "内的", "中", "中的"]
    nPersonAdd = ["", "案件", "案子", "的案件", "的案子", "涉及的案件", "涉及的案子"]

    nTeamYouthAdd = [["团体", "团队", "团伙", "组团", "组队"],
                     ["年轻人", "青年", "青年人", "青少年", "青壮", "青壮年", "少年", "少女", "男孩", "女孩"]]
    nPenalAdd = ["犯罪", "犯案", "作案"]
    nRatioAdd = ["率", "比例", "的比例", "比率", "的比率"]
    nRatioPlusAdd = ["总", "总共", "总的来说", "一共", "总的"]

    nCharEnd = ["?", "？", ",", "，", ".", "。", "!", "！"]

    def __init__(self, pathDir):
        """
        # vocabulary(old)
        file = open(pathDir + "vocabulary.txt", "r", encoding='utf-8')
        file_res = file.read()
        line_res = file_res.split('\n')
        self.nVocabulary = len(line_res)
        for line in line_res:
            s = line.split(':')
            self.vocabulary.append(s[1])
        """

        """
        # train_list(old)
        dataSet = pd.read_csv(pathDir + "train_list.csv")
        columns = list(dataSet.columns)
        X = dataSet[columns[:-1]]
        y = dataSet[columns[-1]]
        X = np.array(X)
        y = np.array(y).reshape((y.size,))
        m, n = X.shape
        self.nTrain = m
        """

        # question_classification
        file = open(pathDir + "question_classification.txt", "r", encoding='utf-8')
        file_res = file.read()
        line_res = file_res.split('\n')
        for line in line_res:
            s = line.split(':')
            self.questionsPattern[s[0]] = s[1]

        print("questionsPattern")
        print(self.questionsPattern)

        train_path = pathDir + '/train_list_of_question_type/'
        rt = os.listdir(train_path)

        X = []
        y = []

        # train_list
        for allDir in rt:
            path = os.path.join(train_path, allDir)
            f1 = open(path, "r", encoding='UTF-8')
            f_res = f1.read()
            f1.close()
            line_res = f_res.split('\n')
            print(allDir)
            label = int(str(re.search(re.compile('【\d+】'), allDir).group())[1:-1])
            for i in line_res:
                print(i)
                if '\ufeff' in i:
                    i = i.replace('\ufeff', '')
                # team or youth
                inx = -1
                if re.search('team', i):
                    inx = 0
                    i = i.replace("team", "")
                if re.search('youth', i):
                    inx = 1
                    i = i.replace("youth", "")
                if inx != -1:
                    for tt in self.nTeamYouthAdd[inx]:
                        j = i + tt
                        print(j)
                        X.append(j)
                        y.append(label)
                        for shy in self.nPenalAdd:
                            k = j + shy
                            print(k)
                            X.append(k)
                            y.append(label)
                            for szy in self.nRatioAdd:
                                l = k + szy
                                print(l)
                                X.append(l)
                                y.append(label)
                                for lyh in self.nRatioPlusAdd:
                                    m = l + lyh
                                    print(m)
                                    X.append(m)
                                    y.append(label)
                # insert original model
                X.append(i)
                self.addtoVocabulary(i, 1)
                y.append(label)

                # nCase or nPerson
                if re.search('nCase', i):
                    inx1 = i.find("e")
                    for tt in self.nCaseAdd:
                        j = i[:(inx1 + 1)] + tt + i[(inx1 + 1):]
                        print(j)
                        X.append(j)
                        y.append(label)
                        k = j.replace('nCase', 'nPerson')
                        inx2 = k.find("on")
                        for shy in self.nPersonAdd:
                            ll = k[:(inx2 + 2)] + shy + k[(inx2 + 2):]
                            print(ll)
                            X.append(ll)
                            y.append(label)
                # nYear or/and nLocation
                elif re.search('nYear', i):
                    inx = i.find("r")
                    for tt in self.nCaseAdd:
                        j = i[:(inx + 1)] + tt + i[(inx + 1):]
                        print(j)
                        X.append(j)
                        y.append(label)

                        k1 = j.replace('nYear', 'nLocation')
                        print(k1)
                        X.append(k1)
                        y.append(label)
                        inx1 = k1.find("on")

                        k2 = j[:(inx + 1)] + "_nLocation" + j[(inx + 1):]
                        print(k2)
                        X.append(k2)
                        y.append(label)
                        inx2 = k2.find("on")

                        for shy in self.nPersonAdd:
                            ll = k1[:(inx1 + 2)] + shy + k1[(inx1 + 2):]
                            print(ll)
                            X.append(ll)
                            y.append(label)

                            ll = k2[:(inx2 + 2)] + shy + k2[(inx2 + 2):]
                            print(ll)
                            X.append(ll)
                            y.append(label)
                elif re.search('nPerson', i):
                    print("Ignore me")
                else:
                    j = 'nLocation' + i
                    print(j)
                    X.append(j)
                    y.append(label)

        # vocabulary
        self.addtoVocabulary("", 0)
        for i in self.n_set:
            self.vocabulary.append(i)

        self.nVocabulary = len(self.vocabulary)

        print("self.nVocabulary\n", self.nVocabulary)
        print(self.vocabulary)

        print("X\n", X)
        print("y\n", y)

        self.nTrain = len(y)
        print("nTrain:", self.nTrain)

        X_ = [[0.0 for col in range(self.nVocabulary)] for row in range(self.nTrain)]
        for i in range(self.nTrain):
            # print(i, X[i][0])
            X_[i] = self.sentenceToArrays(str(X[i]))

        self.clf = GaussianNB()
        self.clf.fit(X_, y)

    def predict(self, original_question):

        print("original_question:", original_question)

        self.doubleExist = 0

        # 抽象句子，利用HanLP分词，将关键字进行词性抽象
        abstr = self.queryAbstract(original_question)
        print("abstract str:", abstr)  # nCase 涉案 人数 是 多少

        # 将抽象的句子与训练集中的模板进行匹配，拿到句子对应的模板
        strPatt, modelIndex = self.queryClassify(abstr)
        print("str pattern:", strPatt)  # nCase 人数

        # 模板还原成句子，此时问题已转换为我们熟悉的操作
        finalPatt = self.queryExtenstion(strPatt)  # (2017)浙0402刑初277号 涉案 人数 是 多少
        print("final pattern:", finalPatt)

        print("modelIndex:", modelIndex)
        print("abstractMap:", self.abstractMap)

        infoMap = self.abstractMap

        self.abstractMap = {
            "nCase": "",
            "nPerson": "",
            "nYear": "",
            "nLocation": ""
        }

        return modelIndex, self.doubleExist, infoMap

    def queryAbstract(self, original_question):
        print("========HanLP开始分词========")
        HanLP = jpype.JClass("com.hankcs.hanlp.HanLP")
        terms = HanLP.segment(original_question)
        abstr = ""

        for term in terms:
            print(term)
            if "nCase" in str(term):
                abstr += "nCase "
                self.abstractMap['nCase'] = term.word
                if self.doubleExist == 2:
                    self.doubleExist = 3
                else:
                    self.doubleExist = 1
            elif "nPerson" in str(term):
                abstr += "nPerson "
                self.abstractMap['nPerson'] = term.word
                if self.doubleExist == 1:
                    self.doubleExist = 3
                else:
                    self.doubleExist = 2
            elif "nYear" in str(term):
                abstr += "nYear "
                self.abstractMap['nYear'] = str(re.search(re.compile('\d+'), term.word).group())
                if self.doubleExist == 2:
                    self.doubleExist = 3
                else:
                    self.doubleExist = 1
            elif "nLocation" in str(term):
                abstr += "nLocation "
                self.abstractMap['nLocation'] = term.word
                if self.doubleExist == 1:
                    self.doubleExist = 3
                else:
                    self.doubleExist = 2
                    # print("Ha?I'm here")
            else:
                abstr += term.word + " "
        print("========HanLP分词结束========")
        return abstr

    def queryClassify(self, abstr):

        test = [self.sentenceToArrays(abstr)]
        predict = self.clf.predict(test)
        # print("predict", predict)

        return self.questionsPattern[str(predict[0])], predict[0]

    def sentenceToArrays(self, sentence):
        HanLP = jpype.JClass("com.hankcs.hanlp.HanLP")
        terms = HanLP.segment(sentence)

        vv = [0.0] * self.nVocabulary

        for term in terms:
            s = str(term).split('/')
            # print(s[0], s[1])
            if s[0] in self.vocabulary:
                vv[self.vocabulary.index(s[0])] = 1.0

        return vv

    def addtoVocabulary(self, sentence, sig):
        if sig == 0:
            for i in self.nCaseAdd: self.n_set.add(i)
            for i in self.nPersonAdd: self.n_set.add(i)
            for i in self.nTeamYouthAdd:
                for j in i:
                    self.n_set.add(j)
            for i in self.nPenalAdd: self.n_set.add(i)
            for i in self.nRatioAdd: self.n_set.add(i)
            for i in self.nRatioPlusAdd: self.n_set.add(i)
            for i in self.nCharEnd: self.n_set.add(i)
        else:
            HanLP = jpype.JClass("com.hankcs.hanlp.HanLP")
            terms = HanLP.segment(sentence)

            for term in terms:
                s = str(term).split('/')
                # print(s[0], s[1])
                self.n_set.add(s[0])

    def queryExtenstion(self, sentence):
        for i in self.abstractMap:
            # print(i)
            if i in sentence:
                sentence = sentence.replace(i, self.abstractMap[i])
        return sentence


if __name__ == '__main__':
    jpype.startJVM(jpype.getDefaultJVMPath(), "-Djava.class.path=D:\Software\HanLP\hanlp-1.7.0.jar;D:\Software\HanLP",
                   "-Xms1g",
                   "-Xmx1g")  # 启动JVM，Linux需替换分号;为冒号:
    nb = Naive_Bayes("../data/question/")
    nb.predict("2017年总的罚金")
    nb.predict("2018年总的罚金")
