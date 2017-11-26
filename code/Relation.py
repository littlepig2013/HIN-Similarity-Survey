class Relation(object):

	def __init__(self, startEntity, endEntity, weight=None):
		self.startEntity = startEntity
		self.endEntity = endEntity
		self.weight = weight

	def __eq__(self, other):
		return self.startEntity == other.startEntity and self.endEntity == other.endEntity

	def __repr__(self):
		return "Start Entity: " + str(self.startEntity) + "\n" + "End Entity: " + str(self.endEntity)

	def __str__(self):
		return self.__repr__()
