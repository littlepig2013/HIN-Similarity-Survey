from HIN import EntityInfo
import pickle
import queue
import math


def getWsRel(hin, sEntity, tEntity, metaPath):
	# sigmoid function
	def sigmoid(weight):
		if weight == None:
			return 0.5
		else:
			return 1/(1 + math.exp(-weight))

	# initialize
	sEntityInfo = hin['EntityTypes'][hin[sEntity.entityType][sEntity.entityId]]
	metaPathLen = len(metaPath)
	wsRelResult = 0

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
				entity_key = ' '.join([pre_entity.entity.entityId, cur_entity.entity.entityId])
			elif flag == -1:
				entity_key = ' '.join([cur_entity.entity.entityId, pre_entity.entity.entityId])
			if entity_key not in distri:
				distri[entity_key] = 1
			else:
				distri[entity_key] += 1
			continue
		for key in cur_entity.outRelations[meta_path[pos + 1]].relIndexDict:
			for relation in cur_entity.outRelations[meta_path[pos + 1]].relIndexDict[key]:
				entity = HIN['Relations'][relation].endEntity
				entityInfoIdx = HIN['EntityTypes'][entity.entityType][entity.entityId]
				entityInfo = Hin['Entities'][entityInfoIdx]
				q.put(entityInfo, pos + 1, cur_entity)

	return distri


def distant_similarity(HIN, sEntity, tEntity, meta_path):
	'''
	calculate distant similarity of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path: meta-path needs to be symmetric
	:return: distant similarity between eEntity and tEntity using cosine similarity
	'''

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

def hete_sim(HIN, sEntity, tEntity, meta_path):
	'''
	calculate HeteSim of two entities, sEntity and tEntity
	:param HIN: the heterogeneous information network
	:param sEntity: start entity
	:param tEntity: end entity
	:param meta_path: mata-path used in this similarity calculation
	:return: HeteSim value between eEntity and tEntity based on mata-path
	'''
	flag = 0
	if len(meta_path) % 2 == 0:
		flag = 1

	mid = len(meta_path) / 2 + 1

	distri_start = neighbor_distribution(HIN, sEntity, meta_path[:mid], flag)
	distri_end = neighbor_distribution(HIN, tEntity, reversed(meta_path)[:mid], -flag)

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

if __name__ == "__main__":
	f = open('HIN.pkl','rb')
	HIN = pickle.load(f)
