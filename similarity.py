import numpy as np
import pandas as pd
import os
import datetime
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
import re
import math
from gensim.models import KeyedVectors


model = KeyedVectors.load_word2vec_format(r'D:\tencent-ailab-embedding-zh-d200-v0.2.0-s.txt', binary=False, limit=10000)


def word_similarity(word1, word2):
    if word1 not in model or word2 not in model:
        return 0
    return model.similarity(word1, word2)


def parseSen(blog):
    while True:
        body = urllib.parse.urlencode({'text': blog}).encode('utf-8')
        url = 'http://ltpapi.xfyun.cn/v1/cws'
        api_key = '32fc90f15cf3cc365dd0cd09f725fce0'
        param = {"type": "dependent"}
        x_appid = '31a62a47'
        x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
        x_time = int(int(round(time.time() * 1000)) / 1000)
        x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
        x_header = {'X-Appid': x_appid,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}
        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read().decode('utf-8')
        x = json.loads(result)
        if x['data']['word']:
            break
        print('No word: ' + blog)
    return x['data']['word']  # return a list of parse sentences


def roleBlog(blog):
    while True:
        body = urllib.parse.urlencode({'text': blog}).encode('utf-8')

        url = 'http://ltpapi.xfyun.cn/v1/sdp'
        api_key = '32fc90f15cf3cc365dd0cd09f725fce0'
        param = {"type": "dependent"}

        x_appid = '31a62a47'
        x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
        x_time = int(int(round(time.time() * 1000)) / 1000)
        x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
        x_header = {'X-Appid': x_appid,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}
        req = urllib.request.Request(url, body, x_header)
        result = urllib.request.urlopen(req)
        result = result.read().decode('utf-8')
        if json.loads(result)['data']['sdp']:
            break
    x = json.loads(result)['data']['sdp']
    y = []
    for n in range(len(x)):
        y.append(x[n]['relate'])
    return y  # return a list of role of words in sentences


def cal_count(allSen_p, role_sen, par_sen):
    count = []
    result = {}
    for n in range(len(par_sen)):
        num1 = 0
        num2 = 0
        for m in range(len(allSen_p)):
            for p in range(len(allSen_p[m])):
                if allSen_p[m][p] == par_sen[n]:
                    num1 += 1
            if par_sen[n] in allSen_p[m]:
                num2 += 1
        count.append(num1 * math.log((len(allSen_p) / num2) + 0.01))
        result[role_sen[n]] = count[n]
    return result


def cal_sen_Similarity(role_sen1, par_sen1, count1, role_sen2, par_sen2, count2):
    relation = ['Agt', 'Exp', 'Aft', 'Poss', 'Pat', 'Cont', 'Prod', 'Orig',
                'Datv', 'Comp', 'Belg', 'Clas', 'Accd', 'Reas',
                'Int', 'Cons', 'Mann', 'Tool', 'Malt', 'Time', 'Loc',
                'Proc', 'Dir', 'Sco', 'Quan', 'Qp', 'Freq', 'Seq', 'Desc',
                'Host', 'Nmod', 'Tmod', 'r + main role', 'd + main role',
                'eCoo', 'eSelt', 'eEqu', 'ePrec', 'eSucc', 'eProg',
                'eAdvt', 'eCau', 'eResu', 'eInf', 'eCond', 'eSupp', 'eConc',
                'eMetd', 'ePurp', 'eAban', 'ePref', 'eSum', 'eRect', 'mConj',
                'mAux', 'mPrep', 'mTone', 'mTime', 'mRang', 'mDegr', 'mFreq',
                'mDir', 'mPars', 'mNeg', 'mMod', 'mPunc', 'mPept', 'mMaj',
                'mVain', 'mSepa', 'Root']
    dict_sen1 = {}
    dict_sen2 = {}
    for n in range(len(par_sen1)):
        dict_sen1[role_sen1[n]] = par_sen1[n]
    for n in range(len(par_sen2)):
        dict_sen2[role_sen2[n]] = par_sen2[n]
    SIM = 0.0
    sim = word_similarity(dict_sen1['Root'], dict_sen2['Root'])
    sim_word = []
    for n in relation:
        if n in dict_sen1.keys() and n in dict_sen2.keys():
            result = word_similarity(dict_sen1[n], dict_sen2[n])
            if result is not None:
                sim_word.append(result)
    vector1 = []
    vector2 = []
    sim_v = 0.0
    for n in relation:
        if n != 'Root':
            if n in count1.keys() and n in count2.keys():
                vector1.append(count1[n])
                vector2.append(count2[n])
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    if (sum(vector1 ** 2) * sum(vector2 ** 2)) == 0:
        sim_v = 0
    else:
        sim_v = sum(vector1 * vector2) / ((sum(vector1 ** 2) * sum(vector2 ** 2)) ** 0.5)
    SIM = 0.3 * sim + 0.3 * sum(sim_word) / len(sim_word) + 0.4 * sim_v
    return SIM

# print(cal_sen_Similarity('我去他家', cal_count('我去他家', '我去他家'), '我回家', cal_count('我回家', '我回家')))


def cal_blog_Similarity(blog1, blog2):
    blog1_p = list(filter(None, re.split(r'[：，。！？?\s]\s*', blog1)))
    blog2_p = list(filter(None, re.split(r'[：，。！？?\s]\s*', blog2)))
    SIM = 0.0
    if len(blog1_p) == 1 and len(blog2_p) == 1:
        allSen1_p = []
        role_sen1 = []
        for p in range(len(blog1_p)):
            x = parseSen(blog1_p[p])
            y = roleBlog(blog1_p[p])
            allSen1_p.append(x)
            role_sen1.append(y)
        allSen2_p = []
        role_sen2 = []
        for p in range(len(blog2_p)):
            x = parseSen(blog2_p[p])
            y = roleBlog(blog2_p[p])
            allSen2_p.append(x)
            role_sen2.append(y)
        SIM = cal_sen_Similarity(role_sen1[0], allSen1_p[0], cal_count(allSen1_p, role_sen1[0], allSen1_p[0]), role_sen2[0], allSen2_p[0], cal_count(allSen2_p, role_sen2[0], allSen2_p[0]))
    elif len(blog1_p) == 1:
        sim1 = 0.0
        allSen1_p = []
        role_sen1 = []
        for p in range(len(blog1_p)):
            x = parseSen(blog1_p[p])
            y = roleBlog(blog1_p[p])
            allSen1_p.append(x)
            role_sen1.append(y)
        allSen2_p = []
        role_sen2 = []
        for p in range(len(blog2_p)):
            x = parseSen(blog2_p[p])
            y = roleBlog(blog2_p[p])
            allSen2_p.append(x)
            role_sen2.append(y)
        for n in range(len(blog2_p)):
            count_2 = cal_count(allSen2_p, role_sen2[n], allSen2_p[n])
            sim2 = cal_sen_Similarity(role_sen1[0], allSen1_p[0], cal_count(allSen1_p, role_sen1[0], allSen1_p[0]), role_sen2[n], allSen2_p[n], count_2)
            if sim2 > sim1:
                sim1 = sim2
        SIM = sim1
    elif len(blog2_p) == 1:
        sim1 = 0.0
        allSen1_p = []
        role_sen1 = []
        for p in range(len(blog1_p)):
            x = parseSen(blog1_p[p])
            y = roleBlog(blog1_p[p])
            allSen1_p.append(x)
            role_sen1.append(y)
        allSen2_p = []
        role_sen2 = []
        for p in range(len(blog2_p)):
            x = parseSen(blog2_p[p])
            y = roleBlog(blog2_p[p])
            allSen2_p.append(x)
            role_sen2.append(y)
        for n in range(len(blog1_p)):
            count_1 = cal_count(allSen1_p, role_sen1[n], allSen1_p[n])
            sim2 = cal_sen_Similarity(role_sen1[n], allSen1_p[n], count_1, role_sen2[0], allSen2_p[0], cal_count(allSen2_p, role_sen2[0], allSen2_p[0]))
            if sim2 > sim1:
                sim1 = sim2
        SIM = sim1
    else:
        sim_col = []
        sum = 0.0
        count_2 = []
        allSen1_p = []
        role_sen1 = []
        for p in range(len(blog1_p)):
            x = parseSen(blog1_p[p])
            y = roleBlog(blog1_p[p])
            allSen1_p.append(x)
            role_sen1.append(y)
        allSen2_p = []
        role_sen2 = []
        for p in range(len(blog2_p)):
            x = parseSen(blog2_p[p])
            y = roleBlog(blog2_p[p])
            allSen2_p.append(x)
            role_sen2.append(y)
        for m in range(len(blog2_p)):
            count_2.append(cal_count(allSen2_p, role_sen2[m], allSen2_p[m]))
        for n in range(len(blog1_p)):
            sim1 = 0.0
            count_1 = cal_count(allSen1_p, role_sen1[n], allSen1_p[n])
            for m in range(len(blog2_p)):
                print(blog1_p[n] + '|' + blog2_p[m])
                sim2 = cal_sen_Similarity(role_sen1[n], allSen1_p[n], count_1, role_sen2[m], allSen2_p[m], count_2[m])
                print(sim2)
                if sim2 > sim1:
                    sim1 = sim2
            sim_col.append(sim1)
        for n in range(len(sim_col)):
            sum += sim_col[n]
        SIM = sum / len(blog1_p)
    return SIM


def time_diff(blog1, blog2, time1, time2):
    blog1Date_s = blog1[0]
    blog1Date_d = datetime.datetime.strptime(blog1Date_s, '%a %b %d %H:%M:%S %z %Y')
    blog1Date_d.strftime('%Y-%m-%d %H:%M:%S')
    blog2Date_s = blog2[0]
    blog2Date_d = datetime.datetime.strptime(blog2Date_s, '%a %b %d %H:%M:%S %z %Y')
    blog2Date_d.strftime('%Y-%m-%d %H:%M:%S')
    diff1 = blog1Date_d - blog2Date_d
    diff1_sec = diff1.days * 86400 + diff1.seconds

    time1Date_d = datetime.datetime.strptime(time1, '%a %b %d %H:%M:%S %z %Y')
    time1Date_d.strftime('%Y-%m-%d %H:%M:%S')
    time2Date_d = datetime.datetime.strptime(time2, '%a %b %d %H:%M:%S %z %Y')
    time2Date_d.strftime('%Y-%m-%d %H:%M:%S')
    diff2 = time1Date_d - time2Date_d
    diff2_sec = abs(diff2.days) * 86400 + diff2.seconds

    return 1 - ((abs(diff1_sec)) / abs(diff2_sec))


def write_result(result, value, route):
    with open('result.txt', 'w') as f:
        f.write('---------------------------------------------------------------------------------\n')
        print('---------------------------------------------------------------------------------')
        for n in range(len(result)):
            if n == 12:
                break
            print(result[n] + '    similarity value: ' + value[n])
            f.write(result[n] + '    similarity value: ' + value[n] + '\n')
            print('---------------------------------------------------------------------------------')
            f.write('---------------------------------------------------------------------------------\n')
        f.write('\n| ' + route[0] + ' |')
        for m in range(len(route)):
            if m > 0:
                f.write(' ---> ')
                f.write('| ' + route[m] + ' |')


# read csv file
fileName = input("Input the name of CSV file: ")
df = pd.read_csv(fileName + '.csv', encoding='gb18030')
df.columns = ["发布时间", "微博id", "用户id", "用户名", "微博地址", "转发数", "评论数", "点赞数", "正文", "实验正文"]
microBlogs = df[["发布时间", "微博id", "用户id", "用户名", "微博地址", "转发数", "评论数", "点赞数", "正文", "实验正文"]]
microBlogs = np.array(microBlogs)
print(microBlogs)

# get target microblog
address = input("Input the id of the target microblog: ")
for n in range(len(microBlogs)):
    if microBlogs[n][1] == int(address):
        targetBlog = []
        for m in range(len(microBlogs[0])):
            targetBlog.append(microBlogs[n][m])
        p = n
        break

# delete other blogs
targetDate_s = targetBlog[0]
targetDate_d = datetime.datetime.strptime(targetDate_s, '%a %b %d %H:%M:%S %z %Y')
targetDate_d.strftime('%Y-%m-%d %H:%M:%S')
length = len(microBlogs)
for n in range(length):
    compareDate_s = microBlogs[n][0]
    compareDate_d = datetime.datetime.strptime(compareDate_s, '%a %b %d %H:%M:%S %z %Y')
    compareDate_d.strftime('%Y-%m-%d %H:%M:%S')
    diff = targetDate_d - compareDate_d
    diff_sec = diff.days * 86400 + diff.seconds
    if diff_sec < 0:
        for m in range(n, length - 1):
            microBlogs[m] = microBlogs[m + 1]
        if n < p:
            p = p - 1
        n = n - 1
        length = length - 1

# body
route = []
route.append(targetBlog[3])
result = []
value = []
time_exp = targetBlog[0]
time_min = microBlogs[len(microBlogs)-1][0]
while p < (length - 1):
    for n in range(p, len(microBlogs) - 1):
        microBlogs[n] = microBlogs[n + 1]
    Perc = 0.0
    num = -1
    userBlog = []
    simBlog = []
    for n in range(len(microBlogs)):
        if n == 12:
            break
        print(n)
        userBlog.append(microBlogs[n][3])
        SIM = cal_blog_Similarity(targetBlog[9], microBlogs[n][9])
        time_dif = time_diff(targetBlog, microBlogs[n], time_exp, time_min)
        perc = 0.5 * SIM + 0.5 * time_dif
        simBlog.append(str(perc))
        if perc > Perc:
            Perc = perc
            num = n
            targetBlog = []
            for m in range(len(microBlogs[0])):
                targetBlog.append(microBlogs[n][m])
    p = n
    length = len(microBlogs)
    print('Perc: ' + str(Perc))
    route.append(targetBlog[3])
    write_result(userBlog, simBlog, route)
    break
    if Perc < 0.69:
        break
    result.append(targetBlog)
    value.append(Perc)
# write_result(result, value)

