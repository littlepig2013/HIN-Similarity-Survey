class Entity(object):

	def __init__(self, entityId, entityType):
		self.entityId = entityId
		self.entityType = entityType

	def __eq__(self, other):
		return self.entityId == other.entityId and self.entityType == other.entityType

	def __repr__(self):
		return "Entity: entityType->" + str(self.entityType) + ", entityId->"+str(self.entityId)

	def __str__(self): 
		return self.__repr__()

