from HIN import EntityInfo
from Similarity import *
import pickle, random

f = open('HIN.pkl','rb')
HIN = pickle.load(f)
f.close()

hinEntities = HIN['Entities']
# User - Movie - Actor - Movie - User
userEntityId1, userEntityId2 = random.sample(list(HIN['EntityTypes']['user'].keys()), 2)

userEntityInfoIndex1 = HIN['EntityTypes']['user'][userEntityId1]
userEntityInfoIndex2 = HIN['EntityTypes']['user'][userEntityId2]

userEntity1 = HIN['Entities'][userEntityInfoIndex1].entity
userEntity2 = HIN['Entities'][userEntityInfoIndex2].entity

print(userEntity1)
print(userEntity2)

metaPath = ['user','movie','user']
print(getWsRel(HIN, userEntity1, userEntity2, metaPath))
print(getSignSim(HIN, userEntity1, userEntity2, metaPath))
print(getPathSim(HIN, userEntity1, userEntity2, metaPath))
print(getTeteSim(HIN, userEntity1, userEntity2, metaPath))
print(getDistantSim(HIN, userEntity1, userEntity2, metaPath))
print(getJoinSim(HIN, userEntity1, userEntity2, metaPath))
