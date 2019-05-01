# coding=utf-8
# @author: kaiyuan
# blog: https://blog.csdn.net/Kaiyuan_sjtu
import re
from config import get_config
import tqdm
def full2half(full_str):
    """
    全角转换成半角
    :param full_str:
    :return:
    """
    half_str = ''
    for char in full_str:
        inside_code = ord(char)
        if inside_code == 12288:    # space
            inside_code = 32
        elif 65374 >= inside_code >= 65281:    # letter
            inside_code -= 65248
        half_str += chr(inside_code)
    return half_str

def half2full(half_str):
    """
    半角转换成全角
    :param half_str:
    :return:
    """
    full_str = ''
    for char in half_str:
        inside_code = ord(char)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif 126 >= inside_code >= 32:  # 半角字符（除空格）根据关系转化
            inside_code += 65248
        full_str += chr(inside_code)
    return full_str

__corpus = None

class Corpus:
    _config = get_config()
    # 实体对应表
    _maps = {'t': 'T',
             'nr': 'PER',
             'ns': 'ORG',
             'nt': 'LOC'}

    @classmethod
    def read_corpus(cls, file):
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return lines

    @classmethod
    def process_k(cls, words):
        """合并实体词"""
        pro_words = []
        index = 0
        temp = ''
        while True:
            word = words[index] if index < len(words) else ''
            if '[' in word:
                temp += re.sub(pattern='/[a-zA-Z]*', repl='', string=word.replace('[', ''))
            elif ']' in word:
                w = word.split(']')
                temp += re.sub(pattern='/[a-zA-Z]*', repl='', string=w[0])
                pro_words.append(temp + '/' + w[1])
                temp = ''
            elif temp:
                temp += re.sub(pattern='/[a-zA-Z]*', repl='', string=word)
            elif word:
                pro_words.append(word)
            else:
                break
            index += 1
        return pro_words

    @classmethod
    def process_t(cls, words):
        """处理时间"""
        pro_words = []
        index = 0
        temp = ''
        while True:
            word = words[index] if index < len(words) else ''
            if '/t' in word:
                temp = temp.replace('/t', '') + word
            elif temp:
                pro_words.append(temp)
                pro_words.append(word)
                temp = ''
            elif word:
                pro_words.append(word)
            else:
                break
            index += 1
        return pro_words

    @classmethod
    def process_nr(cls, words):
        """处理人名"""
        pro_words = []
        index = 0
        while True:
            word = words[index] if index < len(words) else ''
            if '/nr' in word:
                next_index = index + 1
                if next_index < len(words) and '/nr' in words[next_index]:
                    pro_words.append(word.replace('/nr', '') + words[next_index])
                    index = next_index
                else:
                    pro_words.append(word)
            elif word:
                pro_words.append(word)
            else:
                break
            index += 1
        return pro_words

    @classmethod
    def write_corpus(cls, data, file):
        with open(file, 'w', encoding='utf-8') as f:
            f.write(data)


    @classmethod
    def pre_process(cls):
        train_corpus_path = cls._config.get('ner', 'train_corpus_path')
        lines = cls.read_corpus(train_corpus_path)
        new_lines = []
        for line in lines:
            words = full2half(line.strip()).split(' ')
            pro_words = cls.process_t(words)
            pro_words = cls.process_nr(pro_words)
            pro_words = cls.process_k(pro_words)
            new_lines.append('  '.join(pro_words[1:]))
        process_corpus_path = cls._config.get('ner', 'process_corpus_path')
        cls.write_corpus('\n'.join(new_lines), process_corpus_path)

    @classmethod
    def pos2tag(cls, p):
        t = cls._maps.get(p, None)
        return t if t else 'O'

    @classmethod
    def tag_perform(cls, tag, index):
        if index == 0 and tag != 'O':
            return 'B_{}'.format(tag)
        elif tag != 'O':
            return 'I_{}'.format(tag)
        else:
            return tag

    @classmethod
    def pos_perform(cls, pos):
        """去除词性标签 """
        if pos in cls._maps.keys() and pos != 't':
            return 'n'
        else:
            return pos

    @classmethod
    def init_seq(cls, words_list):
        """"""
        words_seq = [[word.split('/')[0] for word in words] for words in words_list]
        pos_seq = [[word.split('/')[1] for word in words] for words in words_list]
        tag_seq = [[cls.pos2tag(p) for p in pos] for pos in pos_seq]
        cls.pos_seq = [[[pos_seq[index][i] for _ in range(len(words_seq[index][i]))]
                        for i in range(len(pos_seq[index]))] for index in range(len(pos_seq))]
        cls.tag_seq = [[[cls.tag_perform(tag_seq[index][i], w) for w in range(len(words_seq[index][i]))]
                        for i in range(len(tag_seq[index]))] for index in range(len(tag_seq))]
        cls.pos_seq = [['un'] + [cls.pos_perform(p) for pos in pos_seq for p in pos] + ['un'] for pos_seq in
                       cls.pos_seq]
        cls.tag_seq = [[t for tag in tag_seq for t in tag] for tag_seq in cls.tag_seq]
        cls.word_seq = [['<BOS>'] + [w for word in word_seq for w in word] + ['<EOS>'] for word_seq in words_seq]


    @classmethod
    def initialize(cls):
        corpus_path = cls._config.get('ner', 'process_corpus_path')
        lines = cls.read_corpus(corpus_path)
        words_list = [line.split('  ') for line in lines if line.strip()]
        del lines
        cls.init_seq(words_list)

    @classmethod
    def segment_by_window(cls, words_list=None, window=3):
        words = []
        begin, end = 0, window
        for _ in range(1, len(words_list)):
            if end > len(words_list):
                break
            words.append(words_list[begin:end])
            begin += 1
            end += 1
        return words

    @classmethod
    def extract_features(cls, word_grams):
        features, feature_list = [], []
        for index in range(len(word_grams)):
            for i in range(len(word_grams[index])):
                word_gram = word_grams[index][i]
                feature = {'w-1': word_gram[0], 'w': word_gram[1], 'w+1': word_gram[2],
                           'w-1:w': word_gram[0] + word_gram[1], 'w:w+1': word_gram[1] + word_gram[2],
                           'bias': 1.0}
                feature_list.append(feature)
            features.append(feature_list)
            feature_list = []
        return features

    @classmethod
    def generator(cls):
        word_grams = [cls.segment_by_window(words_list) for words_list in cls.word_seq]
        features = cls.extract_features(word_grams)
        return features, cls.tag_seq

    def __init__(self):
        raise Exception('This class has not element method')

def get_corpus():
    global __corpus
    if not __corpus:
        __corpus = Corpus
    return __corpus

if __name__ == '__main__':
    corpus = get_corpus()
    corpus.pre_process()
