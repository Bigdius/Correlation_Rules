# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 16:35:33 2018

@author: Cheng
"""
# 使用关联规则进行疾病统计
import os
import pandas as pd
from Corre_rules.Aprior import Apriorange
orange = pd.read_csv('C:\\Users\\Cheng\\PycharmProjects\\GHB\\DataBase\\claims_final.csv')

# 只选取疾病来进行研究
all_dis = orange[['Member ID', 'Incurred  Date', 'Ailment_Description', 'Form ID']]
all_dis = all_dis.drop_duplicates()
all_dis = all_dis.sort_values(by=['Member ID', 'Incurred  Date'], ascending=True)
all_dis = all_dis.reset_index(drop=True)
# 需要去掉连续出现的疾病记录，我没有想到简单的方法，只能遍历：--运行半天，服
# all_diss = dict()
# all_diss[0] = list(all_dis.ix[0])
# for i in range(1, len(all_dis.index)):
#     if all_dis.ix[i, 0] != all_dis.ix[i - 1, 0]:
#         all_diss[i] = list(all_dis.ix[i])
#     elif all_dis.ix[i, 0] == all_dis.ix[i - 1, 0]:
#         if all_dis.ix[i, 2] == all_dis.ix[i - 1, 2]:
#             continue
#         else:
#             all_diss[i] = list(all_dis.ix[i])

# 后面又想到一个简便方法！就是简单的递归，将源数据拷贝，去掉第一个后再join起来源数据；看下一个是不是和上一个相等
a = all_dis['Member ID'][1:]
a[656341] = 'aaaa'
a = pd.DataFrame(a).reset_index(drop=True)
all_dis['new member id'] = a['Member ID']

b = all_dis['Ailment_Description'][1:]
b[656341] = 'bbbb'
b = pd.DataFrame(b).reset_index(drop=True)
all_dis['new Ailment_Description'] = b['Ailment_Description']

all_dis['check disease'] = all_dis['new Ailment_Description'] == all_dis['Ailment_Description']
all_dis['check member'] = all_dis['new member id'] == all_dis['Member ID']

all_dis['if take'] = all_dis['check member'] & all_dis['check disease']
chosen = list(all_dis[all_dis['if take'] == False].index)
chosen.append(-1)
chosen2 = [w + 1 for w in chosen]
selected = all_dis.ix[chosen2]
selected = selected[['Member ID', 'Incurred  Date', 'Ailment_Description', 'Form ID']]
selected = selected.sort_values(by=['Member ID', 'Incurred  Date'])
selected.reset_index(drop=True, inplace=True)
del selected['Form ID']

selected.to_csv('E:\\Python Projects\\GHB\\Corre_rules\\prepared_data.csv', index=False)

selected = pd.read_csv('E:\\Python Projects\\GHB\\Corre_rules\\prepared_data.csv')
selected[selected['Ailment_Description'].isnull()]
selected = selected.drop(411725)

# 又要用遍历了。
# 先将这部分疾病编码
dis_encode = selected[['Ailment_Description']].drop_duplicates().sort_values(by='Ailment_Description').reset_index(
    drop=True)
dis_encode = dis_encode.reset_index()
dis_encode.to_csv('E:\\Python Projects\\GHB\\Corre_rules\\disease_encode.csv', index=False)
selected = pd.merge(selected, dis_encode, how='left')

final_dict = {}
for w in list(selected['Member ID'].unique()):
    a = list(selected[selected['Member ID'] == w]['index'])
    final_dict[w] = a

# 保存字典数据


os.chdir('C:\\Users\\Cheng\\PycharmProjects\\GHB\\Corre_rules\\')
f = open("inputdata.txt", 'a')
f.write(str((final_dict.values())))
f.close()

f = open('C:\\Users\\Cheng\\PycharmProjects\\GHB\\Corre_rules\\dis_pattern.txt')
all_data = f.read()
all_data = eval(all_data)   # tricky!
f.close()

importdata = Apriorange(all_data, 0.5, 0.5)
L, suppData = importdata.aprior()
rules = importdata.generaterules(L, suppData)

'''    
frozenset([43]) --> frozenset([8]) conf: 0.545365168539
frozenset([127]) --> frozenset([8]) conf: 0.689165497896
frozenset([43]) --> frozenset([70]) conf: 0.549297752809
frozenset([70]) --> frozenset([8]) conf: 0.575564526303
frozenset([8]) --> frozenset([70]) conf: 0.541543026706
frozenset([40]) --> frozenset([58]) conf: 0.523846302375
frozenset([70]) --> frozenset([58]) conf: 0.512615112905
frozenset([40]) --> frozenset([8]) conf: 0.590654566519
frozenset([43]) --> frozenset([58]) conf: 0.533005617978
frozenset([40]) --> frozenset([70]) conf: 0.610252944584
'''
