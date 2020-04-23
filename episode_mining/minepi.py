#coding: utf-8
from numpy import *
from itertools import combinations, permutations

class MINEPI(object):
	def __init__(self, sequence, episode_type='serial'):
		self.sequence = sequence
		if episode_type not in ('serial', 'parallel'):
			raise Exception(
				'`episode_type` must be `serial` or `parallel`'
			)
		self.episode_type = episode_type
		# set up serial/parallel environment
		if episode_type == 'parallel':
			self.createCandidates = self.createCandidates_parallel
		elif episode_type == 'serial':
			self.createCandidates = self.createCandidates_serial


	def createC1(self):
		C1 = {}
		for event in self.sequence:
			mo = tuple((event[0], event[0] + self.step)) # calc minimal occurrence (mo)
			if event[1] in C1: # if event exists in C1
				if mo not in C1[event[1]]: # if mo not exists in event's set of mo
					C1[event[1]].add(mo)
			else: C1[event[1]] = set((mo,))
		return C1



	def createLargeEpisodeSet(self, Ck):
		Lk = Ck.copy()
		for episode in Ck:
			if len(Ck[episode]) < self.minFrequent: # if number of mo < min_fr
				del Lk[episode]
		return Lk


	def checkSubsetFrequency(self, candidate, Lk, k):
		if k > 1:	
			subsets = list(combinations(candidate, k))
		else:
			return True
		for elem in subsets:
			if not elem in Lk: #elem is tuple
				return False
		return True


	def createCandidates_serial(self, Lk, L1, k):
		# create candidates list
		candidatesK = [] #candidates list
		generatedCans = [] 
		lkKeys = sorted(set([item for t in Lk for item in t])) # get all episodes and sort / Lk:get all keys
		generatedCans = list(permutations(lkKeys, k))
		for can in generatedCans:
			if self.checkSubsetFrequency(can, Lk, k-1): #if all subsets of can is frequent / Lk:get all keys
				candidatesK.append(can)
		# create minimal occurrence of candidates
		if len(candidatesK) == 0: # if candidates list is null
			return dict()
		else:
			Ck = {}
			if k == 2: #candidate 2
				for can in candidatesK: # can is tuple
					Ck[can] = set()
					for mok in Lk[can[0]]:
						for mo1 in L1[can[1]]:
							# mo1.ts >= mok.te and mo1.te - mok.ts <= max_width
							if mo1[0] >= mok[1] and mo1[1] - mok[0] <= self.max_width:
								Ck[can].add(tuple((mok[0], mo1[1])))
			else: #candidate > 2
				for can in candidatesK: # can is tuple
					Ck[can] = set()
					for mok in Lk[can[:-1]]:
						for mo1 in L1[can[-1]]:
							# mo1.ts >= mok.te and mo1.te - mok.ts <= max_width
							if mo1[0] >= mok[1] and mo1[1] - mok[0] <= self.max_width:
								Ck[can].add(tuple((mok[0], mo1[1])))
			# recheck minimal occurrence to remove superset of mo
			for episode, setOfMOs in Ck.items():
				rem = set()
				for mo1 in setOfMOs:
					for mo2 in setOfMOs.difference(mo1):
						# mo1[0] is mo1.ts, mo2[0] is mo2.ts, mo1[1] is mo1.te, mo2[1] is mo2.te
						if (mo1[0]==mo2[0] and mo1[1] < mo2[1]) or (mo1[0] > mo2[0] and mo1[1] == mo2[1]) or (mo1[0] > mo2[0] and mo1[1] < mo2[1]):
							rem.add(mo2)
				Ck[episode] = setOfMOs.difference(rem)
			return Ck


	def MinEpi(self, minFrequent, max_width, step):
		self.minFrequent = minFrequent
		self.max_width = max_width
		self.step = step
		C1 = self.createC1()
		L1 = self.createLargeEpisodeSet(C1)
		L = [L1]
		k = 2
		while (len(L[k-2]) > 0):
			Ck = self.createCandidates(L[k-2], k)
			Lk = self.createLargeEpisodeSet(Ck)
			L.append(Lk)
			k += 1
		#remove empty last itemset from L
		if L[-1] == {}:
			L.pop()
			
		return L