from HIN import EntityInfo
from Similarity import *
import pickle, random, math, time

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
    timeCost = 0
    simCalCount = 0
    movieEntityInfoIndexes = hin['EntityTypes']['movie']
    for movieId in sampledMovies:
        movieEntity = hin['Entities'][movieEntityInfoIndexes[movieId]].entity
        if movieEntity.entityId not in ratedMovieId:
            startTime = time.time()
            sim = simFunc(hin, userEntity, movieEntity, metaPath)
            endTime = time.time()
            timeCost += endTime - startTime
            simCalCount += 1
            movieRank.append((sim, movieId))
    movieRank.sort(reverse=True)

    if simCalCount == 0:
        timeCost = None
    else:
        timeCost /= simCalCount

    return movieRank, timeCost


def getMetrics(groundTruth, predictResult, k):
    if k > len(groundTruth):
        k = len(groundTruth)
        print("Not enough candidate movies")
        print("current candidate num:" + str(k))

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

    return precision


def main():
    f = open('HIN.pkl','rb')
    HIN = pickle.load(f)
    f.close()

    K = 10
    userSampleNum = 10
    movieSampleNum = 50

    print('k ', K, 'user ', userSampleNum, 'movie', movieSampleNum)
    # Meta path
    metaPath = ['user','movie','genre','movie']

    hinEntities = HIN['Entities']
    userEntityIdDict = HIN['EntityTypes']['user']
    movieEntityIdDict = HIN['EntityTypes']['movie']
    # generate sampled users
    sampledUserEntityIdList = random.sample(list(userEntityIdDict.keys()), userSampleNum)
    sampledUserEntityInfoList = [hinEntities[userEntityIdDict[userEntityId]] for userEntityId in sampledUserEntityIdList]

    simFuncList = [getWsRel, getSignSim, getPathSim, getHeteSim]
    simFuncNameList = ['WsRel', 'SignSim', 'PathSim', 'HeteSim', ]
    for i in range(4):
        finalPrecision = avgTimeCost = 0
        for userId in sampledUserEntityIdList:
            userEntityInfo = HIN['Entities'][HIN['EntityTypes']['user'][userId]]
            # generate the sampled movies and get the ground truth result
            sampledMovies, rateGroundTruth = loadRatingGroundTruth(userId, movieSampleNum)
            movieRank, timeCost = getMovieRank(HIN, userEntityInfo, sampledMovies, metaPath, simFuncList[i])
            if movieRank == [] and timeCost == None:
                userSampleNum -= 1
                continue
            precision = getMetrics(rateGroundTruth, movieRank, K)
            finalPrecision += precision
            avgTimeCost += timeCost
        if userSampleNum != 0:
            finalPrecision /= userSampleNum
            avgTimeCost /= userSampleNum
            print()
            print(simFuncNameList[i] + " Result:")
            print("Precision -> %.4f; cost time -> %.10f" % (finalPrecision, avgTimeCost))
        else:
            print("Failed to select candidate movies to perform the evaluation.")


if __name__ == '__main__':
    main()
