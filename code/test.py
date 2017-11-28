from HIN import EntityInfo
from Similarity import *
import pickle, random, math

# loading remaining user rating record to evaluae the similarity method
def loadRatingGroundTruth(currentUserId, movieSampleNum):

    fin = open('dataset/users_rate_test.txt','r')
    userRecords = fin.readlines()
    fin.close()

    sampledMovies = set()
    currUserGroundTruth = []
    for userRecord in userRecords:
        [userStr, movieStr, ratingStr] = userRecord.split(" ")
        userId = int(userStr)
        movieId = int(movieStr)
        if userId == currentUserId:
            sampledMovies.add(movieId)
            currUserGroundTruth.append((float(ratingStr), movieId))

    if len(sampledMovies) > movieSampleNum:
        sampledMovies = set(random.sample(sampledMovies, movieSampleNum))

    currUserFinalGroundTruth = []
    for rating, movieId in currUserGroundTruth:
        if movieId in sampledMovies:
            currUserFinalGroundTruth.append((rating, movieId))

    currUserFinalGroundTruth.sort(reverse=True)

    return sampledMovies, currUserFinalGroundTruth


def getMovieRank(hin, userEntityInfo, sampledMovies, metaPath, simFunc):
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
    for movieId in sampledMovies:
        movieEntity = hin['Entities'][movieEntityInfoIndexes[movieId]].entity
        if movieEntity.entityId not in ratedMovieId:
            sim = simFunc(hin, userEntity, movieEntity, metaPath)
            movieRank.append((sim, movieId))
    movieRank.sort(reverse=True)
    return movieRank


def getMetrics(groundTruth, predictResult, k):
    if k > len(groundTruth):
        k = len(groundTruth)

    movieIdSample1 = set([movieId for _, movieId in groundTruth])
    movieIdSample2 = set([movieId for _, movieId in predictResult])
    # process ground truth first
    groundTruthDict = dict()
    sigMoidRatingSum = 0
    for rating, movieId in groundTruth:
        sigmoidRating = 1/(1 + math.exp(-rating))
        sigMoidRatingSum += sigmoidRating
        groundTruthDict[movieId] = sigmoidRating
    # normalization
    for movieId in groundTruthDict:
        groundTruthDict[movieId] /= sigMoidRatingSum

    groundTruthTopK = groundTruth[:k]
    groundTruthTopKSet = set()
    for _, movieId in groundTruthTopK:
        groundTruthTopKSet.add(movieId)
    predictResultTopK = predictResult[:k]

    # calculate the precision
    hitCount = 0
    for sim, movieId in predictResultTopK:
        if movieId in groundTruthTopKSet:
            hitCount += 1
    precision = hitCount/k

    # calculate the MAP
    MAP = 1
    for _, movieId in  predictResultTopK:
        MAP *= groundTruthDict[movieId]

    return precision, -math.log(MAP)


def main():
    f = open('HIN.pkl','rb')
    HIN = pickle.load(f)
    f.close()

    K = 10
    userSampleNum = 100
    movieSampleNum = 50

    print('k ', K, 'user ', userSampleNum, 'movie', movieSampleNum)
    # Meta path
    metaPath = ['user','movie','actor','movie']

    hinEntities = HIN['Entities']
    userEntityIdDict = HIN['EntityTypes']['user']
    movieEntityIdDict = HIN['EntityTypes']['movie']
    # generate sampled users
    sampledUserEntityIdList = random.sample(list(userEntityIdDict.keys()), userSampleNum)
    sampledUserEntityInfoList = [hinEntities[userEntityIdDict[userEntityId]] for userEntityId in sampledUserEntityIdList]

    simFuncList = [getWsRel, getSignSim, getPathSim, getHeteSim]
    simFuncNameList = ['WsRel', 'SignSim', 'PathSim', 'HeteSim', ]
    for i in range(4):
        finalPrecision = finalMAP = 0
        for userId in sampledUserEntityIdList:
            userEntityInfo = HIN['Entities'][HIN['EntityTypes']['user'][userId]]
            # generate the sampled movies and get the ground truth result
            sampledMovies, rateGroundTruth = loadRatingGroundTruth(userId, movieSampleNum)
            movieRank = getMovieRank(HIN, userEntityInfo, sampledMovies, metaPath, simFuncList[i])
            precision, MAP = getMetrics(rateGroundTruth, movieRank, K)
            finalPrecision += precision
            finalMAP += MAP
        finalPrecision /= userSampleNum
        finalMAP /= userSampleNum*math.factorial(K)
        print()
        print(simFuncNameList[i] + " Result:")
        print("Precision -> %.4f; -log(MAP) -> %.10f" % (finalPrecision, finalMAP))


if __name__ == '__main__':
    main()
