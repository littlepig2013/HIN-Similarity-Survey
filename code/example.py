from HIN import EntityInfo

import pickle

f = open('HIN.pkl','rb')
HIN = pickle.load(f)

print(HIN.keys())

f.close()
