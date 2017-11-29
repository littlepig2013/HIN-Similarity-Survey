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
				* relIndexDict:
					* Type: dict
					* keys: the start entity id
					* Values: the indexes of these correponding relations in HIN['Relations']
				* relsNum:
					* Type: int
					* the number of relations under this relation type
		* outRelations:
			* Type: dict
			* keys: the end entity type
			* Values: (similar to the inRelations values)
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

## To Run the Code

* Dataset source is refered in the report.
* `python3 split.py` is used to produce the train and test data based on the dataset.
* `python3 HIN.py` is used to load the graph and store the graph into pickle file for further use.
* `python3 test.py` is used to re-produde the results shown in our report.


