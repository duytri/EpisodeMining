#coding: utf-8
from numpy import *
from itertools import combinations, permutations
from . import WINEPIRule

class WINEPI(object):
	def __init__(self, sequence, episode_type='parallel'):
		self.sequence = sequence
		if episode_type not in ('serial', 'parallel'):
			raise Exception(
				'`episode_type` must be `serial` or `parallel`'
			)
		self.episode_type = episode_type
		# set up serial/parallel environment
		if episode_type == 'parallel':
			self.aprioriGen = self.aprioriGen_parallel
			self.scanWindows = self.scanWindows_parallel
		elif episode_type == 'serial':
			self.aprioriGen = self.aprioriGen_serial
			self.scanWindows = self.scanWindows_serial


	def slidingWindow(self):
	    windows = [list(self.sequence[0][1])]
	    t_end = self.sequence[0][0] + self.step
	    t_start = t_end - self.width
	    # number of windows = (Te - Ts + width - step)/step = (te_max - ts_min + width)/step
	    noWins = int((self.sequence[-1][0] - self.sequence[0][0] + self.width)/self.step)
	    for i in range(noWins-1): #because 1st window has been generated.
	        row = []
	        t_start += self.step; t_end += self.step
	        for event in self.sequence:
	            if t_start <= event[0] and event[0] < t_end:
	                row.append(event[1])
	        windows.append(row)
	    return windows


	def createC1(self, windows):
	    C1 = []
	    for transaction in windows:
	        for item in transaction:
	            if not [item] in C1:
	                C1.append([item])
	                
	    C1.sort()
	    return list(C1)


	def scanWindows_parallel(self, windows, Ck):
	    ssCnt = {}
	    for tid in windows:
	        for can in Ck:
	            if set(can).issubset(tid):
	            	#cannot use type 'set' in key of 'dictionary'
	                #so we use 'tuple' (Error: unhashable type)
	                if not tuple(can) in ssCnt: ssCnt[tuple(can)]=1
	                else: ssCnt[tuple(can)] += 1
	    numItems = float(len(windows))
	    retList = []
	    supportData = {}
	    for key in ssCnt:
	        support = ssCnt[key]/numItems
	        if support >= self.minFrequent:
	            retList.insert(0,key)
	        supportData[key] = support
	    return retList, supportData


	def isSubsetInOrderWithGap(self, sub, lst):
		ln, j = len(sub), 0
		for elem in lst:
			if elem == sub[j]:
				j += 1
			if j == ln:
				return True
		return False


	def scanWindows_serial(self, windows, Ck):
		ssCnt = {}
		for tid in windows:
			for can in Ck:
				if self.isSubsetInOrderWithGap(can, tid):
					if not tuple(can) in ssCnt: ssCnt[tuple(can)]=1
					else: ssCnt[tuple(can)] += 1
		numItems = float(len(windows))
		retList = []
		supportData = {}
		for key in ssCnt:
			support = ssCnt[key]/numItems
			if support >= self.minFrequent:
				retList.insert(0,key)
			supportData[key] = support
		return retList, supportData


	def checkSubsetFrequency(self, candidate, Lk, k):
	    if k > 1:
	        subsets = list(combinations(candidate, k))
	    else:
	        return True
	    for elem in subsets:
	        if not elem in Lk: #elem is tuple
	            return False
	    return True


	def aprioriGen_parallel(self, Lk, k): #creates Ck
	    resList = [] #result set
	    candidatesK = [] 
	    lk = sorted(set([item for t in Lk for item in t])) #get and sort elements from frozenset
	    candidatesK = list(combinations(lk, k))
	    for can in candidatesK:
	        if self.checkSubsetFrequency(can, Lk, k-1):
	            resList.append(can)
	    return resList


	def aprioriGen_serial(self, Lk, k): #creates Ck
		resList = [] #result set
		candidatesK = [] 
		lk = sorted(set([item for t in Lk for item in t])) #get and sort elements from frozenset
		candidatesK = list(permutations(lk, k))
		for can in candidatesK:
			if self.checkSubsetFrequency(can, Lk, k-1):
				resList.append(can)
		return resList


	def WinEpi(self, width, step=1, minFrequent):
		self.width = width
		self.step = step
		self.minFrequent = minFrequent
		windows = self.slidingWindow()
		C1 = self.createC1(windows)
		L1, supportData = self.scanWindows(windows, C1)
		L = [L1]
		k = 2
		while (len(L[k-2]) > 0):
			Ck = self.aprioriGen(L[k-2], k)
			Lk, supK = self.scanWindows(windows, Ck) #scan DB to get Lk
			supportData.update(supK)
			L.append(Lk)
			k += 1
		#remove empty last itemset from L
		if L[-1] == []:
			L.pop()
		return L, supportData


class WinEpiRules(object):
	def __init__(self, largeItemSet, supportData, width, minConfidence):
		self.largeItemSet = largeItemSet
		self.supportData = supportData
		self.width = width
		self.minConf = minConfidence


	def generateRules(self):  #supportData is a dict coming from scanWindows_parallel
		bigRuleList = []
		for i in range(1, len(self.largeItemSet)): #only get the sets with two or more items
			for item in self.largeItemSet[i]: #for each item in a level
				for j in range(1, i+1): # i+1 equal to length of an item
					lhsList = list(combinations(item, j))
					for lhs in lhsList: #lhs and item are both tuple
						conf = self.supportData[item]/self.supportData[lhs]
						if conf >= self.minConf:
							bigRuleList.append(WINEPIRule(list(lhs),list(item), self.width, self.supportData[item], conf))
		return bigRuleList


	def printRules(self, ruleList):
		for rule in ruleList:
			print(rule)