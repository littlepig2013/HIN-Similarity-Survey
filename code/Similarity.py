from HIN import EntityInfo
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

