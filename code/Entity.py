class Entity(object):

	def __init__(self, entityId, entityType):
		self.entityId = entityId
		self.entityType = entityType

	def __eq__(self, other):
		return self.entityId == other.entityId and self.entityType == other.entityType


