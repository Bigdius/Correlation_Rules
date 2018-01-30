# -*- coding: utf-8 -*-
"""
@author: Cheng
"""


class Apriorange():
    """
    根据Aprior算法，计算出关联规则：
    Step1：计算出满足最小支持度的各类集合，以及相应的support
    Step2：根据计算出来的集合，组合出可能的规则，并计算相应的confidence
    输入：pattern组合,ex:[[2,3,4],[3,4]]
    输出：  aprior：regular pattern  + supportdata
           generaterules ：print规则 + 规则及置信度
    """

    def __init__(self, dataset, minisupp, minconf):
        self.dataset = dataset
        self.minisupp = minisupp
        self.minconf = minconf

    def createC1(self, dataa):
        """
        :param dataa:
        :return: 生成dataset内所有不重复元素的frozenset
        """
        c1 = []
        for transaction in dataa:
            for item in transaction:
                if not [item] in c1:
                    c1.append([item])
        c1.sort()
        return list(map(frozenset, c1))

    def scanD(self, D, ck, supp):
        """
        看这些ck在D中的频率
        :param D: 原始数据,变成由集合构成的list
        :param ck: 候选探查的项集，上一步骤/迭代构成的 frozenset集合
        :param supp:
        :return: 入选项集及所有集support
        """
        sscnt = {}
        for tid in D:
            for can in ck:
                if can.issubset(tid):
                    if not can in sscnt.keys():
                        sscnt[can] = 1
                    else:
                        sscnt[can] += 1
        numitem = float(len(D))
        retlist = []
        supportdata = {}
        for key in sscnt.keys():
            support = sscnt[key] / numitem
            if support > supp:
                retlist.insert(0, key)
            supportdata[key] = support
        return retlist, supportdata

    def apriorGen(self, lk, k):
        """
        生成组合集，合并前k-1项相同的forzenset
        :param lk: lk为上次返回的forzenset集合
        :param k:
        :return: 新生成的forzenset的组合
        """
        retlist = []
        lenlk = len(lk)
        for i in range(lenlk):
            for j in range(i + 1, lenlk):
                l1 = list(lk[i])[:k - 2]
                l2 = list(lk[j])[:k - 2]
                l1.sort()
                l2.sort()
                if l1 == l2:
                    retlist.append(lk[i] | lk[j])
        return retlist

    # 计算频繁项集以及支持度的主函数
    def aprior(self):
        c1 = self.createC1(self.dataset)  # 每个不重复元素一个frozenset
        D = list(map(set, self.dataset))  # 源数据变成set组成的列表
        L1, supportdata = self.scanD(D, c1, self.minisupp)  # 第一部分，满足最小支持度的单个元素的结果
        L = [L1]
        k = 2
        while len(L[k - 2]) > 0:
            ck = self.apriorGen(L[k - 2], k)  # 前K-1项相同的被合并起来，生成由k个元素构成的frozenset
            LK, supK = self.scanD(D, ck, self.minisupp)  # 新合并的frozenset的频率统计
            supportdata.update(supK)
            L.append(LK)
            k += 1
        return L, supportdata

    # 计算规则可信度的函数
    def calcConf(self, freqset, H, supportdata, brl, minconff):
        """
        :param freqset: 上面计算出来的满足条件的forzenset，ex：frozenset({4, 5})
        :param H: 将freqset中的元素分解出来，构成的单独的forzenset，类似于createC1，ex：[frozenset({4}), frozenset({5})]
        :param supportdata: 上面函数计算出来的supportdata
        :param brl:  空列表，存储返回结果
        :param minconff: 最小置信度
        :return:   打印出满足条件的关联规则，返回入选规则的forzenset，供下面循环使用
        """
        pruedh = []
        for conseq in H:
            conf = supportdata[freqset] / supportdata[freqset - conseq]
            if conf >= minconff:
                print(freqset - conseq, '-->', conseq, 'conf:', conf)
                brl.append((freqset - conseq, conseq, conf))
                pruedh.append(conseq)
        return pruedh

    # 针对超过2个元素的frozenset需要考虑高阶的规则，所以需要进行合并，不能仅仅用上面的函数进行分解
    def rulesfromconseq(self, freqset, H, supportdata, br1, minconff):
        """
        :param freqset: 计算出来的满足条件的forzenset，ex：frozenset({4, 5, 6})
        :param H: 首次循环时只会有单个元素frozenset({4})，随后会出现多重frozenset({4,5})
        :param supportdata: 上面函数计算出来的supportdata
        :param br1: 空列表，存储返回结果
        :param minconff: 最小置信度
        :return:
        """
        m = len(H[0])
        if len(freqset) > (m + 1):
            hmp1 = self.apriorGen(H, m + 1)  # 生成m+1长度的forzenset
            hmp1 = self.calcConf(freqset, hmp1, supportdata, br1, minconff)
            if len(hmp1) > 1:  # 仍然有满足条件的关联规则，那么继续扩大屁股部分
                self.rulesfromconseq(freqset, hmp1, supportdata, br1, minconff)

    # 最终大函数
    def generaterules(self, L, supportdata):
        gigrule = []
        gg = self.minconf
        for i in range(1, len(L)):
            for freqset in L[i]:
                H1 = [frozenset([item]) for item in freqset]
                if i == 1:  # 这里只有两个元素，所以直接 a-b 类型
                    self.calcConf(freqset, H1, supportdata, gigrule, gg)
                else:
                    self.rulesfromconseq(freqset, H1, supportdata, gigrule, gg)
        return gigrule
