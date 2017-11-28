from HIN import EntityInfo
import pickle
import queue
import math


# simType = 1 -> cosin similarity
# simType = 2 -> Euclidean similarity
def getSignSim(hin, sEntity, tEntity, metaPath, simType=2):
	'''
	calculate signed similarity of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path: meta-path
	:param simType: 1 -> cosin similarity; 2 -> Euclidean similarity
	:return: signed similarity between eEntity and tEntity using simType
	'''

	# meta-path factorization
	def getFactorizedPath(metaPath):
		splittedMetaPaths = []
		metaPathLen = len(metaPath)
		k = 1
		k_ = 0
		while k < metaPathLen:
			for i in range(k_, k):
				if metaPath[i] == metaPath[k]:
					if i != k_:
						splittedMetaPaths.append({'redundant':True, 'metaPath':metaPath[k_:i+1]})
					splittedMetaPaths.append({'redundant':False, 'metaPath':metaPath[i:k+1]})
					k_ = k
					break
			k += 1
		if k_ + 1 != k:
			splittedMetaPaths.append({'redundant':True, 'metaPath':metaPath[k_:]})
		return splittedMetaPaths

	# Select the weighted relation's weight
	# weightFilter = None -> no weight filter
	# weightFilter = 0 -> select negative weight
	# weightFilter = 1 -> select positive weight
	def selectRelationWeights(hin, relationIndexes, weightFilter=None):
		weightFilterList = [lambda t: t < 0, lambda t: t > 0]
		tmpRelationWeights = []
		for relationIndex in relationIndexes:
			tmpWeight = hin['Relations'][relationIndex].weight
			if tmpWeight != None:
				if weightFilter != None and not weightFilterList[weightFilter](tmpWeight):
					continue
				tmpRelationWeights.append(tmpWeight)
		return tmpRelationWeights

	# Similarity on atomic relation
	def getAtomicSim(hin, sEntityInfo, tEntityInfo, metaPath, simType):

		signSimDict = dict()
		metaPathLen = len(metaPath)
		secondEntityType = metaPath[1]

		if tEntityInfo != None:
			tEntityId = tEntityInfo.entity.entityId
			signSimDict[tEntityId] = 0

			if secondEntityType not in sEntityInfo.outRelations:
				return signSimDict
			if secondEntityType not in tEntityInfo.outRelations:
				return signSimDict


			sEntityFeature = sEntityInfo.outRelations[secondEntityType]
			tEntityFeature = tEntityInfo.outRelations[secondEntityType]

			sEntityFeatureIdSet = set(sEntityFeature['relIndexDict'].keys())
			tEntityFeatureIdSet = set(tEntityFeature['relIndexDict'].keys())
			intersectionIdSet = sEntityFeatureIdSet.intersection(tEntityFeatureIdSet)

			tmpResult = 0
			for entityId in intersectionIdSet:
				sRelationIndexes = sEntityFeature['relIndexDict'][entityId]
				tRelationIndexes = tEntityFeature['relIndexDict'][entityId]

				# select those weighted relation
				sRelationWeights = selectRelationWeights(hin, sRelationIndexes)
				tRelationWeights = selectRelationWeights(hin, tRelationIndexes)

				if sRelationWeights != [] and tRelationWeights != []:
					if simType == 1:
						tmpResult += (sum(sRelationWeights)*sum(tRelationWeights))/(len(sRelationWeights)*len(tRelationWeights))
					else:
						tmpResult += (sum(sRelationWeights)/len(sRelationWeights) - sum(tRelationWeights)/len(tRelationWeights))**2

			if simType == 1:
				signSimDict[tEntityId] = tmpResult/(sEntityFeature['relsNum']*tEntityFeature['relsNum'])
			else:
				signSimDict[tEntityId] = 1/(1 + math.sqrt(tmpResult))

		else:
			if secondEntityType not in sEntityInfo.outRelations:
				return signSimDict

			relIndexDict = sEntityInfo.outRelations[secondEntityType]['relIndexDict']
			if metaPathLen == 2:
				for tEntityId in relIndexDict:
					tEntityInfo = hin['Entities'][hin['EntityTypes'][secondEntityType][tEntityId]]
					signSimDict.update(getAtomicSim(hin, sEntityInfo, tEntityInfo, metaPath, simType))
			else:
				sEntityType = metaPath[0]
				candidateTEntityIdList = []
				for secondEntityId in relIndexDict:
					secondEntityInfo = hin['Entities'][hin['EntityTypes'][secondEntityType][secondEntityId]]
					tmpRelIndexDict = secondEntityInfo.outRelations[sEntityType]['relIndexDict']
					for tEntityId in tmpRelIndexDict:
						tEntityInfo = hin['Entities'][hin['EntityTypes'][sEntityType][tEntityId]]
						tmpSignSimDict = getAtomicSim(hin, sEntityInfo, tEntityInfo, metaPath, simType)
						if tEntityId not in signSimDict:
							signSimDict.update(tmpSignSimDict)
						else:
							signSimDict[tEntityId] += tmpSignSimDict[tEntityId]

		return signSimDict

	# Similarity on redundant relation
	def getRedundantSim(hin, sEntityInfo, tEntityInfo, metaPath):

		def getSignSimFromCertainTEntity(hin, sEntityInfo, tEntityInfo):

			tEntityId = tEntityInfo.entity.entityId
			tEntityType = tEntityInfo.entity.entityType

			if tEntityType not in sEntityInfo.outRelations:
				return 0

			relIndexDict = sEntityInfo.outRelations[tEntityType]['relIndexDict']
			if tEntityId not in relIndexDict:
				return 0

			relationIndexes = relIndexDict[tEntityId]

			sEntityType = sEntityInfo.entity.entityType
			tEntityType = tEntityInfo.entity.entityType

			tmpRelationWeights = selectRelationWeights(hin, set(relationIndexes))

			if tmpRelationWeights == []:
				return 1/(sEntityInfo.outRelations[tEntityType]['relsNum'] * tEntityInfo.inRelations[sEntityType]['relsNum'])
			else:
				tmpWeight = sum(tmpRelationWeights)/len(tmpRelationWeights)
				if tmpWeight != 0:
					sCandidateRelIndexes = []
					for _, relationIndexes in sEntityInfo.outRelations[tEntityType]['relIndexDict'].items():
						sCandidateRelIndexes += relationIndexes
					tCandidateRelIndexes = []
					for _, relationIndexes in tEntityInfo.inRelations[sEntityType]['relIndexDict'].items():
						tCandidateRelIndexes += relationIndexes

					sHomoWeights = [0]
					tHomoWeights = [0]
					if tmpWeight < 0:
						sHomoWeights = selectRelationWeights(hin, sCandidateRelIndexes, 0)
						tHomoWeights = selectRelationWeights(hin, tCandidateRelIndexes, 0)
					else:
						sHomoWeights = selectRelationWeights(hin, sCandidateRelIndexes, 1)
						tHomoWeights = selectRelationWeights(hin, tCandidateRelIndexes, 1)
					return tmpWeight/(sum(sHomoWeights)*sum(tHomoWeights))
				else:
					return 0

		metaPathLen = len(metaPath)
		sEntityType = metaPath[0]
		signSimDict = dict()

		if metaPathLen == 2:
			tEntityType = metaPath[1]
			if tEntityInfo != None:
				tEntityId = tEntityInfo.entity.entityId
				signSimDict[tEntityId] = getSignSimFromCertainTEntity(hin, sEntityInfo, tEntityInfo)
			else:
				relationInfo = sEntityInfo.outRelations[tEntityType]
				for entityId  in relationInfo['relIndexDict']:
					tmpTEntityInfo = hin['Entities'][hin['EntityTypes'][tEntityType][entityId]]
					signSimDict[entityId] = getSignSimFromCertainTEntity(hin, sEntityInfo, tmpTEntityInfo)
		else:
			nextEntityType = metaPath[1]
			relationInfo = sEntityInfo.outRelations[nextEntityType]
			for nextEntityId in relationInfo['relIndexDict']:
				nextEntityInfo = hin['Entities'][hin['EntityTypes'][nextEntityType][nextEntityId]]
				nextSignSimDict = getRedundantSim(hin, sEntityInfo, nextEntityInfo, metaPath[0:2])
				nextSignSim = nextSignSimDict[nextEntityId]

				# update the final sign sim dict
				tmpFinalSignSimDict = getRedundantSim(hin, nextEntityInfo, tEntityInfo, metaPath[1:])
				for tmpEntityId in tmpFinalSignSimDict:
					if tmpEntityId in signSimDict:
						signSimDict[tmpEntityId] += tmpFinalSignSimDict[tmpEntityId]*nextSignSim
					else:
						signSimDict[tmpEntityId] = tmpFinalSignSimDict[tmpEntityId]*nextSignSim

		return signSimDict

	# the main recursive function to get sign similarity
	def getSignSimMain(hin, sEntityInfo, tEntityInfo, splittedMetaPaths, simType):
		splittedMetaPathsLen = len(splittedMetaPaths)
		if splittedMetaPathsLen == 1:
			if splittedMetaPaths[0]['redundant']:
				return getRedundantSim(hin, sEntityInfo, tEntityInfo, splittedMetaPaths[0]['metaPath'])
			else:
				return getAtomicSim(hin, sEntityInfo, tEntityInfo, splittedMetaPaths[0]['metaPath'], simType)
		else:
			firstSignSimDict = dict()
			currSignSimDict = dict()
			if splittedMetaPaths[0]['redundant']:
				firstSignSimDict = getRedundantSim(hin, sEntityInfo, None, splittedMetaPaths[0]['metaPath'])
			else:
				firstSignSimDict = getAtomicSim(hin, sEntityInfo, None, splittedMetaPaths[0]['metaPath'], simType)

			nextEntityType = splittedMetaPaths[0]['metaPath'][-1]
			for entityId in firstSignSimDict:
				entityInfo = hin['Entities'][hin['EntityTypes'][nextEntityType][entityId]]
				nextSignSimDict = getSignSimMain(hin, entityInfo, tEntityInfo, splittedMetaPaths[1:], simType)

				# update the sign sim dict
				for tEntityId in nextSignSimDict:
					if tEntityId in currSignSimDict:
						currSignSimDict[tEntityId] += nextSignSimDict[tEntityId]*firstSignSimDict[entityId]
					else:
						currSignSimDict[tEntityId] = nextSignSimDict[tEntityId]*firstSignSimDict[entityId]

			return currSignSimDict

	splittedMetaPaths = getFactorizedPath(metaPath)

	sEntityType = sEntity.entityType
	sEntityId = sEntity.entityId
	sEntityInfo = hin['Entities'][hin['EntityTypes'][sEntityType][sEntityId]]

	tEntityType = tEntity.entityType
	tEntityId = tEntity.entityId
	tEntityInfo = hin['Entities'][hin['EntityTypes'][tEntityType][tEntityId]]

	signSimDict = getSignSimMain(hin, sEntityInfo, tEntityInfo, splittedMetaPaths, simType)
	return signSimDict[tEntityId]


def getWsRel(hin, sEntity, tEntity, metaPath):
	'''
	calculate weighted signed relation of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path: meta-path
	:return: weighted signed relation between eEntity and tEntity
	'''
	# sigmoid function
	def sigmoid(weight):
		if weight == None:
			return 0.5
		else:
			return 1/(1 + math.exp(-weight))

	# initialize
	sEntityInfo = hin['Entities'][hin['EntityTypes'][sEntity.entityType][sEntity.entityId]]
	hinRelationList = hin['Relations']
	metaPathLen = len(metaPath)
	wsRelResult = 0

	nextEntityType = metaPath[1]
	if nextEntityType not in sEntityInfo.outRelations:
		return 0

	if metaPathLen == 2:
		if tEntity.entityId not in sEntityInfo.outRelations[metaPath[1]]['relIndexDict']:
			return 0
		else:
			relationInfo = sEntityInfo.outRelations[metaPath[1]]
			relationsNum = relationInfo['relsNum']
			relationIndexList = relationInfo['relIndexDict'][tEntity.entityId]
			for relationIndex in relationIndexList:
				currRelation = hinRelationList[relationIndex]
				wsRelResult += sigmoid(currRelation.weight)/relationsNum

			return wsRelResult


	relationInfo = sEntityInfo.outRelations[nextEntityType]
	# relationsNum -> the number of relations which have the same type and all start from the source entity
	relationsNum = relationInfo['relsNum']


	for nextEntityId in relationInfo['relIndexDict']:
		relationIndexList = relationInfo['relIndexDict'][nextEntityId]
		for relationIndex in relationIndexList:
			currRelation = hinRelationList[relationIndex]
			currEntity = currRelation.endEntity
			wsRelResult += sigmoid(currRelation.weight)*getWsRel(hin, currEntity, tEntity, metaPath[1:])

	wsRelResult /= relationsNum

	# Do something here

	return wsRelResult


def neighbor_distribution(HIN, sEntity, meta_path, flag = 0):
	'''
	calculate neighbor distribution of entity start based on meth_path
	:param flag: whether require middle node
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param meta_path:
	:return: neighbor distribution of start
	'''

	distri = {}
	q = queue.Queue()
	q.put((sEntity, 0, 0))
	while not q.empty():
		cur_entity, pos, pre_entity = q.get()
		if pos == len(meta_path) - 1:
			entity_key = 0
			if flag == 0:
				entity_key = cur_entity.entity.entityId
			elif flag == 1:
				entity_key = ' '.join([str(pre_entity.entity.entityId), str(cur_entity.entity.entityId)])
			elif flag == -1:
				entity_key = ' '.join([str(cur_entity.entity.entityId), str(pre_entity.entity.entityId)])
			if entity_key not in distri:
				distri[entity_key] = 1
			else:
				distri[entity_key] += 1
			continue
		if meta_path[pos + 1] in cur_entity.outRelations:
			for key in cur_entity.outRelations[meta_path[pos + 1]]['relIndexDict']:
				for relation in cur_entity.outRelations[meta_path[pos + 1]]['relIndexDict'][key]:
					entity = HIN['Relations'][relation].endEntity
					entityInfoIdx = HIN['EntityTypes'][entity.entityType][entity.entityId]
					entityInfo = HIN['Entities'][entityInfoIdx]
					q.put((entityInfo, pos + 1, cur_entity))

	return distri


def getDistantSim(HIN, sEntity, tEntity, meta_path):
	'''
	calculate distant similarity of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path: meta-path needs to be symmetric
	:return: distant similarity between eEntity and tEntity using cosine similarity
	'''
	sEntity = HIN['Entities'][HIN['EntityTypes'][sEntity.entityType][sEntity.entityId]]
	tEntity = HIN['Entities'][HIN['EntityTypes'][tEntity.entityType][tEntity.entityId]]
	distri_start = neighbor_distribution(HIN, sEntity, meta_path)
	distri_end = neighbor_distribution(HIN, tEntity, meta_path)
	numerator = 0
	for key in distri_start:
		if key in distri_end:
			numerator += distri_start[key] * distri_end[key]
	denominator1 = 0
	denominator2 = 0
	for key in distri_start:
		denominator1 += distri_start[key] ** 2
	for key in distri_end:
		denominator2 += distri_end[key] ** 2
	denominator1 = math.sqrt(denominator1)
	denominator2 = math.sqrt(denominator2)
	return numerator / denominator1 / denominator2


def getHeteSim(HIN, sEntity, tEntity, meta_path):
	'''
	calculate HeteSim of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path: mata-path used in this similarity calculation
	:return: HeteSim value between eEntity and tEntity based on mata-path
	'''
	sEntity = HIN['Entities'][HIN['EntityTypes'][sEntity.entityType][sEntity.entityId]]
	tEntity = HIN['Entities'][HIN['EntityTypes'][tEntity.entityType][tEntity.entityId]]
	flag = 0
	if len(meta_path) % 2 == 0:
		flag = 1

	mid = len(meta_path) // 2 + 1

	distri_start = neighbor_distribution(HIN, sEntity, meta_path[:mid], flag)
	distri_end = neighbor_distribution(HIN, tEntity, list(reversed(meta_path))[:mid], -flag)

	numerator = 0
	for key in distri_start:
		if key in distri_end:
			numerator += distri_start[key] * distri_end[key]
	denominator1 = 0
	denominator2 = 0
	for key in distri_start:
		denominator1 += distri_start[key] ** 2
	for key in distri_end:
		denominator2 += distri_end[key] ** 2
	denominator1 = math.sqrt(denominator1)
	denominator2 = math.sqrt(denominator2)
	denominator = denominator2 * denominator1
	if denominator == 0:
		return 0
	else:
		return numerator / denominator

def getPathSim(HIN, sEntity, tEntity, meta_path):
	'''
	calculate PathSim of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path:  mata-path used in this similarity calculation
	:return: PathSim value between eEntity and tEntity based on mata-path
	'''
	sEntity = HIN['Entities'][HIN['EntityTypes'][sEntity.entityType][sEntity.entityId]]
	tEntity = HIN['Entities'][HIN['EntityTypes'][tEntity.entityType][tEntity.entityId]]
	distri_start = neighbor_distribution(HIN, sEntity, meta_path)
	distri_end = neighbor_distribution(HIN, tEntity, list(reversed(meta_path)))
	tEntity_key = tEntity.entity.entityId
	numerator = 0
	if tEntity_key in distri_start:
		numerator = 2 * distri_start[tEntity_key]
	denominator1 = 0
	denominator2 = 0
	for key in distri_start:
		denominator1 += distri_start[key]
	for key in distri_end:
		denominator2 += distri_end[key]
	denominator = denominator2 + denominator1
	if denominator == 0:
		return 0
	else:
		return numerator / denominator

def getJoinSim(HIN, sEntity, tEntity, meta_path):
	'''
	calculate JoinSim of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path:  mata-path used in this similarity calculation
	:return: JoinSim value between eEntity and tEntity based on mata-path
	'''
	sEntity = HIN['Entities'][HIN['EntityTypes'][sEntity.entityType][sEntity.entityId]]
	tEntity = HIN['Entities'][HIN['EntityTypes'][tEntity.entityType][tEntity.entityId]]
	distri_start = neighbor_distribution(HIN, sEntity, meta_path)
	distri_end = neighbor_distribution(HIN, tEntity, list(reversed(meta_path)))
	tEntity_key = tEntity.entity.entityId
	numerator = distri_start[tEntity_key]
	denominator1 = 0
	denominator2 = 0
	for key in distri_start:
		denominator1 += distri_start[key]
	for key in distri_end:
		denominator2 += distri_end[key]
	return numerator / math.sqrt(denominator1 * denominator2)

if __name__ == "__main__":
	f = open('HIN.pkl','rb')
	HIN = pickle.load(f)
