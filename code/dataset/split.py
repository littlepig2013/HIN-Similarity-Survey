import random
fin = open("users_rate.txt",'r')
data = fin.readlines()

userDict = dict()
for record in data:
	[userStr, movieStr, ratingStr] = record.split(' ')
	if userStr not in userDict:
		userDict[userStr] = [(movieStr, ratingStr)]
	else:
		userDict[userStr].append([movieStr, ratingStr])

TRAINING_RATE = 0.5
fout1 = open('users_rate_train.txt','w')
fout2 = open('users_rate_test.txt','w')
for userStr in userDict:
	userRecords = userDict[userStr].copy()
	random.shuffle(userRecords)
	trainingLen = int(TRAINING_RATE*len(userRecords))
	trainUser = userDict[userStr][:trainingLen]
	for movieStr, ratingStr in trainUser:
		fout1.write(userStr + ' ' + movieStr + ' ' + ratingStr)
	testUser = userDict[userStr][trainingLen:]
	for movieStr, ratingStr in testUser:
		fout2.write(userStr + ' ' + movieStr + ' ' + ratingStr)

fin.close()
fout1.close()
fout2.close()
