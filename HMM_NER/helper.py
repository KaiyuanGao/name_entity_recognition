# coding=utf-8
# @author: kaiyuan
# blog: https://blog.csdn.net/Kaiyuan_sjtu
# coding=utf-8
import os
import nltk
from tqdm import tqdm

class Helper():
    """
    For data preprocess
    """
    def __init__(self):
        """初始化转移矩阵，发射矩阵"""
        transition_probability = {'0': {},
                                       '1': {},
                                       '2': {},
                                       '3': {},
                                       '4': {},
                                       '5': {},
                                       '6': {},
                                       '7': {},
                                       '8': {},
                                       '9': {},
                                       '10': {},
                                       '11': {},
                                       '12': {}
                                       }

        emission_probability = {'0': {},
                                     '1': {},
                                     '2': {},
                                     '3': {},
                                     '4': {},
                                     '5': {},
                                     '6': {},
                                     '7': {},
                                     '8': {},
                                     '9': {},
                                     '10': {},
                                     '11': {},
                                     '12': {}
                                     }
        self.init_probility()


    def get_states():
        """
        隐状态
        :return:
        """
        states = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')
        return states

    def get_observationsunicode(sentence):
        """
        unicode格式的观察状态格式
        :param sentence:
        :return:
        """
        word_list = []
        for i in sentence:
            word_list.append(i)
        return tuple(word_list)

    def get_word_tag(self):
        """
        获取词和标注
        :return: word_tag_list
        """
        with open('dict/rmrb.txt', 'r', encoding='utf-8') as fr:
            word_tag_list = []
            for line in tqdm(fr):
                line = line.replace("\n", "").replace("\r", "")
                wtags = line.split(" ")
                for wt in wtags:
                    w_t = wt.split("/")
                    if len(w_t) == 2:
                        word_tag_list.append((w_t[0], w_t[1]))
        return word_tag_list

    def get_tag_tag(self):
        """
        获取前一个标注 后一个标注的组合
        :return: tag_tag_list
        """
        with open('dict/rmrb.txt', 'r', encoding='utf-8') as fr:
            tag_tag_list = []
            for line in tqdm(fr):
                line = line.replace("\n", "").replace("\r", "")
                if line != "":
                    wtags = line.split(" ")
                    for i in range(len(wtags) - 1):
                        forward_w_t = wtags[i].split("/")
                        backward_w_t = wtags[i + 1].split("/")
                        if len(backward_w_t) == 2:
                            tag_tag_list.append((forward_w_t[1], backward_w_t[1]))
        return tag_tag_list

    def get_words(self, word_tag_list):
        """
        获取全部字
        :param word_tag_list:
        :return:
        """
        fw = open('dict/words.txt', 'w')
        words = []
        for w, t in word_tag_list:
            words.append(w)
        onlywords = set(words)
        for w in onlywords:
            fw.write(w + " ")
        fw.close()
        print(len(onlywords))
        return onlywords

    def get_start_probability(self, word_tag_list):
        """
        开始概率：标注的初始概率
        :param word_tag_list:
        :return:
        """
        fdist = nltk.FreqDist(t for w, t in word_tag_list)
        print(fdist.items())

    def get_emission_probability(self, word_tag_list):
        """
        获取发射概率，字对应的标注的概率
        :param words:
        :param word_tag_list:
        :return:
        """
        start_pro = self.load_start_profortransemi()

        wf = open('dict/emission_probability.txt', 'w+')
        fdist = nltk.FreqDist(word_tag_list)
        for key, value in fdist.items():
            print(key[1], key[0], value, fdist.freq(key) / start_pro[key[1]][0])
            wf.write(key[1] + ' ' + key[0] + ' ' + str(value) + ' ' + str(fdist.freq(key) / start_pro[key[1]][0]))
            wf.write('\n')
        wf.close()

    def get_transition_probability(self, tag_tag_list):
        """
        获取转移概率 前标注转移下一个标注的概率
        :param tag_tag_list:
        :return:
        """
        wf = open('dict/transition_probability.txt','w+')
        start_pro = self.load_start_profortransemi()
        fdist = nltk.FreqDist(tag_tag_list)
        print(fdist.items())
        for key, value in fdist.items():
            condition_pro2 = value*1.00 / start_pro[key[0]][0]
            print('频率/频率的条件概率', key[0], key[1], value, condition_pro2)
            wf.write(key[0]+' '+key[1]+' '+str(value)+' '+str(condition_pro2))
            wf.write('\n')
        wf.close()

    def load_start_profortransemi(self, path='dict/start_probability.txt'):
        """
        用于计算转移概率 发射概率的格式封装，便于计算
        :param path:
        :return:
        """
        start_pro = {}
        rf = open(path, 'r')
        lines = rf.readlines()
        for line in lines:
            line = line.replace("\n", '')
            tag_pro = line.split(" ")
            start_pro[tag_pro[0]] = [eval(tag_pro[1]), eval(tag_pro[2])]
        return start_pro

    def load_words(self, path='dict/words.txt'):
        """
        把语料的字全部加载进来，用于初始化方法
        :param path:
        :return:
        """
        rf = open(path, 'r')
        lines = rf.readlines()
        words = []
        for line in lines:
            line = line.replace("\n", "")
            words = line.split(" ")
            words.remove(words[0])
        return words

    def init_probility(self):
        """
        初始化转移概率 发射概率的值为0
        :return:
        """
        words = self.load_words()
        for state0 in self.get_states():
            for state1 in self.get_states():
                self.transition_probability[state0][state1] = 0
            for word in words:
                self.emission_probability[state0][word] = 0

    def load_start_pro(self, path='dict/start_probability.txt'):
        """
        hmm 维特比计算的时候，初始概率的格式封装
        :param path:
        :return:
        """
        start_pro = {}
        rf = open(path, 'r')
        lines = rf.readlines()
        for line in lines:
            line = line.replace("\n", '')
            tag_pro = line.split(" ")
            start_pro[tag_pro[0]] = eval(tag_pro[2])
        return start_pro

    def load_transition_pro(self, path='dict/transition_probability.txt'):
        """
        hmm 维特比计算的时候，转移概率的封装
        :param path:
        :return:
        """
        rf = open(path, 'r')
        lines = rf.readlines()
        for line in lines:
            line = line.replace("\n", '')
            tag_totag_pro = line.split(" ")
            self.transition_probability[tag_totag_pro[0]][tag_totag_pro[1]] = eval(tag_totag_pro[3])
        return self.transition_probability

    def load_emission_pro(self, path='dict/emission_probability.txt'):
        """
        hmm 维特比计算的时候，发射概率的格式封装
        :param path:
        :return:
        """
        rf = open(path, 'r')
        lines = rf.readlines()
        for line in lines:
            line = line.replace("\n", '')
            tag_toword_pro = line.split(" ")
            # print tag_toword_pro
            self.emission_probability[tag_toword_pro[0]][tag_toword_pro[1]] = eval(tag_toword_pro[3])
        return self.emission_probability
