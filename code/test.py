from HIN import EntityInfo
from Similarity import *
import pickle, random

# loading remaining user rating record to evaluae the similarity method
def loadRatingGroundTruth():
    rateGroundTruth = dict()
    fin = open('dataset/users_rate_test.txt','r')
    userRecords = fin.readlines()
    fin.close()
    for userRecord in userRecords:
        [userStr, movieStr, ratingStr] = userRecord.split(" ")
        userId = int(userStr)
        if userId not in rateGroundTruth:
            rateGroundTruth[userId] = [(float(ratingStr), int(movieStr))]
        else:
            rateGroundTruth[userId].append((float(ratingStr), int(movieStr)))

    for userId in rateGroundTruth:
        rateGroundTruth[userId].sort(reverse=True)

    return rateGroundTruth


def getMovieRanking(hin, userEntityInfo, metaPath, simFunc):
    '''
	calculate the movie rank list
	:param HIN: the heterogeneous information network
	:param userEntity: the user entityInfo
	:param metaPath: meta-path
    :simFunc: the similarity function
	:return: weighted signed relation between eEntity and tEntity
	'''

    # filter those unrated movie in this entity
    userEntity = userEntityInfo.entity
    ratedMovieId = set()
    if 'movie' in userEntityInfo.outRelations:
        ratedMovieId.update(set(userEntityInfo.outRelations['movie'].keys()))

    # get the similarity value and rank them
    movieRank = []
    movieEntityInfoIndexes = hin['EntityTypes']['movie']
    print(len(movieEntityInfoIndexes))
    for movieId in movieEntityInfoIndexes:
        movieEntity = hin['Entities'][movieEntityInfoIndexes[movieId]].entity
        if movieEntity.entityId not in ratedMovieId:
            movieRank.append((simFunc(hin, userEntity, movieEntity, metaPath), movieId))
    movieRank.sort(reverse=True)
    return movieRank

def getMetrics(groundTruth, predictResult, k):
    # process ground truth first
    groundTruthDict = dict()
    ratingSum = 0
    for rating, movieId in groundTruth:
        ratingSum += rating
        groundTruthDict[movieId] = rating
    # normalization
    for movieId in groundTruthDict:
        groundTruthDict[movieId] /= ratingSum


    groundTruthTopK = groundTruth[:k]
    groundTruthTopKSet = set()
    for movieId in groundTruthTopK:
        groundTruthTopKSet.add(movieId)
    predictResultTopK = predictResult[:k]

    # calculate the precision
    hitCount = 0
    for sim, movieId in predictRank:
        if movieId in groundTruthTopKSet:
            hitCount += 1
    precision = hitCount/k

    # calculate the MAP
    MAP = 1
    for _, movieId in predictRank:
        MAP *= 10*groundTruthDict[movieId]

    return precision, MAP



def main():
    f = open('HIN.pkl','rb')
    HIN = pickle.load(f)
    f.close()

    K = 10
    userSample = 5
    movieCandidates = 1000

    # Meta path
    metaPath = ['user','movie','user','movie']

    hinEntities = HIN['Entities']
    userEntityIdDict = HIN['EntityTypes']['user']
    movieEntityIdDict = HIN['EntityTypes']['movie']
    # generate sampled users
    sampledUserEntityIdList = random.sample(list(userEntityIdDict.keys()), userSample)
    sampledUserEntityInfoList = [hinEntities[userEntityIdDict[userEntityId]] for userEntityId in sampledUserEntityIdList]
    # generate movie candidates
    ratedMoviesSet = set()
    for userEntityInfo in sampledUserEntityInfoList:
        if "movie" in userEntityInfo.outRelations:
            ratedMoviesSet.update(set(userEntityInfo.outRelations['movies'].keys()))
    movieCandidates = set(movieEntityIdDict.keys()) - ratedMoviesSet

    rateGroundTruth = loadRatingGroundTruth()

if __name__ == '__main__':
    main()
