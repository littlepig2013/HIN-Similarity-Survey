from Relation import Relation
from Entity import Entity

import numpy as np
import pickle

DATASET_DIR = "dataset/"
USER_RATE_FILENAME = "users_rate.txt"
MOVIE_GENRE_FILENAME = "movie_genres.txt"
MOVIE_DIRECTOR_FILENAME = "movie_directors.txt"
MOVIE_ACTOR_FILENAME = "movie_actors.txt"
HIN_FILENAME = "HIN.pkl"

class EntityInfo:

	def __init__(self, entity):
		self.entity = entity
		self.inRelations = dict()
		self.outRelations = dict()

	# inRelationFlag = True -> add inRelations
	# inRelationFlag = False -> add outRelations
	def addRelation(self, relation, relationIndex, inRelationFlag):
		tmpEntityType = None
		tmpRelations = None
		# Select a relation list and an entity type	
		if inRelationFlag:
			if hasattr(relation, 'endEntity') and relation.endEntity == self.entity:
				tmpEntityType = relation.startEntity.entityType
				tmpRelations = self.inRelations
		else:
			if hasattr(relation, 'startEntity') and relation.startEntity == self.entity:
				tmpEntityType = relation.endEntity.entityType
				tmpRelations = self.outRelations

		if tmpRelations != None and tmpEntityType != None:
			# Add the relation in specified list
			if tmpEntityType in tmpRelations:
				tmpRelations[tmpEntityType].append(relationIndex)
			else:
				tmpRelations[tmpEntityType] = [relationIndex]




# If the entity does not exsit, the function will add the entity in the hin
def locateEntity(hin, entityId, entityType):
	hinEntityType = hin['EntityTypes'][entityType]
	hinEntityList = hin['Entities']

	if entityId not in hinEntityType:
		# The entity is not in the HIN
		hinEntityList.append(EntityInfo(Entity(entityId, entityType)))
		hinEntityType[entityId] = len(hinEntityList) - 1

	hinEntityIndex = hinEntityType[entityId]
	return hinEntityList[hinEntityIndex], hinEntityIndex



def loadRelationFile(hin, relationFileName, startEntityType, endEntityType):
	# Judge whether the entity type exists in the HIN
	if startEntityType not in hin['EntityTypes']:
		hin['EntityTypes'][startEntityType] = dict()
	if endEntityType not in hin['EntityTypes']:
		hin['EntityTypes'][endEntityType] = dict()

	# Initialize relations list
	startTypeToEndType = startEntityType + '-' + endEntityType
	endTypeToStartType = endEntityType + '-' + startEntityType
	hin['RelationTypes'][startTypeToEndType] = []
	hin['RelationTypes'][endTypeToStartType] = []
	hinStartToEndList = hin['RelationTypes'][startTypeToEndType]
	hinEndToStartList = hin['RelationTypes'][endTypeToStartType]

	hinRelationList = hin['Relations']

	# Start reading data file
	with open(DATASET_DIR + relationFileName, 'r') as relationFile:

		while True:
			relationLine = relationFile.readline()
			if not relationLine:
				break

			relationLine = relationLine.strip()
			relation = relationLine.split(' ')

			# Data sensitive -> type ... 
			# Load the start entity and the end entity
			startEntityId = int(relation[0])
			endEntityId = relation[1]
			if endEntityId.isdigit():
				endEntityId = int(endEntityId)
			weight = None

			# The third column is regarded as the weight
			if len(relation) > 2:
				weightStr = relation[2]
				# Judge whether the type of the weight should be float or int
				if '.' in weightStr:
					weight = float(weightStr)
				else:
					weight = int(weightStr)

			# Entity location
			tmpStartEntityInfo, tmpStartEntityIndex = locateEntity(hin, startEntityId, startEntityType)
			tmpEndEntityInfo, tmpEndEntityIndex = locateEntity(hin, endEntityId, endEntityType)
			tmpStartEntity = tmpStartEntityInfo.entity
			tmpEndEntity = tmpEndEntityInfo.entity

			# Construct a relation and its reverse one
			tmpRelation = Relation(tmpStartEntity, tmpEndEntity, weight)
			hinRelationList.append(tmpRelation)
			tmpRelationIndex = len(hinRelationList) - 1
			tmpReverseRelation = Relation(tmpEndEntity, tmpStartEntity)
			hinRelationList.append(tmpReverseRelation)
			tmpReverseRelationIndex = len(hinRelationList) - 1

			# Add the relations in entity and HIN
			tmpStartEntityInfo.addRelation(tmpRelation, tmpRelationIndex, False)
			tmpEndEntityInfo.addRelation(tmpRelation, tmpRelationIndex, True)
			hinStartToEndList.append(tmpRelationIndex)

			tmpStartEntityInfo.addRelation(tmpReverseRelation, tmpReverseRelationIndex, True)
			tmpEndEntityInfo.addRelation(tmpReverseRelation, tmpReverseRelationIndex, False)
			hinEndToStartList.append(tmpReverseRelationIndex)

		relationFile.close()


def main():
	# hin initialize
	hin = dict()
	hin['Entities'] = []
	hin['Relations'] = []
	hin['EntityTypes'] = dict()
	hin['RelationTypes'] = dict()
	

	# Start load data
	loadRelationFile(hin, USER_RATE_FILENAME, 'user', 'movie')
	loadRelationFile(hin, MOVIE_GENRE_FILENAME, 'movie', 'genre')
	loadRelationFile(hin, MOVIE_DIRECTOR_FILENAME, 'movie', 'director')
	loadRelationFile(hin, MOVIE_ACTOR_FILENAME, 'movie', 'actor')

	# Store HIN in a specified file
	with open(HIN_FILENAME, 'wb') as hinFile:
		pickle.dump(hin, hinFile)


if __name__ == '__main__':
	main()