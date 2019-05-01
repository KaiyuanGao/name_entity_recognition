# coding=utf-8
# @author: kaiyuan
# blog: https://blog.csdn.net/Kaiyuan_sjtu

from tqdm import tqdm
import re

def process_k(words):
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

def map_tag(pro_words):
    new = []
    for item in pro_words:
        if len(item) > 1:
            w, t = item.rsplit('/', 1)
            if t == 'nz':
                if len(w) > 2:
                    new_w = w[0] + '/10' + ' ' + ' '.join([w[i] + '/11' for i in range(1, len(w) - 1)]) + ' ' + w[
                        -1] + '/12'
                elif len(w) == 2:
                    new_w = w[0] + '/10' + ' ' + w[-1] + '/12'
                else:
                    new_w = w[0] + '/10'
                new.append(new_w)
            elif t == 'nt':
                if len(w) > 2:
                    new_w = w[0] + '/1' + ' ' + ' '.join([w[i] + '/2' for i in range(1, len(w) - 1)]) + ' ' + w[-1] + '/3'
                elif len(w) == 2:
                    new_w = w[0] + '/1' + ' ' + w[-1] + '/3'
                else:
                    new_w = w[0] + '/1'
                new.append(new_w)
            elif t == 'ns':
                if len(w) > 2:
                    new_w = w[0] + '/7' + ' ' + ' '.join([w[i] + '/8' for i in range(1, len(w) - 1)]) + ' ' + w[-1] + '/9'
                elif len(w) == 2:
                    new_w = w[0] + '/7' + ' ' + w[-1] + '/9'
                else:
                    new_w = w[0] + '/7'
                new.append(new_w)
            elif t == 'nr':
                if len(w) > 2:
                    new_w = w[0] + '/4' + ' ' + ' '.join([w[i] + '/5' for i in range(1, len(w) - 1)]) + ' ' + w[-1] + '/6'
                elif len(w) == 2:
                    new_w = w[0] + '/4' + ' ' + w[-1] + '/6'
                else:
                    new_w = w[0] + '/4'
                new.append(new_w)
            else:
                if len(w) > 2:
                    new_w = w[0] + '/0' + ' ' + ' '.join([w[i] + '/0' for i in range(1, len(w) - 1)]) + ' ' + w[-1] + '/0'
                elif len(w) == 2:
                    new_w = w[0] + '/0' + ' ' + w[-1] + '/0'
                else:
                    new_w = w[0] + '/0'
                new.append(new_w)
        else:
            new.append(item)
    return ' '.join(new)

fw = open('dict/rmrb.txt', 'w', encoding='utf-8')
with open('D:/NLP/data/renmin/2014_corpus.txt', 'r', encoding='utf-8') as fr:
    for line in tqdm(fr):
        words = line.strip().split(' ')
        pro_words = process_k(words)
        new_line = map_tag(pro_words)
        fw.write(new_line)
        fw.write('\n')

