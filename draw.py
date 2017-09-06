#!/usr/bin/env python3
# coding: utf-8

import os
import requests
from bs4 import BeautifulSoup as bs
import matplotlib
import matplotlib.pyplot as plt


# 填写一分一档表网页地址
# 2017广西理科
URL = 'http://gaokao.eol.cn/guang_xi/dongtai/201706/t20170623_1533059.shtml'
# 2011广西理科
# URL = 'http://edu.sina.com.cn/gaokao/2011-06-22/2029302820.shtml'

KEYWORD_FENSHU = ['总分', '分数', '分值']
KEYWORD_COUNTS = ['人数']
KEYWORD_EXCLUDE = ['排除', '累计', '累积']

if os.name == 'nt': # windows:
    zhfont = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\msyh.ttc')
elif os.name == 'posix': # linux:
    zhfont = matplotlib.font_manager.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

print('下载网页...')
r = requests.get(URL)

print('检测页面编码...')
r.encoding = 'GB2312' #r.apparent_encoding
soup = bs(r.text, 'lxml')

print('获取正确的列表...')
tables = soup.findAll('table')

right_table = None
col_fenshu = -1
col_counts = -1
for table in tables:
    found_fenshu = False
    found_counts = False
    for row in table.findAll("tr"):
        cols = row.findAll("td")
        cols_len = len(cols)
        if cols_len < 2:
            continue
        col_pointer = -1
        for col in cols:
            col_pointer += 1
            col_text = col.getText()
            if any(key in col_text for key in KEYWORD_FENSHU) and \
                not any(key in col_text for key in KEYWORD_COUNTS):
                found_fenshu = True
                col_fenshu = col_pointer
                continue
            if any(key in col_text for key in KEYWORD_COUNTS) and \
                not any(key in col_text for key in KEYWORD_FENSHU) and \
                not any(key in col_text for key in KEYWORD_EXCLUDE):
                found_counts = True
                col_counts = col_pointer
                continue
            if found_fenshu and found_counts:
                right_table = table
                break
        if found_fenshu and found_counts:
            break
    if found_fenshu and found_counts:
        break
else:
    print('未找到分数列表. 设定的关键词: ', KEYWORD_FENSHU, KEYWORD_COUNTS)
    exit(0)

print('处理列表...')
grades = {}
for row in right_table.findAll("tr"):
    cols = row.findAll("td")
    if len(cols) < 2:
        continue
    try:
        fenshu = int(cols[col_fenshu].text)
        counts = int(cols[col_counts].text)
    except:
        continue
    else:
        grades[fenshu] = counts
grades_keys = sorted(grades.keys())
grades_values = [grades[key] for key in grades_keys]
print('显示图像...')
# plt.bar(list(grades.keys()), grades.values(), color='g', width=1.0)
plt.plot(grades_keys, grades_values, '-o')
plt.title(soup.title.text, fontsize=20, fontproperties=zhfont)
plt.xlabel('分数', fontsize=16, fontproperties=zhfont)
plt.ylabel('人数', fontsize=16, fontproperties=zhfont)
plt.show()
