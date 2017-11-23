# HIN-Similarity-Survey

> By Zichen Zhu & Chenhao Ma
## Data Structure
### Basic Classes:
* Entity:
	* Variables:
		* entityType -> entity type
		* entityId -> entity id in this type
* Relation:
	* Variables:
		* startEntity -> the start entity
		* endEntity -> the end entity
		* weight(default:None) -> the weight of this relation object 
* Entity Info:
	* Variables:
		* entity -> its correponding entity in HIN
		* inRelations:
			* Type: dict
			* keys: the start entity type
			* Values: 
				* Type: list
				* Values: the indexes of these correponding relations in HIN['Relations']
		* outRelations:
			* Type: dict
			* keys: the end entity type
			* Values:
				* Type: list
				* Values: the indexes of these correponding relations in HIN['Relations']
	* Methods:
		* addRelation(relation, relationIndex, inRelationFlag):
			* relation: a Relation object
			* relationIndex: its correponding index in HIN['Relations']
			* inRelationFlag:
				*  True -> a incoming relation
				*  False -> a outgoing relation
			* function: update this entity's inRelations or outRelations according to the relation and its index 

### Other Variables: 
* HIN:
	* Type: dict
	* Keys: ['Entities', 'EntityTypes', 'Relations', 'RelationTypes']
* HIN['Entities']:
	* Type: list
	* Values: 
		* Type: Entity Info Class
* HIN['EntityTypes']:
	* Type: dict
	* Keys: all possible entity types
	* Values:
		* Type: dict
		* Keys: entity id of this type
		* Values: the index of an EntityInfo object in HIN['Entities']
* HIN['Relations']:
	* Type: list
	* Values:
		* Type: Relation Class 
* HIN['RelationTypes']:
	* Type: dict
	* Keys: "(entity type1)-(entity type2)"
	* Values:
		* Type: list
		* Values:
			* Type: the index of a relation in HIN['Relations']

